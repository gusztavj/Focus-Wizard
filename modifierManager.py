
from typing import List
import bpy
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Context, Panel, Operator, AddonPreferences, PropertyGroup

# Addon settings for add-on preferences ===========================================================================================
class T1nkerModifierManagerAddonSettings(bpy.types.PropertyGroup):
    """
    Addon settings for add-on preferences.
    """
    
    # Some internal structures ====================================================================================================
           
    # Show and hide patterns for presets
    presetPatterns = {
        "custom":   {"show": ".*",              "hide": ""},
        "lod0":     {"show": "\[lod0\]",        "hide": "\[lod[1-5]\]"},    # to hide all modifiers containing [lod1], [lod2], ... [lod5] in their name
        "lod1":     {"show": "\[lod[0-1]\]",    "hide": "\[lod[2-5]\]"},    # to hide all modifiers containing [lod1], [lod2], ... [lod4] in their name
        "lod2":     {"show": "\[lod[0-2]\]",    "hide": "\[lod[3-5]\]"},    # as above
        "lod3":     {"show": "\[lod[0-3]\]",    "hide": "\[lod[4-5]\]"},    # as above
        "lod4":     {"show": "\[lod[0-4]\]",    "hide": "\[lod[5]\]"},      # as above
        "lod5":     {"show": "\[lod[0-5]\]",    "hide": ""},                # to don't hide anything
        "all":      {"show": ".*",              "hide": ""},                # to show all modifiers
        "none":     {"show": "",                "hide": ".*"},              # to hide all modifiers
    }
    """
    Show and hide patterns for presets with the key being the enum value, followed by the pair of show and hide patterns.
    """
    
    # Enum data for Blender to display the preset combo box 
    presetEnum = [
        ("custom", "Custom", "Specify your own regex"),
        ("lod0", "Lod 0", "Show effects for modifiers designed for LOD 0 and hide effects of all modifiers designed for LOD levels 1-5"),
        ("lod1", "Lod 1", "Show effects for modifiers designed for LOD 1 and hide effects of all modifiers designed for LOD levels 2-5"),
        ("lod2", "Lod 2", "Show effects for modifiers designed for LOD 2 and hide effects of all modifiers designed for LOD levels 3-5"),
        ("lod3", "Lod 3", "Show effects for modifiers designed for LOD 3 and hide effects of all modifiers designed for LOD levels 4-5"),
        ("lod4", "Lod 4", "Show effects for modifiers designed for LOD 4 and hide effects of all modifiers designed for LOD level 5"),
        ("lod5", "Lod 5", "Show effects for modifiers designed for LOD 5"),
        ("all",  "Show all", "Show effects of all modifiers"),
        ("none",  "Hide all", "Hide effects of all modifiers"),
    ]
    """
    Enum data for Blender to display the preset combo box.
    """
    
    
    # Returns the enum of presets for the combo box ===============================================================================
    def _getLodLevels(self, context):
        """Returns the enum of presets for the enum property of the preset combo box.

        Returns:
            enum: Contents for the enum property
        """
        return self.presetEnum
    
    # Event handler for selecting a different item in the Preset drop-down ========================================================
    def _lodLevelChanged(self, context):
        """Event handler for selecting a different item in the Preset drop-down.

        This method sets the patterns for the selected preset.
        """

        # Check if Custom is selected and do nothing if it is
        if context.scene.t1nkrModifierManagerSettings.presetLodLevel == "custom": 
            return None
        
        # Set the predefined patterns
        context.scene.t1nkrModifierManagerSettings.showThese = self.presetPatterns[context.scene.t1nkrModifierManagerSettings.presetLodLevel]["show"]
        context.scene.t1nkrModifierManagerSettings.hideThese = self.presetPatterns[context.scene.t1nkrModifierManagerSettings.presetLodLevel]["hide"]
        
        # Item changed, execute operation
        bpy.ops.t1nker.modifiermanager()
        
    
       

    # Properties ==================================================================================================================

    # Controls whether to process selected objects or all 
    affectSelectedObjectsOnly: BoolProperty(
        name="Only process selected objects",
        description="If unchecked, it will process all of your visible objects",
        default=False
    )
    """
    Controls whether to process selected objects or all.
    """
        
    # Stores which pattern preset is selected.
    presetLodLevel: EnumProperty(        
        items=_getLodLevels,
        name="Preset",
        description="Adjust modifier visibility to the selected LOD level or special case",
        update=_lodLevelChanged
    )
    """
    Stores which pattern preset is selected.
    """
    
    # Defines a pattern. Modifiers with a name matching this pattern will be made visible in the viewport.
    showThese: StringProperty(
        name="Show these",
        description="You can use a regex applied on modifier names to specify which to show"
    )
    """
    # Defines a pattern. Modifiers with a name matching this pattern will be made visible in the viewport
    """
    
    # Defines a pattern. Modifiers with a name matching this pattern will be made hidden in the viewport.
    hideThese: StringProperty(
        name="Hide these",
        description="You can use a regex applied on modifier names to specify which to hide"
    )    
    """
    Defines a pattern. Modifiers with a name matching this pattern will be made hidden in the viewport
    """

    # Controls log verbosity.
    isVerbose: BoolProperty(
        name="Verbose mode",
        description="Check to get a detailed log on what happened and what not. Non-verbone mode only reports what actually happened.",
        default=False
    )
    """
    Controls log verbosity.
    """
    
    # Controls if actions are actually taken or just simulated.
    isTestOnly: BoolProperty(        
        name="Just a test", 
        description="Don't do anything, just show what you would do",
        default=False
    )    
    """
    Controls if actions are actually taken or just simulated.
    """
    
# Control panel to show in Blender's viewport, in the 'N' toolbar =================================================================
class T1nkerModifierManagerPanel(bpy.types.Panel):
    """Control panel to show in Blender's viewport, in the 'N' toolbar
    """
    # Blender-specific stuff
    bl_idname = "OBJECT_PT_t1nker_modifiermanager_panel"
    bl_label = "Modifier Visibility for LODs (T1nk-R Utilities)"    
    bl_description = "Switch visibility of modifiers based on modifier name pattern"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "T1nk-R Utils"  # this is going to be the name of the tab
    
    # Draw the panel  =============================================================================================================  
    def draw(self, context: Context):
        """Draws the panel.

        Args:
            context (Context): A bpy.context object passed by Blender.
        """
        
        # Store the settings in a shorthand variable
        self.settings = context.scene.t1nkrModifierManagerSettings
        
        # We'll create boxes with rows for the various settings
        
        layout = self.layout
        
        box = layout.box()
                    
        row = box.row(align=True)
        row.label(text="Select scope")
        
        row = box.row(align=True)
        row.prop(self.settings, "affectSelectedObjectsOnly")
        
        
        box = layout.box()
        
        row = box.row(align=True)        
        row.label(text="Select preset to hide modifiers")
        
        row = box.row(align=True)
        row.label(text="For presets, names for modifiers of LOD level 'n' shall contain '[lodn]'")
        
        row = box.row(align=True)        
        row.prop(self.settings, "presetLodLevel")
        
        
        box = layout.box()
        
        row = box.row(align=True)        
        row.label(text="Custom patterns")
        
        row = box.row(align=True)
        row.label(text="Specify custom regex for showing modifiers") 
        
        row = box.row(align=True)
        row.prop(self.settings, "showThese")
        
        
        row = box.row(align=True)
        row.label(text="Specify custom regex for hiding modifiers") 
        
        row = box.row(align=True)
        row.prop(self.settings, "hideThese")      
        

        box = layout.box()
        
        row = box.row(align=True)
        row.label(text="Select operation mode") 
        
        row = box.row(align=True)
        row.prop(self.settings, "isVerbose")  
        
        row = box.row(align=True)
        row.prop(self.settings, "isTestOnly")  
        
        layout.operator("t1nker.modifiermanager", text="Go")
        
    

# Main operator class to switch visibility of modifiers based on name pattern =====================================================
class T1NKER_OT_ModifierManager(Operator):    
    """Switch visibility of modifiers based on name pattern."""
    
    # Blender-specific stuff
    bl_idname = "t1nker.modifiermanager"
    bl_label = "T1nker Modifier Visibility Manager"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Operator settings
    settings : T1nkerModifierManagerAddonSettings = None        

    # Constructor =================================================================================================================
    def __init__(self):
        self.settings = None        
    
    # See if the operation can run ================================================================================================
    @classmethod
    def poll(cls, context):
        """Standard method requested by Blender to tell if the UI can be drawn.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.

        Returns:
            Boolean: True if the UI can be drawn.
        """
        
        # We can work regardless of objects are selected or not, so let's just return true always
        return True
    

    # Show the dialog =============================================================================================================
    def invoke(self, context, event):           
        """Show the panel if it can be shown.
        """
        
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            try:
                #self.settings = context.preferences.addons[__package__].preferences.settings
                self.settings = context.scene.t1nkrModifierManagerSettings
            except:
                pass

        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
                
        if (self.settings.affectSelectedObjectsOnly and len(bpy.context.selected_objects) == 0):
            raise Exception("You chose to process only selected objects, but no object is selected.")
            return {'CANCELLED'}
        
        if self.settings.presetLodLevel != "custom":
            self.settings.hideThese = T1nkerModifierManagerAddonSettings.presetPatterns[self.settings.presetLodLevel]["hide"]
            self.settings.showThese = T1nkerModifierManagerAddonSettings.presetPatterns[self.settings.presetLodLevel]["show"]
        
        return result

    
    # Here is the core stuff ======================================================================================================
    def execute(self, context):      
        """Execute the operator
        """                     
        
        print(f"Modifier visibility changing process started")
            
        # Get relevant stuff to shortcut variables
        self.settings = context.scene.t1nkrModifierManagerSettings            
        viewLayer = context.view_layer            
        activeObject = viewLayer.objects.active

        # Big try block to make sure we terminate gracefully
        try:            
                        
            # Determine scope and collect objects
            if self.settings.affectSelectedObjectsOnly:
                print(f"Will process only selected objects")
                objects = bpy.context.selected_objects
            else:
                print(f"Will process all objects as follows")
                objects = viewLayer.objects

            if self.settings.isVerbose:
                print("Objects to process" + ", ".join([o.name for o in objects]))

            print(f"Will show modifiers with a name matching the following regex pattern: {self.settings.showThese}")
            print(f"Will hide modifiers with a name matching the following regex pattern: {self.settings.hideThese}")
            
            print(f"Processing {len(objects)} objects:")
            
            if len(self.settings.showThese) == 0 and self.settings.isVerbose:
                print(f"\tNo pattern defined to show modifiers, won't make visible any")
                
            if len(self.settings.hideThese) == 0 and self.settings.isVerbose:
                print(f"\tNo pattern defined to hide modifiers, won't make hidden any")
                    
            # Process all objects in scope
            for object in objects:
                if self.settings.isVerbose:
                    print(f"\tProcessing {object.name} with {len(object.modifiers)} modifiers")
                
                # Use this to make sure we print an object's name only once
                objectAlreadyMentioned = False
                
                # Process the show pattern only if it's not an empty string
                if len(self.settings.showThese) > 0:
                    
                    # Process all modifiers
                    for modifier in object.modifiers:                    
                        
                        # Show if its name matches the pattern
                        if re.search(self.settings.showThese, modifier.name):                        
                            if not objectAlreadyMentioned:
                                print(f"\tProcessing {object.name}")
                                objectAlreadyMentioned = True
                            print(f"\t\tSetting modifier {modifier.name} to visible")
                            if self.settings.isTestOnly:
                                print(f"\t\t\t-- but this is just a test, nothing is actually changed")
                            else:
                                modifier.show_viewport = True
                        else:
                            if self.settings.isVerbose:
                                print(f"\t\tNo need to show modifier {modifier.name}")
                
                # Process the hide pattern only if it's not an empty string
                if len(self.settings.hideThese) > 0:
                    
                    # Process all modifiers
                    for modifier in object.modifiers:         
                        
                        # Hide if its name matches the pattern           
                        if re.search(self.settings.hideThese, modifier.name):       
                            if not objectAlreadyMentioned:
                                print(f"\tProcessing {object.name}")
                                objectAlreadyMentioned = True                 
                            print(f"\t\tSetting modifier {modifier.name} to hidden")
                            if self.settings.isTestOnly:
                                print(f"\t\t\t-- but this is just a test, nothing is actually changed")
                            else:
                                modifier.show_viewport = False
                        else:
                            if self.settings.isVerbose:
                                print(f"\t\tNo need to hide modifier {modifier.name}")
                  

        except Exception as ex:
            print(ex)
        finally:
            # Restore active and selected flags
            viewLayer.objects.active = activeObject
            
            print(f"Modifier visibility changing process exited")

        return {'FINISHED'}
    

