bl_info = {
    "name": "MikeBWalks Autorender",
    "blender": (4, 0, 2),
    "category": "Object",
}

import bpy
import os
    
class MikeBWalksAutoRender(bpy.types.Operator):
    """MikeBWalks Autorender"""
    bl_idname = "object.mikebwalks_auto_render"
    bl_label = "Autorender MikeBWalks clips"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        blend_path = bpy.context.blend_data.filepath
        blend_dir = os.path.dirname(blend_path)
        out_dir = blend_dir + '\\render'
        date = os.path.basename(blend_dir)
        
        # ensure we have nothing selected
        bpy.ops.sequencer.select_all(action="DESELECT")

        sed = bpy.data.scenes[0].sequence_editor

        # get the list of all the strips currently in the editor
        strips = filter(lambda x: x.type == 'MOVIE' and x.mute == False, sed.sequences_all)
        
        for strip in strips:
            start = strip.frame_final_start
            end = strip.frame_final_end
            
            bpy.data.scenes[0].frame_start = start
            bpy.data.scenes[0].frame_end = end
            
            output_name = out_dir + '\\' + date + "_" + strip.name.lower().replace(' ', '_') + '.mp4'
            bpy.context.scene.render.filepath = output_name
            print(f'Rendering animation [{output_name}]...')
            
            bpy.ops.render.render(animation=True)

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.row().separator()
    self.layout.operator(MikeBWalksAutoRender.bl_idname)

def register():
    bpy.utils.register_class(MikeBWalksAutoRender)
    bpy.types.SEQUENCER_MT_strip.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MikeBWalksAutoRender)
    bpy.types.SEQUENCER_MT_strip.remove(menu_func)

if __name__ == "__main__":
    register()