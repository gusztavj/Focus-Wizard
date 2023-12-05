
from typing import List
import bpy
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Object, Operator, AddonPreferences, PropertyGroup

# Addon settings for add-on preferences
class T1nkerModifierManagerAddonSettings(PropertyGroup):
           
    lodPatterns = {
        "custom": "",
        "lod0": f"\[lod[1-5]\]",    # to hide all modifiers containing [lod1], [lod2], ... [lod5] in their name
        "lod1": f"\[lod[2-5]\]",    # to hide all modifiers containing [lod1], [lod2], ... [lod4] in their name
        "lod2": f"\[lod[3-5]\]",    # as above
        "lod3": f"\[lod[4-5]\]",    # as above
        "lod4": f"\[lod[5]\]",      # as above
        "lod5": ""                  # to don't hide anything
    }
    
    def _getLodLevels(self):
        return self.lodPatterns.keys()

    affectSelectedObjectsOnly: BoolProperty(
        name="Only process selected objects",
        description="If unchecked, it will process all of your visible objects",
        default=False
    )
    
    presetLodLevel: EnumProperty(
        items=_getLodLevels,
        name="Adjust to lod level",
        description="Adjust modifier visibility to the selected LOD level"
    )
    
    modifierNamePattern: StringProperty(
        name="Custom pattern to specify which modifiers to hide",
        description="You can use a regex applied on modifier names to specify which one to hide"
    )    

    isTestOnly: BoolProperty(
        name="Just a test", 
        description="Don't do anything, just show what you would do",
        default=False
    )

    

class T1nkerModifierManagerAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    
    settings : PointerProperty(type=T1nkerModifierManagerAddonSettings)

    # Display addon preferences ===================================================================================================
    def draw(self, context):
        pass


# Main operator class
class T1NKER_OT_ModifierManager(Operator):    
    """Switch visibility of modifiers based on name pattern"""
    bl_idname = "t1nker.ModifierManager"
    bl_label = "T1nker Modifier Manager"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Operator settings
    settings : T1nkerModifierManagerAddonSettings = None        

    # Constructor =================================================================================================================
    def __init__(self):
        self.settings = None
    
    # See if the operation can run ================================================================================================
    @classmethod
    def poll(cls, context):
        return True

    # Draw operator to show export settings during invoke =========================================================================
    def draw(self, context):        
        layout = self.layout                    
        layout.label(text="Select scope")        
        layout.prop(self.settings, "affectSelectedObjectsOnly")
        
        layout.label(text="Select modifiers")
        layout.label(text="Choose a preset or specify a custom pattern")        
        layout.label(text="For preset, names for modifiers of LOD level 'n' shall contain '[lodn]'")        
        layout.label(text="This is only taken into account if you chose custom")                
        layout.prop_enum(self.settings, "presetLodLEvel")
        layout.prop(self.settings, "customPattern")      
        
        layout.label(text="Select operation mode")
        layout.prop(self.settings, "isTestOnly")  

    # Show the dialog ======================================================================================================
    def invoke(self, context, event):                
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            self.settings = context.preferences.addons[__package__].preferences.settings        

        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
                
        if (self.settings.affectSelectedObjectsOnly and len(bpy.context.selected_objects) == 0):
            raise Exception("You chose to process only selected objects, but no object is selected.")
            return {'CANCELLED'}
        
        if self.settings.presetLodLevel != "custom":
            self.settings.modifierNamePattern = T1nkerModifierManagerAddonSettings.lodPatterns[self.settings.presetLodLevel]
        
        return result

    
    # Here is the core stuff ======================================================================================================
    def execute(self, context):                           

        try:
            print(f"Modifier visibility changing process started")
            
            viewLayer = context.view_layer            
            activeObject = viewLayer.objects.active

            selection = bpy.context.selected_objects

            object: bpy.types.Object
            
            
            if self.settings.affectSelectedObjectsOnly:
                print(f"Will process only selected objects as follows:")
                objects = selection
                print(", ".join(objects))
            else:
                print(f"Will process all objects as follows:")
                objects = [o for o in viewLayer.objects]
                print(", ".join(objects))

            print(f"Will hide modifiers with a name matching the following regex pattern: {self.settings.modifierNamePattern}")

            print(f"Processing {len(objects)} objects:")
            
            for object in objects:
                print(f"\tProcessing {object.name} with {len(object.modifiers)} modifiers")
                
                for modifier in object.modifiers:                    
                    if re.match(self.settings.modifierNamePattern, modifier.name):                        
                        print(f"\t\tSetting modifier {modifier.name} to hidden")
                        if self.settings.isTestOnly:
                            print(f"\t\t\t-- but this is just a test, nothing is actually changed")
                        else:
                            modifier.show_viewport = False
                    else:
                        print(f"\t\tDid not touch modifier {modifier.name}")
                  
                
                print(f"\tMaterial to assign to object: {self.settings.materialToSet}")
                if not self.settings.isTestOnly:
                    object.data.materials.append(bpy.data.materials[self.settings.materialToSet])

        except Exception as ex:
            print(ex)
        finally:
            # Restore active and selected flags
            viewLayer.objects.active = activeObject
            print(f"Modifier visibility changing process exited")

        return {'FINISHED'}
    

