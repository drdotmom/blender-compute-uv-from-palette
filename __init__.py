bl_info = {
    "name": "ComputePaletteUV",
    "author": "Boris Nikolaev",
    'version': (1, 0),
    'blender': (2, 92, 0),
    "location": "VIEW 3D > Properties > Scene ",
    "description": "Wrap the UV to a universal palette",
    "warning": "Can broken you objects!",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scene",
}

import bpy
import os
from . import unity_content as uc
from . import gl_wrapper
from . import cs_main

try:
    import modern_gl
except:
    from subprocess import call
    pyhon_path = bpy.app.binary_path_python
    call([pyhon_path, "-m", "ensurepip", "--user"])
    call([pyhon_path, "-m", "pip", "install", "--user", "modern_gl"])
    
    try:
        import modern_gl
    except:
        "Install modern_gl manually"


def place_to_scene(objects):
    lenght = 0
    for obj in objects:
        lenght += obj.dimensions[0]
        obj.location[0] = lenght + obj.dimensions[0]


def compute_uv(wm):
    shader_path = os.path.join(os.path.dirname(__file__), "rebuild_uv_by_palette.cs.glsl")
    shader = gl_wrapper.ComputeShader(shader_path)

    if wm.ActiveOnly:

        obj = bpy.context.view_layer.objects.active
        tex = bpy.data.images[wm.Texture]
        col = [1,1,1,1]

        cs_main.compute_uv(shader, obj, tex, col)

    else:
        content = uc.read_unity_project(wm.SceneInfoPath)

        textures = []
        files = []
        for i in content:
            for obj in bpy.context.selected_objects:
                obj.select_set(False)

            if i.fbx not in files:
                bpy.ops.import_scene.fbx(filepath=i.fbx)
                files.append(i.fbx)

            if i.texture not in textures:
                if i.texture is not None:
                    tex = bpy.data.images.load(filepath=i.texture)
                else:
                    tex = None

            for obj in bpy.context.selected_objects:
                obj["path"] = i.fbx
                if obj.name == i.mesh:
                    cs_main.compute_uv(shader, obj, tex, i.color)
                    obj.select_set(False)

        h_files = []
        if wm.GenerateMaterial:
            material = bpy.data.materials.new(name="Palette")
        for obj in bpy.data.objects:

            if obj.parent is None and len(obj.children) == 0:

                if wm.GenerateMaterial:
                    if obj.type == "MESH":
                        if len(obj.material_slots) == 0:
                            obj.data.materials.append(material)
                        else:
                            obj.material_slots[0].material = material

                obj.select_set(True)
                if wm.Export:
                    bpy.ops.export_scene.fbx(filepath=obj["path"], use_selection=True)
                obj.select_set(False)

            else:
                if obj["path"] not in h_files:
                    h_files.append(obj["path"])
                    obj.color = [1 ,0, 0, 1]

                obj.select_set(False)
                if wm.ClearScene:
                    bpy.data.objects.remove(obj)

        for path in h_files:
            print("Hide for export: ", path)

        if wm.PlaceObjects:
            place_to_scene(bpy.data.objects)

    shader.Release()


class ComputeUVPanel(bpy.types.Panel):
    bl_label = "Rebuild Palette UV"
    bl_idname = "SCENE_PT_RebuildPaletteUV"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        wm = bpy.context.window_manager

        layout.label(text="Rebuild UV")
        split = layout.split(factor=10.0)

        # Debug Menu
        column = layout.column(align=False)
        column.prop(wm, "Debug")
        if wm.Debug:
            column.label(text="Manage Steps:")
            column.prop(wm, "Export")
            column.prop(wm, "PlaceObjects")
            column.prop(wm, "GenerateMaterial")
            column.prop(wm, "ClearScene")

        column = layout.column(align=False)
        column.prop(wm, "ActiveOnly")

        column = layout.column(align=True)
        column.prop(wm, "ComputeShader")
        column.enabled = False

        column = layout.column(align=False)
        if wm.ActiveOnly:
            column.prop(wm, "Texture")
        else:
            column.prop(wm, "SceneInfoPath")

        if wm.ActiveOnly:
            column.operator("btools.compute_uv", text = "Process Object")
        else:
            column.operator("btools.compute_uv", text = "Process Project")


class ComputeUV(bpy.types.Operator):
    bl_label = "Compute Palette UV"
    bl_idname = "btools.compute_uv"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = bpy.context.window_manager
        compute_uv(wm)

        return {'FINISHED'}


classes = [
    ComputeUVPanel,
    ComputeUV
]

def register():
    for clss in classes:
        bpy.utils.register_class(clss)

    bpy.types.WindowManager.Debug = bpy.props.BoolProperty(name='Debug', default=False)

    bpy.types.WindowManager.Export = bpy.props.BoolProperty(name='Export', default=True)
    bpy.types.WindowManager.GenerateMaterial = bpy.props.BoolProperty(name='Generate Material', default=True)
    bpy.types.WindowManager.PlaceObjects = bpy.props.BoolProperty(name='Place Objects', default=False)
    bpy.types.WindowManager.ClearScene = bpy.props.BoolProperty(name='Clear Scene', default=True)

    bpy.types.WindowManager.SceneInfoPath = bpy.props.StringProperty(name='SceneInfo Path', subtype='FILE_PATH')
    bpy.types.WindowManager.ComputeShader = bpy.props.StringProperty(name='Compute Shader', 
                                subtype='FILE_PATH', default="/rebuild_uv_by_palette.cs.glsl")

    bpy.types.WindowManager.ActiveOnly = bpy.props.BoolProperty(name='Active Only', default=False)
    bpy.types.WindowManager.Texture = bpy.props.StringProperty(name='Texture')

def unregister():
    for clss in classes:
        bpy.utils.unregister_class(clss)

if __name__ == "__main__":
    register()
