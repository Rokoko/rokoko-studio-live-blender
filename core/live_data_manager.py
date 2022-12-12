
import bpy
import json

loaded_lz4 = False
unsupported_os = False
try:
    from lz4 import frame

    loaded_lz4 = True
except ModuleNotFoundError:
    print("Error: LZ4 module didn't load. Unsupported OS or Python version!")
except ImportError:
    print("Error: LZ4 module didn't load. Unsupported OS!")
    unsupported_os = True


class LiveDataPacket:

    def __init__(self, data):
        self.data = data
        self.fps = 60
        self.actors: [Actor] = []
        self.props = []

        self._decode_data()
        self._process_data()

        LiveDataState.update_state(self)

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
            raise ImportError("os" if unsupported_os else "")

        if not self.data:
            raise ValueError

    def _process_data(self):
        self.version = self.data.get('version')
        ver_str = str(self.version).replace(".", ",")
        if ',' in ver_str:
            self.version = int(ver_str.split(',')[0])

        if not self.version or self.version < 3:
            raise TypeError

        self.fps = self.data['fps']
        self.props = self.data['scene']['props']

        for actor_data in self.data['scene']['actors']:
            actor = Actor(actor_data)
            self.actors.append(actor)


class Actor:
    def __init__(self, data):
        self.data = data

        self.name = self.data['name']
        self.bones = self.data['body']

        self.has_face = self.data['meta']['hasFace']
        self.has_gloves = self.data['meta']['hasGloves']
        self.has_left_glove = self.data['meta']['hasLeftGlove']
        self.has_right_glove = self.data['meta']['hasRightGlove']

        self.hips_height = self.data['dimensions']['hipHeight']

        self.attribute_name = 'rsl_actor_v2_' + self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def get_paired_armature(self):
        return getattr(bpy.context.scene, self.attribute_name)


class LiveDataState:
    state: LiveDataPacket = None
    actors = []

    @staticmethod
    def update_state(packet):
        from ..properties import register_actor
        LiveDataState.state = packet

        actors = [actor for actor in packet.actors]
        actors_new = [actor for actor in packet.actors if actor not in LiveDataState.actors]

        LiveDataState.actors = actors

        for actor in actors_new:
            register_actor(actor)


class ActorPairs:
    pairs: {Actor: str} = {}

    @staticmethod
    def update_pairs():
        for actor in LiveDataState.actors:
            paired_armature = actor.get_paired_armature()
            if ActorPairs.pairs.get(actor) == paired_armature:
                continue

            # TODO: Trigger armature pairing or removing
            ActorPairs.pairs[actor] = paired_armature
            print("PAIR ARMATURE:", actor.name, paired_armature)
            ActorPairs.pair_armature(paired_armature)

    @staticmethod
    def pair_armature(armature_target_name):
        from ..operators import receiver
        from . import detection_manager

        armature_base = receiver.receiver.animator.armature
        armature_target = bpy.data.objects.get(armature_target_name)
        if not armature_target:
            print("ERROR: Armature not found:", armature_target_name)
            return

        for bone in armature_base.pose.bones:
            # Detect the corresponding bone in the target armature
            bone_target_name = detection_manager.detect_bone(armature_target, bone.name)
            bone_target = armature_target.pose.bones.get(bone_target_name)
            if not bone_target:
                print("ERROR: Bone not found:", bone_target_name, "from", bone.name)
                continue

            if len(bone_target.constraints) > 0:
                print("ERROR: Bone already has constraints:", bone_target_name, "(tried:", bone.name, ")")
                continue

            # Mimic the animation of the base bone to the target bone by adding rotation constraints
            constraint = bone_target.constraints.new('COPY_ROTATION')
            constraint.name = bone.name
            constraint.target = armature_base
            constraint.subtarget = bone.name
            # constraint.owner_space = "CUSTOM"

            # # Mimic the animation of the base bone to the target bone by adding transform constraints
            # constraint = bone_target.constraints.new('COPY_TRANSFORMS')
            # constraint.name = bone.name
            # constraint.target = armature_base
            # constraint.subtarget = bone.name



def update_pair(self, context):
    ActorPairs.update_pairs()


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
            raise ImportError("os" if unsupported_os else "")

        if not self.data:
            raise ValueError

    def _process_data(self):
        self.version = self.data.get('version')
        ver_str = str(self.version).replace(".", ",")
        if ',' in ver_str:
            self.version = int(ver_str.split(',')[0])

        # If the user selected JSON v2.5 in Studio 1, the version number is "3" but it contains the data from version 2
        # This checks if this is the case and sets the version number accordingly
        if self.version == 3 and self.data.get('trackers') is not None:
            self.version = 2

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
