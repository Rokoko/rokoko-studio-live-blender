import json

loaded_lz4 = False
try:
    from lz4 import frame
    loaded_lz4 = True
except ModuleNotFoundError:
    print("Error: LZ4 module didn't load. Unsupported Python version!")


class LiveData:
    data = None
    version = 0

    # JSON v2
    timestamp = 0
    props = []
    trackers = []
    faces = []
    actors = []

    # JSON v3
    fps = 60
    timestamp_prev = 0
    timedelta_prev = 0

    def init(self, data):
        self.data = data
        self._decode_data()
        self.clear_data()
        self._process_data()

    def clear_data(self):
        self.version = 0

        # JSON v2
        # self.timestamp = 0
        self.props = []
        self.trackers = []
        self.faces = []
        self.actors = []

        # JSON v3
        self.fps = 60
        # self.timestamp_prev = 0
        # self.timedelta_prev = 0

    def _decode_data(self):
        try:
            self.data = frame.decompress(self.data)
        except (RuntimeError, NameError):
            pass

        try:
            self.data = json.loads(self.data)
        except UnicodeDecodeError:
            if loaded_lz4:
                raise UnicodeDecodeError
            raise ImportError

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
            self.fps = self.data['fps']

            self.actors = self.data['scene']['actors']
            self.props = self.data['scene']['props']

            for actor in self.actors:
                if actor['meta']["hasFace"]:
                    actor['face']['parentName'] = actor['name']
                    self.faces.append(actor['face'])

            self._calc_timestamp()

    def _calc_timestamp(self):
        timestamp_new = self.data['scene']['timestamp']
        delta = timestamp_new - self.timestamp_prev

        if delta >= 0:
            self.timestamp += delta
            self.timestamp_prev = timestamp_new
            self.timedelta_prev = delta
        else:
            self.timestamp += self.timedelta_prev
            self.timestamp_prev = timestamp_new

    def has_gloves(self, actor):
        return self.version >= 3 and actor.get('meta') and actor.get('meta').get('hasGloves')

    def supports_trackers(self):
        return self.version <= 2

    # Get data for and from the live data selection lists

    def get_actor_by_obj(self, obj):
        actors = [actor for actor in self.actors if actor['name'] == obj.rsl_animations_actors]
        return actors[0] if actors else None

    def get_actor_id(self, actor):
        return actor['name']

    def get_face_by_obj(self, obj):
        face_id = 'faceId'  # if self.version <= 2 else 'parentName'
        faces = [face for face in self.faces if face[face_id] == obj.rsl_animations_faces]
        return faces[0] if faces else None

    def get_face_id(self, face):
        face_id = 'faceId'  # if self.version <= 2 else 'parentName'
        return face[face_id]

    def get_face_parent_id(self, face):
        face_id = 'profileName' if self.version <= 2 else 'parentName'
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

    def get_prop_name_raw(self, prop, is_tracker=False):
        return prop['name']






