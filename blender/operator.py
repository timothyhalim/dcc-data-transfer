import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from . import command
import json

class Exporter_OT_ExportCamera(Operator):
    bl_idname = "exporter.exportcamera"
    bl_label = "Export Camera"
    bl_description = "Export Camera"

    def execute(self, context):
        data_transfer_prop = context.scene.data_transfer_prop
        output_folder = bpy.path.abspath(data_transfer_prop.outCameraPath)

        command.exportCamera(
            output_folder, 
            camera=context.scene.camera, 
            startFrame=bpy.context.scene.frame_start, 
            endFrame=bpy.context.scene.frame_end
        )

        return {'FINISHED'}

class Importer_OT_ImportCamera(Operator):
    bl_idname = "importer.importcamera"
    bl_label = "Import Camera"
    bl_description = "Import Camera"

    def execute(self, context):
        data_transfer_prop = context.scene.data_transfer_prop
        abcFile = bpy.path.abspath(data_transfer_prop.inCameraAbc)
        jsonFile = bpy.path.abspath(data_transfer_prop.inCameraJson)
        setFrameRange = data_transfer_prop.setFrameRange
        deleteExisting = data_transfer_prop.deleteExisting

        if deleteExisting:
            cacheData = command.getRootFromAbc(abcFile)
            for cacheFile, topNodes in cacheData.items():
                objs = []
                for node in topNodes:
                    objs.append(node)
                    objs.extend(command.getDescendants(node))
                command.delete(objs)
            command.purgeOrphan()

        existingCamera = bpy.data.cameras.keys()
        abc = command.importAlembic(abcFile, setFrameRange)
        newCameras = [camera for camera in bpy.data.cameras.keys() 
                        if not camera in existingCamera]
        if newCameras:
            camObj = command.getObjectFromData(bpy.data.cameras[newCameras[0]])
            print(camObj)
            if camObj:
                camObj = camObj[0]
                bpy.context.scene.camera = camObj
                command.addToCollection("Camera", [camObj])

                with open(jsonFile, "r") as f:
                    data = json.load(f)
                    
                for frame, item in data.items():
                    for attr, value in item.items():
                        command.setKeyFrame(camObj.data, attr, value, int(frame))
        
        return {'FINISHED'}

def register():
    register_class(Exporter_OT_ExportCamera)
    register_class(Importer_OT_ImportCamera)

def unregister():
    unregister_class(Exporter_OT_ExportCamera)
    unregister_class(Importer_OT_ImportCamera)