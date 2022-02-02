from bpy.types import Panel
from bpy.utils import register_class, unregister_class

class Transfer_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Data Transfer"

class Exporter_PT_CameraPanel(Transfer_PT_Panel):
    bl_label = "Camera Export"
    bl_idname = "Exporter_PT_CameraPanel"
    
    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        scene = context.scene
        data_transfer_prop = scene.data_transfer_prop
        layout = self.layout
        layout.prop(data_transfer_prop, "outCameraPath")
        layout.operator('exporter.exportcamera', text="Export Scene Camera")

class Importer_PT_CameraPanel(Transfer_PT_Panel):
    bl_label = "Camera Import"
    bl_idname = "Importer_PT_CameraPanel"
    
    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        scene = context.scene
        data_transfer_prop = scene.data_transfer_prop
        layout = self.layout
        layout.prop(data_transfer_prop, "inCameraAbc")
        layout.prop(data_transfer_prop, "inCameraJson")
        layout.prop(data_transfer_prop, "deleteExisting")
        layout.prop(data_transfer_prop, "setFrameRange")
        layout.operator('importer.importcamera', text="Import Camera")

def register():
    register_class(Exporter_PT_CameraPanel)
    register_class(Importer_PT_CameraPanel)

def unregister():
    unregister_class(Exporter_PT_CameraPanel)
    unregister_class(Importer_PT_CameraPanel)