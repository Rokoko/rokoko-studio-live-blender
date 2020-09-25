import json
import platform

if platform.system() == "Windows":
    from ..packages.win.lz4 import frame
elif platform.system() == "Darwin":
    from ..packages.mac.lz4 import frame
elif platform.system() == "Darwin":
    from ..packages.linux.lz4 import frame


class LiveData:
    data = None
    version = 0

    # JSON v2
    timestamp = None
    props = []
    trackers = []
    faces = []
    actors = []

    # JSON v3
    fps = 60

    # def __init__(self, data):
    #     self.data = data
    #     self.decode_data()
    #     self.clear_data()
    #     self.process_data()

    def init(self, data):
        self.data = data
        self._decode_data()
        self.clear_data()
        self._process_data()

    def clear_data(self):
        self.version = 0

        # JSON v2
        self.timestamp = None
        self.props = []
        self.trackers = []
        self.faces = []
        self.actors = []

        # JSON v3
        self.fps = 60

    def _decode_data(self):
        try:
            self.data = frame.decompress(self.data)
        except RuntimeError:
            pass

        self.data = json.loads(self.data)
        if not self.data:
            raise ValueError

    def _process_data(self):
        self.version = self.data.get('version')

        if not self.version or self.version < 2:
            raise TypeError

        if self.version == 2:
            self.timestamp = self.data['timestamp']
            self.props = self.data['props']
            self.trackers = self.data['trackers']
            self.faces = self.data['faces']
            self.actors = self.data['actors']

        else:
            if self.data.get('scene'):
                self.data = self.data['scene']
            elif self.data['live']['actors'] or self.data['live']['props']:
                self.data = self.data['live']
            else:
                self.data = self.data['playback']

            self.timestamp = self.data['timestamp']
            self.actors = self.data['actors']
            self.props = self.data['props']

            for actor in self.actors:
                if actor['meta']["hasFace"]:
                    actor['face']['parentName'] = actor['name']
                    self.faces.append(actor['face'])

    def has_gloves(self, actor):
        # TODO Remove v2 support for this
        return self.version <= 2 or (self.version >= 3 and actor.get('meta') and actor.get('meta').get('hasGloves'))

    def supports_trackers(self):
        return self.version <= 2

    # Get data for and from the live data selection lists

    def get_actor_by_obj(self, obj):
        actors = [actor for actor in self.actors if actor['name'] == obj.rsl_animations_actors]
        return actors[0] if actors else None

    def get_actor_id(self, actor):
        return actor['name']

    def get_face_by_obj(self, obj):
        face_id = 'faceId' if self.version <= 2 else 'parentName'
        faces = [face for face in self.faces if face[face_id] == obj.rsl_animations_faces]
        return faces[0] if faces else None

    def get_face_id(self, face):
        face_id = 'faceId' if self.version <= 2 else 'parentName'
        return face[face_id]

    def get_prop_by_obj(self, obj):
        if self.version <= 2:
            obj_id = obj.rsl_animations_props_trackers.split('|')
            obj_type = obj_id[0]
            obj_name = obj_id[1]

            if obj_type == 'PR':
                props = [prop for prop in self.props if prop['name'] == obj_name]
            else:
                props = [tracker for tracker in self.trackers if tracker['name'] == obj_name]

            return props[0] if props else None

        props = [prop for prop in self.props if prop['name'] == obj.rsl_animations_props_trackers]
        return props[0] if props else None

    def get_prop_id(self, prop, is_tracker=False):
        if self.version <= 2:
            return ('TR' if is_tracker else 'PR') + '|' + prop['name']
        return prop['name']

    def get_prop_name(self, prop, is_tracker=False):
        if self.version <= 2:
            return ('Tracker: ' if is_tracker else 'Prop: ') + prop['name']
        return prop['name']






