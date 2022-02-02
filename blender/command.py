import bpy
import os

def getAllObjects():
    return bpy.data.objects

def getObjectFromData(data):
    objects = [o for o in bpy.data.objects if o.data==data]
    return objects

def createCollection(name):
    collections = [c for c in bpy.data.collections if c.name == name]
    if collections:
        return collections[0]
    else:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
        return collection

def addToCollection(collection, objects=[], move=True):
    if isinstance(collection, str):
        collection = createCollection(collection)
    for obj in objects:
        if isinstance(obj, str):
            obj = bpy.data.objects.get(obj, None)
        if obj:
            if move:
                for c in obj.users_collection:
                    c.objects.unlink(obj)
            collection.objects.link(obj)
    return collection

def getAttrValue(obj, attr, frame=1):
    currentFrame = bpy.context.scene.frame_current
    
    bpy.context.scene.frame_set(frame)
    value = getattr(obj, attr, None)
    if value and value.__class__.__name__ == 'bpy_func':
        value = value()
    bpy.context.scene.frame_set(currentFrame)
    
    return value

def getAttrsFrames(map, frames=[]):
    """
    map format should be dictionary with object as key and attributes as value
    """
    currentFrame = bpy.context.scene.frame_current
    values = {}
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        for obj, attrs in map.items():
            values[obj.name] = values.get(obj.name, {})
            values[obj.name][frame] = values[obj.name].get(frame, {})
            for attr in attrs:
                values[obj.name][frame][attr] = getattr(obj, attr, None)
    bpy.context.scene.frame_set(currentFrame)
    return values

def setKeyFrame(object, attribute, value, frame):
    if hasattr(object, attribute):
        setattr(object, attribute, value)
        object.keyframe_insert(data_path=attribute, frame=frame)
        return getattr(object, attribute)

def setAttrValue(object, attribute, value, frame, key=True):
    if hasattr(object, attribute):
        setattr(object, attribute, value)
        if key:
            object.keyframe_insert(data_path=attribute, frame=frame)
        return getattr(object, attribute)

def getAlembicCache(filename):
    filename = os.path.basename(filename)
    return [cache for cache in bpy.data.cache_files if os.path.basename(cache.filepath) == filename]

def getRoot(object):
    root = object
    while root.parent:
        root = root.parent
    return root

def getDescendants(object):
    descendants = []
    for child in object.children:
        descendants.append(child)
        descendants.extend(getDescendants(child))
    return descendants

def getRootFromAbc(abcPath):
    topNodes = []
    cacheData = {}
    for cache in getAlembicCache(abcPath):
        for obj in getAllObjects():
            root = getRoot(obj)
            if not root in topNodes:
                for modifier in obj.modifiers:
                    if getattr(modifier, 'cache_file', None) == cache:
                        topNodes.append(root)
                        break

            if not root in topNodes:
                for constraint in obj.constraints:
                    if getattr(constraint, 'cache_file', None) == cache:
                        topNodes.append(root)
                        break
        cacheData[cache] = list(set(topNodes))
    return cacheData

def purgeOrphan():
    return bpy.ops.outliner.orphans_purge(do_recursive=True)

def delete(objects):
    objects = objects if hasattr(objects, '__iter__') else [objects]
    return bpy.ops.object.delete({'selected_objects':objects})

def importAlembic(abcFile, setFrameRange=True):
    if os.path.isfile(abcFile):
        bpy.ops.wm.alembic_import(
            filepath=abcFile,
            set_frame_range=setFrameRange
        )
        return getAlembicCache(abcFile)

def exportAlembic(filepath, startFrame=1, endFrame=1, selected=True):
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    bpy.ops.wm.alembic_export(filepath=filepath, start=startFrame, end=endFrame, selected=selected)
    
    if os.path.isfile(filepath):
        return filepath

def importJson(jsonFile):
    import json

    if os.path.isfile(jsonFile):
        with open(jsonFile, "r") as f:
            data = json.load(f)
    return data

def exportJson(jsonFile, data):
    import json

    folder = os.path.dirname(jsonFile)
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(jsonFile, "w") as f:
        f.write(json.dumps(data, indent=4))

def getCameraAttr(camera, startFrame=1, endFrame=1):
    if not isinstance(camera, bpy.types.Camera):
        camera = camera.data

    values = getAttrsFrames({
            camera:["lens", "sensor_fit", "sensor_width", "sensor_height", "clip_start", "clip_end"]
        }, 
        frames=range(startFrame, endFrame+1)
    )
    return values[camera.name]

def exportCamera(outputFolder, outputName="Camera", camera=None, startFrame=1, endFrame=1):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    if camera:
        camera.hide_viewport = False
        camera.hide_select = False
        camera.hide_set(False)
        camera.select_set(True)

    path = os.path.join(outputFolder, outputName)
    exportAlembic(path+".abc", startFrame=startFrame, endFrame=endFrame)
    exportJson(path+".json", getCameraAttr(camera, startFrame=startFrame, endFrame=endFrame))

def exportAsset(outputFolder, startFrame=1, endFrame=1):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    assetDirectory = r"\\192.168.0.211\bvs_ip\BVS_Cats_Project\CAT_Trailer\02_Production\3D_Asset"
    charProps = [os.path.join(assetDirectory, asset_type) for asset_type in ['Char', 'Props']]

    charPropsLibs = {}
        
    empties = [o for o in bpy.data.objects if o.type == "EMPTY"]

    for l in bpy.data.libraries:
        filepath = l.filepath
        if filepath.startswith(tuple(charProps)):
            charPropsLibs[l] = []

    for c in bpy.data.collections:
        if c.library and c.library in charPropsLibs.keys():
            charPropsLibs[c.library].append(c)

    for l, cs in charPropsLibs.items():
        bpy.ops.object.select_all(action='DESELECT')
        o = []
        for c in cs:
            for e in empties:
                if e.name == c.name:
                    o.append(e)
                    e.hide_select = False
                    e.select_set(True)
        attrs = ['hide_viewport', 'hide_render', 'hide_get']
        assetPath = l.filepath
        assetName = os.path.basename(os.path.splitext(assetPath)[0])
        
        outputFile = os.path.join(outputFolder, assetName).replace("\\", "/")
        print("EXPORTING:", outputFile)
        exportAlembic(outputFile+".abc", start=startFrame, end=endFrame, selected=True)
        exportJson(
            outputFile+".json", 
            getAttrsFrames(
                {e:attrs for e in o}, 
                frames=range(startFrame, endFrame+1)
            )
        )

def importAlembic(abcFile, setFrameRange=True):
    bpy.ops.wm.alembic_import(
        filepath=abcFile,
        set_frame_range=setFrameRange
    )
    return getAlembicCache(abcFile)