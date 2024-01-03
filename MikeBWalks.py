import bpy
import os
import glob
import json
from datetime import datetime, timedelta
import re
import time

frame_rate = 59.94

def get_blend_dir():
    blend_path = bpy.context.blend_data.filepath
    return os.path.dirname(blend_path)

def get_output_dir():
    blend_dir = get_blend_dir()
    return blend_dir + '\\render'

def get_date():
    return os.path.basename(get_blend_dir())

bl_info = {
    "name": "MikeBWalks",
    "blender": (4, 0, 2),
    "category": "Object",
}
    
class MikeBWalksAutoRender(bpy.types.Operator):
    '''MikeBWalks Render'''
    bl_idname = "object.mikebwalks_auto_render"
    bl_label = "MikeBWalks: Render clips"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):        
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
            
            output_name = get_output_dir() + '\\' + get_date() + "_" + strip.name.replace(' ', '_') + '.mp4'
            bpy.context.scene.render.filepath = output_name
            bpy.context.scene.render.use_sequencer = True
            bpy.context.scene.render.use_compositing = False
            print(f'Rendering animation [{output_name}]...')
            
            bpy.ops.render.render(animation=True)

        return {'FINISHED'}
    
class MikeBWalksAutoStrip(bpy.types.Operator):
    '''MikeBWalks Strip'''
    bl_idname = 'object.mikebwalks_auto_strip'
    bl_label = 'MikeBWalks: Strips from events'
    bl_options = {'REGISTER', 'UNDO'}
    
    def load_metadata(self):
        jsonFiles = glob.glob(get_blend_dir() + '\\*.json')

        if len(jsonFiles) > 1:
            print(f'Expected only 1 JSON file but found {len(jsonFiles)}')
        
        metadataFile = open(jsonFiles[0])
        metadataContent = metadataFile.read()
        metadata = json.loads(metadataContent)
        
        return metadata

    def timespan_to_frame(self, timespan):
        result = re.search(r'(\d{2}):(\d{2}):(\d{2})', timespan)
        hours = int(result.group(1))
        minutes = int(result.group(2))
        seconds = int(result.group(3))
        
        return int(((hours * 3600) + (minutes * 60) + seconds) * frame_rate)

    def create_event_strip(self, event):
        bpy.ops.sequencer.select_all(action='SELECT')
            
        start_frame = self.timespan_to_frame(event['adjusted_start'])        
        bpy.context.scene.frame_set(start_frame)
        bpy.ops.sequencer.split(side='BOTH')
        print(f'Split at {start_frame}')
        
        end_frame = self.timespan_to_frame(event['adjusted_end'])
        bpy.context.scene.frame_set(end_frame)  
        bpy.ops.sequencer.split(side='BOTH')
        print(f'Split at {end_frame}')
        
        bpy.ops.sequencer.select_all(action="DESELECT")
        bpy.context.scene.frame_set(bpy.context.scene.frame_current - 1)
        bpy.ops.sequencer.select_side_of_frame(extend=False, side='CURRENT')
        for sequence in bpy.context.selected_sequences:
            sequence.name = event['name']
    
    def mute_nonevent_strips(self):
        for sequence in bpy.context.sequences:
            if sequence.name.startswith('20'):
                sequence.mute = True
            else:
                sequence.mute = False
    
    def execute(self, context):
        original_context_type = bpy.context.area.type
        if bpy.context.area.type != 'SEQUENCE_EDITOR':
            bpy.context.area.type = 'SEQUENCE_EDITOR'
        
        metadata = self.load_metadata()
        for event in metadata:
            if event['name'].startswith('SKIP'):
                print(f'Skipping event with name [{event["name"]}]')
            else:
                self.create_event_strip(event)
            
        self.mute_nonevent_strips()
                
        bpy.context.area.type = original_context_type
        
        return {'FINISHED'}

def menu_func_1(self, context):
    self.layout.operator(MikeBWalksAutoRender.bl_idname)
    
def menu_func_2(self, context):
    self.layout.row().separator()
    self.layout.operator(MikeBWalksAutoStrip.bl_idname)

def register():
    bpy.utils.register_class(MikeBWalksAutoRender)
    bpy.utils.register_class(MikeBWalksAutoStrip)
    bpy.types.SEQUENCER_MT_strip.append(menu_func_2)
    bpy.types.SEQUENCER_MT_strip.append(menu_func_1)

def unregister():
    bpy.types.SEQUENCER_MT_strip.remove(menu_func_1)
    bpy.types.SEQUENCER_MT_strip.remove(menu_func_2)
    bpy.utils.unregister_class(MikeBWalksAutoRender)
    bpy.utils.unregister_class(MikeBWalksAutoStrip)

if __name__ == '__main__':
    register()