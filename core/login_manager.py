import os
import bpy
import ssl
import json
import boto3
import pathlib
import asyncio
import logging
import datetime
import requests
import traceback
import webbrowser

from .. import updater
from .utils import ui_refresh_all, cancel_gen

from gql import Client, gql
from threading import Thread, Timer
from contextlib import suppress
from typing import AsyncGenerator
from urllib.parse import urlparse
from cryptography.fernet import Fernet
from gql.transport.appsync_websockets import AppSyncWebsocketsTransport
from gql.transport.appsync_auth import AppSyncApiKeyAuthentication
from gql.transport.websockets import log as websockets_logger

# Set logging levels
websockets_logger.setLevel(logging.CRITICAL)
logging.getLogger('boto').setLevel(logging.CRITICAL)

# Disable SSL
ssl._create_default_https_context = ssl._create_unverified_context


class Login:
    url = "https://rmp-gql-public.rokoko.ninja/graphql"
    aws_url = "wss://z55v4xbwa5cfplrbnupw7bgn2u.appsync-realtime-api.us-east-1.amazonaws.com/graphql"
    api_key = "da2-o3nnjsj67rhvbfhmvf6zkrsvxq"
    timeout_duration = 60  # In seconds, how long the listener is waiting for the login event after opening the browser

    def __init__(self):
        self.request_id = None
        self.session: Client
        self.results: AsyncGenerator
        self.timeout: Timer

    def start(self):
        user.logging_in = True
        user.display_error = None

        # Start the listener in a new thread so Blender can continue running
        listener = Thread(target=self._start_async, args=[])
        listener.start()

        # Start the timeout thread which stops the listener after a few seconds if nothing happened
        self.timeout = Timer(self.timeout_duration, self._timeout)
        self.timeout.start()

    def stop(self):
        pass

    def _start_async(self):
        try:
            # Get the request id from the server and run the listener
            self._get_request_id()
            asyncio.run(self._run_listener())
        except Exception as e:
            print(traceback.format_exc())
            user.error("No internet connection..")

    def _timeout(self):
        # If the user no longer logging in, don't timeout
        if not user.logging_in:
            return

        # Stop the login listener
        print("Connection timeout, stopping listener..")
        asyncio.run(cancel_gen(self.results))

        # Stopping login and updating UI to show timeout error
        user.error("Timeout, please try again.")
        print("Stopped login listener")

    def _get_request_id(self):
        headers = {"x-api-key": self.api_key}
        query = """
            mutation {
              createRequestToken(client_id: "blender") {
                request_id
                access_token
                id_token
                refresh_token
                client_id
                created_at
                last_modified
                email
                username
                given_name
                family_name
                ttl
              }
            }
        """

        try:
            request = requests.post(self.url, json={'query': query}, headers=headers)
        except Exception as e:
            user.logging_in = False
            raise Exception("No connection to the server.")

        if request.status_code != 200:
            user.logging_in = False
            raise Exception(f"Query failed to reach the server by returning code of {request.status_code}.")

        data = request.json()
        self.request_id = data.get("data").get("createRequestToken").get("request_id")

    def _open_website(self):
        webbrowser.open("https://dev-id.rokoko.com/?request_id=" + self.request_id)   # TODO: Change away from dev-id

    async def _run_listener(self):
        # Extract host from aws_url and create auth
        host = str(urlparse(self.aws_url).netloc)
        auth = AppSyncApiKeyAuthentication(host=host, api_key=self.api_key)

        transport = AppSyncWebsocketsTransport(url=self.aws_url, auth=auth, ssl=ssl._create_unverified_context())

        async with Client(transport=transport) as session:
            self.session = session
            subscription = gql(
                f"""
                subscription {{
                  onTokenChange(request_id: "{self.request_id}") {{
                    request_id
                    access_token
                    id_token
                    refresh_token
                    client_id
                    created_at
                    last_modified
                    email
                    username
                    given_name
                    family_name
                    ttl
                  }}
                }}
                """
            )
            print("Waiting for login event..")

            # Subscribe to the login event
            self.results = session.subscribe(subscription)

            # Open the website to allow the user to login
            self._open_website()

            with suppress(asyncio.CancelledError):

                # Wait for the login event
                async for result in self.results:
                    # Check if the correct data was returned
                    data = result.get("onTokenChange")
                    if data:
                        if data.get("request_id") != self.request_id:
                            user.error("Error, please try again.")
                            print("Request ID not correct, please try again.")
                            break
                        print("Login successful, stopping listener..")
                        user.login(data)
                        user.login_cache.create_login_cache(data)
                        break

                    # If another event was returned (like maintenance), stop the login
                    user.error("Server error, please try again.")
                    print("Server error:", result)
                    break

                # If the connection is closing by itself, cancel the timeout timer
                self.timeout.cancel()


class LoginSilent:
    region = 'us-east-1'
    client_id = "5p8idgrqi7lvq09di4rknhf2bp"

    def __init__(self):
        logging.getLogger('boto').setLevel(logging.ERROR)
        self.login()

    def login(self):
        # Start the listener in a new thread so Blender can continue running
        thread = Thread(target=self._login_async, args=[])
        thread.start()

    def _login_async(self):
        print("SILENT LOGIN")
        if not user.refresh_token:
            return

        response = None

        try:
            client = boto3.client("cognito-idp", region_name=self.region)
            response = client.initiate_auth(
                AuthFlow='REFRESH_TOKEN',
                AuthParameters={
                    'REFRESH_TOKEN': user.refresh_token
                },
                ClientId=self.client_id
            )
        except Exception as e:
            error_msg = str(e)
            print("\nERROR:", error_msg, "\n")
            if "NotAuthorizedException" in error_msg:
                user.logout()
                user.error("Logged out: Invalid user")

        # print("RESPONSE:", response)
        if not response:
            return

        # Check response for challenge, logout if challenge detected
        # See here for challenges:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.initiate_auth
        challenge_name = response.get("ChallengeName")
        challenge_params = response.get("ChallengeParameters")

        if challenge_name or challenge_params:
            print("ERROR: Further account managing needed!")
            user.logout()
            user.error("Logged out:", challenge_name)


class User:
    classes = []
    classes_login = []

    def __init__(self):
        self.logging_in = False
        self.login_cache = LoginCache()

        self.logged_in = False
        self.email = None
        self.username = None  # This is a unique id
        self.access_token = None
        self.refresh_token = None

        self.display_email = False
        self.display_error = None

        self.login_time = None

    def login(self, data, register_classes=True):
        self.email = data.get("email")
        self.username = data.get("username")
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")

        self.logging_in = False
        self.logged_in = self.email and self.username and self.refresh_token and self.access_token
        if not self.logged_in:
            print("ERROR: Not all fields are filled:", self.email, self.username, self.refresh_token, self.access_token)
            self.error("Login failed, please try again")
            return

        self.display_error = None
        self.login_time = datetime.datetime.utcnow().timestamp()

        MixPanel.send_login_event()

        if register_classes:
            self.register_classes()

    def logout(self):
        if not self.logged_in:
            return

        MixPanel.send_logout_event()

        self.logged_in = False
        self.email = self.username = self.refresh_token = self.access_token = None

        self.unregister_classes()
        self.login_cache.delete_cache()

    def quit(self):
        MixPanel.send_logout_event()

    def auto_login(self, classes, classes_login):
        self.classes = classes
        self.classes_login = classes_login

        # Check the login cache
        data = self.login_cache.get_login_cache()
        if not data:
            return False

        self.login(data, register_classes=False)

        if self.logged_in:
            LoginSilent()

        return self.logged_in

    def error(self, *msg):
        # Update the UI if the user is still logging in or of the error message changes
        update_ui = self.logging_in or msg != self.display_error

        self.logging_in = False
        self.display_error = msg

        if update_ui and not self.logged_in:
            ui_refresh_all()

    def register_classes(self):
        # Unregister login classes
        for cls in reversed(self.classes_login):
            bpy.utils.unregister_class(cls)

        # Register normal classes
        for cls in self.classes:
            bpy.utils.register_class(cls)

    def unregister_classes(self):
        # Unregister normal classes
        for cls in reversed(self.classes):
            bpy.utils.unregister_class(cls)

        # Register login classes
        for cls in self.classes_login:
            bpy.utils.register_class(cls)


class LoginCache:
    main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
    resources_dir = os.path.join(main_dir, "resources")
    cache_dir = os.path.join(resources_dir, "cache")
    cache_file = os.path.join(cache_dir, ".cache")
    key = 'p03Ab7CuvhUuwcbOU4nBAl_QkoaU8XxciKvHGb5Wfd0='

    def __init__(self):
        self.f = Fernet(self.key)

    def create_login_cache(self, data):
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)

        data_str = json.dumps(data)
        encoded_data = data_str.encode()
        encrypted_data = self.f.encrypt(encoded_data)

        with open(self.cache_file, 'wb') as file:
            file.write(encrypted_data)

    def get_login_cache(self):
        if not os.path.isfile(self.cache_file):
            return None

        with open(self.cache_file, 'rb') as file:
            encrypted_data = file.read()

        encoded_data = self.f.decrypt(encrypted_data)
        data_str = encoded_data.decode()
        data = json.loads(data_str)

        if not self.is_valid(data):
            return None

        return data

    def delete_cache(self):
        if os.path.isfile(self.cache_file):
            os.remove(self.cache_file)

    def is_valid(self, data):
        if not data:
            return False

        # Check if the cache is too old
        creation_date = data.get("created_at")
        if not creation_date:
            return False

        duration_timestamp = int(datetime.datetime.now().timestamp()) - creation_date
        duration = datetime.timedelta(seconds=duration_timestamp)

        if duration.days > 90:
            print("Cache too old, please login again")
            self.delete_cache()
            user.error("Login expired (90 days)")
            return False

        return True


class MixPanel:
    url = "https://rmp-team-gql.rokoko.ninja/graphql"

    @staticmethod
    def _send_mixpanel_event(event_name, event_properties, send_async=True):
        if send_async:
            thread = Thread(target=MixPanel._send_event, args=[event_name, event_properties])
            thread.start()
            return

        MixPanel._send_event(event_name, event_properties)

    @staticmethod
    def _send_event(event_name, event_properties):
        # Convert dict to json and quotes to escaped quotes, because the API requires it
        event_properties = json.dumps(event_properties).replace("\"", "\\\"")

        headers = {"Authorization": user.access_token}
        query = f"""
            mutation {{
              addMixPanelEventTracking(
                input: {{
                  event_name: "{event_name}",
                  event_properties: "{event_properties}",
                  client_id: BLENDER
                }}
              )
            }}
        """
        # print("SEND MIXPANEL:", query)
        try:
            request = requests.post(MixPanel.url, json={'query': query}, headers=headers)
        except Exception as e:
            # print("ERROR:", e)
            return

        if request.status_code != 200:
            # print(f"Team API query failed to reach the server by returning code of {request.status_code}.")
            return

        # data = request.json()
        # print(event_name, data)

    @staticmethod
    def send_login_event():
        event_name = "session_start"
        event_properties = {
            "action": "login",
            "blender_version": ".".join(map(str, bpy.app.version)),
            "plugin_version": updater.current_version_str,
        }
        MixPanel._send_mixpanel_event(event_name, event_properties)

    @staticmethod
    def send_logout_event():
        session_duration = 0
        if user.login_time:
            session_duration = datetime.datetime.utcnow().timestamp() - user.login_time
            session_duration = round(session_duration, 2)

        event_name = "session_end"
        event_properties = {
            "action": "logout",
            "blender_version": ".".join(map(str, bpy.app.version)),
            "plugin_version": updater.current_version_str,
            "session_duration": session_duration
        }
        MixPanel._send_mixpanel_event(event_name, event_properties)
        # print("SESSION DURATION:", session_duration, datetime.timedelta(seconds=session_duration))


user: User = User()
