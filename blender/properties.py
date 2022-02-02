from bpy.props import PointerProperty, StringProperty, BoolProperty
from bpy.types import PropertyGroup, Scene
from bpy.utils import register_class, unregister_class

class DataTransfer_Properties(PropertyGroup):
    outCameraPath: StringProperty(
        name="Output",
        description="Export Output path",
        default="",
        maxlen=1024,
        subtype="FILE_PATH"
        )

    inCameraAbc: StringProperty(
        name="Alembic",
        description="camera.abc path",
        default="",
        maxlen=1024,
        subtype="FILE_PATH"
        )

    inCameraJson: StringProperty(
        name="Json",
        description="camera.json path",
        default="",
        maxlen=1024,
        subtype="FILE_PATH"
        )
        
    deleteExisting: BoolProperty(
        name="Remove Existing camera cache",
        description="Remove existing camera cache that have same filename",
        default=True
        )

    setFrameRange: BoolProperty(
        name="Set Frame Range",
        description="Set scene frame range to imported alembic",
        default=True
        )

def register():
    register_class(DataTransfer_Properties)
    Scene.data_transfer_prop = PointerProperty(type=DataTransfer_Properties)

def unregister():
    unregister_class(DataTransfer_Properties)
    del Scene.data_transfer_prop