# T1nk-R's Focus Wizard add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# This module contains the main panel and key business logic of the add-on.
#
# Module and add-on authored by T1nk-R (https://github.com/gusztavj/)
#
# PURPOSE & USAGE *****************************************************************************************************************
# You can use this add-on to create presets in the form of a set of rules:
# 
# * to control the visibility of Blender objects based on object name patterns and custom object property value patterns, 
#   as well as
# * to control the visibility of object modifiers based on modifier name patterns.
# 
# With this add-on you can set up rules to easily view your model as it looks like at various LOD levels by showing respective 
# objects and modifier effects and hiding others.
# 
# You need Blender 3.6 or newer for this addon to work.
#
# Help, support, updates and anything else: https://github.com/gusztavj/Modifier-Manager
#
# COPYRIGHT ***********************************************************************************************************************
# Creative Commons CC BY-NC-SA:
#       This license enables re-users to distribute, remix, adapt, and build upon the material in any medium 
#       or format for noncommercial purposes only, and only so long as attribution is given to the creator. 
#       If you remix, adapt, or build upon the material, you must license the modified material under 
#       identical terms. CC BY-NC-SA includes the following elements:
#           BY: credit must be given to the creator.
#           NC: Only noncommercial uses of the work are permitted.
#           SA: Adaptations must be shared under the same terms.
#
#       Credit text:
#           Original addon created by: T1nk-R - janvari.gusztav@imprestige.biz
#
#       For commercial use, please contact me via janvari.gusztav@imprestige.biz. Don't be scared of
#       rigid contracts and high prices, above all I just want to know if this work is of your interest,
#       and discuss options for commercial support and other services you may need.
#
#
# Version: Please see the version tag under bl_info below.
#
# DISCLAIMER **********************************************************************************************************************
# This add-on is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen:
#   * This add-on is intended to show or hide objects under the collection you specified as the scope of operation.
#   * This add-on is intended to show or hide modifier effects of objects under the collection you specified 
#     as the scope of operation.
#   * This add-on is not intended to modify your objects and other Blender assets in any other way. In particular, this add-on 
#     is not intended to anyhow touch objects out of the scope you selected as the scope of operation.
#   * You shall be able to simply undo consequences made by this add-on.
#   * You can use this add-on to save your presets in JSON format to a file on your computer.
#   * You can use this add-on to load presets from a JSON file on your computer.
#
# You may learn more about legal matters on page https://github.com/gusztavj/Modifier-Manager
#
# *********************************************************************************************************************************

from typing import List, Set
import bpy
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Context, Panel, Operator, AddonPreferences, PropertyGroup
from . import presetManager


    
# Control panel to show in Blender's viewport, in the 'N' toolbar #################################################################
class T1nkerFocusWizardPanel(bpy.types.Panel):
    """
    Control panel to show in Blender's viewport, in the 'N' toolbar. This class enables you to select operation scope and preset,
    as well as accessing the Preset Manager implemented in presetManager.py
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------
    
    bl_idname = "OBJECT_PT_t1nker_focuswizard_panel"
    bl_label = "T1nk-R Focus Wizard (T1nk-R Utilities)"    
    bl_description = "Change object and modifier visibility based on preset rules for LOD levels"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "T1nk-R Utils"  # this is going to be the name of the tab
    
    # Public functions ============================================================================================================
    
    # Poll callback for accessibility ---------------------------------------------------------------------------------------------
    @classmethod 
    def poll(self, context):
        # Store the settings in a shorthand variable
        self.settings = context.scene.t1nkrFocusWizardSettings
        
        if len(self.settings.presets) == 0:            
            presetManager.T1NKER_OT_FocusWizardPresetOperations._revertFactoryPresets(self, context)
            
        return True
    
    # Draw UI ---------------------------------------------------------------------------------------------------------------------  
    def draw(self, context: Context):
        """Draws the panel.

        Args:
            context (Context): A bpy.context object passed by Blender.
        """
        
        # Store the settings in a shorthand variable
        self.settings = context.scene.t1nkrFocusWizardSettings                                
        layout = self.layout
        
        
        # Scope selector
        #
        
        box = layout.box()
                    
        row = box.row(align=True)
        row.label(text="Select scope")
        
        row = box.row(align=True)
        row.prop(self.settings, "affectSelectedObjectsOnly")
        
        row = box.row(align=True)
        row.prop_search(data=self.settings, property="rootCollection", search_data=bpy.data, search_property="collections")
        

        # Preset selector and info
        #
        
        box = layout.box()
        
        row = box.row(align=True)        
        row.label(text="Choose, apply, view and edit presets")        
        
        row = box.row(align=True)
        row.prop(self.settings, "presetLodLevel")
        
        # See if the preset list is empty or not
        if len(self.settings.presets) == 0:
            # HACK: Until there's a better way of initializing the empty preset list, tell the user how they can do it
            row = box.row(align=True)
            row.label(text="Click [Edit] > Check [Confirm reverting...] > Click [Revert Built-in] to load built-in presets")    

        # Access Preset Manager        
        row = box.row(align=True)
        row.operator("t1nker.focuswizardpreseteditor", text="Add/Edit Presets", icon="PREFERENCES")
        
        # Apply current preset which happens automatically upon changing. You can use this button to force manual execution.
        #
        row.operator("t1nker.focuswizard", text="Refresh", icon="FILE_REFRESH")
        
        
        # Info on selected preset
        #
        row = box.row(align=True)        
        row.label(text="Selected Preset")
        
        row = box.row(align=True)        
        propColumn = row.column()
        valueColumn = row.column()
        
        propColumn.label(text="Objects to show by name:")
        valueColumn.label(text=self.settings.selectedPreset.objectsToShowByName)
        
        propColumn.label(text="Objects to hide by name:")
        valueColumn.label(text=self.settings.selectedPreset.objectsToHideByName)
        
        propColumn.label(text="Visibility control property:")
        valueColumn.label(text=self.settings.selectedPreset.propertyName)
        
        propColumn.label(text="Objects to show by property value:")
        valueColumn.label(text=self.settings.selectedPreset.propertyValueForShowing)
        
        propColumn.label(text="Objects to hide by property value:")
        valueColumn.label(text=self.settings.selectedPreset.propertyValueForHiding)
        
        propColumn.label(text="Modifiers to show:")
        valueColumn.label(text=self.settings.selectedPreset.modifiersToShow)
        
        propColumn.label(text="Modifiers to hide:")
        valueColumn.label(text=self.settings.selectedPreset.modifiersToHide)
        
        
        # Section for operational settings
        #
        
        box = layout.box()
        
        row = box.row(align=True)
        row.label(text="Select operation mode") 
        
        row = box.row(align=True)
        row.prop(self.settings, "isVerbose")  
        
        row = box.row(align=True)
        row.prop(self.settings, "isTestOnly")  
        


# Business logic for showing/hiding objects and modifiers #########################################################################
class T1NKER_OT_FocusWizard(Operator):    
    """
    This class contains the implementation of applying the selected preset.
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "t1nker.focuswizard"
    bl_label = "T1nk-R Focus Wizard"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Other properties ------------------------------------------------------------------------------------------------------------
        
    # Lifecycle management ========================================================================================================    
    def __init__(self):
        """
        Creates `self.settings: presetManager.T1nkerFocusWizardSettings`, a shortcut for the add-on's settings.
        """
        self.settings = None                
    
    # Poll callback for accessibility ---------------------------------------------------------------------------------------------
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
    

    # Draw UI ---------------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):           
        """
        Show the panel.
        
        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
            event: An event passed by Blender. Not used by us.
            
        Returns:
            Operator return set as requested by Blender (https://docs.blender.org/api/current/bpy.ops.html) to indicate success or failure.
        """
        
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            try:
                self.settings = context.scene.t1nkrFocusWizardSettings
            except:
                pass                

        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
                
        if (self.settings.affectSelectedObjectsOnly and len(bpy.context.selected_objects) == 0):
            self.report({'ERROR'}, "You chose to process only selected objects, but no object is selected.") 
            return {'CANCELLED'}

        return result
    
    
    # Execute the operator --------------------------------------------------------------------------------------------------------
    def execute(self, context):      
        """
        Perform the requested operation using the currently selected preset 
        stored in context.scene.t1nkrFocusWizardSettings.selectedPreset.
        
        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
            
        Returns:
            Operator return set as requested by Blender (https://docs.blender.org/api/current/bpy.ops.html) to indicate success or failure.
        """                     
        
        print("")
        print("=" * 80)
        print(f"T1nk-R Focus Wizard Visibility Adjustment operation started")
        print()
            
        # Get relevant stuff to shortcut variables
        self.settings = context.scene.t1nkrFocusWizardSettings   
        viewLayer = context.view_layer            
        activeObject = viewLayer.objects.active
        root = self.settings.rootCollection
        preset = self.settings.selectedPreset
        
        if root == None:
            self.report({'ERROR'}, "No root collection selected. Select where to operate.")
            return {'CANCELLED'}
        
        selectedObjects = [obj for obj in root.all_objects if obj.select_get()]
        visibleObjects =  [obj for obj in root.all_objects if obj.visible_get()]

        print(f"Will process objects under collection '{root.name}'")

        # Big try block to make sure we terminate gracefully
        try:            
            
            # Determine scope and collect objects
            if self.settings.affectSelectedObjectsOnly:
                print(f"Will process only selected objects within the collection")
                objects = selectedObjects
            else:
                print(f"Will process all objects under the collection")
                objects = root.all_objects

            if self.settings.isVerbose:
                print("Objects to process" + ", ".join([o.name for o in objects]))

            print(f"Processing {len(objects)} objects:")
            
            if self.settings.isVerbose or self.settings.isTestOnly:
                print(f"Hiding all objects")
                
            for obj in objects:
                obj.hide_set(True, view_layer=viewLayer)
                # obj.hide_viewport = obj.hide_render = False
            
            # Show objects by name
            if len(preset.objectsToShowByName) == 0:
                                
                if self.settings.isTestOnly:
                    print(f"\tNo pattern defined to show objects by name, WOULD show all")
                else:
                    if self.settings.isVerbose:
                        print(f"\tNo pattern defined to show objects by name, let's show all")
                        
                    for obj in objects:                    
                        obj.hide_set(False, view_layer=viewLayer)
                        # obj.hide_viewport = obj.hide_render = False
            else:
                if self.settings.isVerbose:
                    print(f"\tTrying to show objects matching name pattern: {preset.objectsToShowByName}")
                
                for obj in objects:
                    match = re.search(preset.objectsToShowByName, obj.name) is not None
                    
                    if match:
                        if self.settings.isTestOnly:
                            print(f"\t\t'{obj.name}' WOULD be made visible by name-based showing pattern")
                        else:
                            obj.hide_set(False, view_layer=viewLayer)
                            # obj.hide_viewport = obj.hide_render = False
                            if self.settings.isVerbose:
                                print(f"\t\t'{obj.name}' made visible by name-based showing pattern")
                    else:
                        if self.settings.isVerbose or self.settings.isTestOnly:
                            print(f"\t\t'{obj.name}' is left intact by name-based showing pattern")  

                
            # Hide objects by name
            if len(preset.objectsToHideByName) == 0:
                if self.settings.isVerbose or self.settings.isTestOnly:
                    print(f"\tNo pattern defined to hide objects by name, let's not hide any")                                    
            else:                
                
                if self.settings.isVerbose:
                    print(f"\tTrying to hide objects matching name pattern: {preset.objectsToHideByName}")
                
                for obj in objects:
                    match = re.search(preset.objectsToHideByName, obj.name) is not None
                    
                    if match:
                        if self.settings.isTestOnly:
                            print(f"\t\t'{obj.name}' WOULD be made hidden by name-based hiding pattern")
                        else:
                            obj.hide_set(True, view_layer=viewLayer)      
                            # obj.hide_viewport = obj.hide_render = True                      
                            if self.settings.isVerbose:
                                print(f"\t\t'{obj.name}' made hidden by name-based hiding pattern")
                    else:
                        if self.settings.isVerbose or self.settings.isTestOnly:
                            print(f"\t\t'{obj.name}' is left intact by name-based hiding pattern")  


            # Show/hide objects by property value
            if len(str.strip(preset.propertyName)) == 0:
                if self.settings.isVerbose or self.settings.isTestOnly:
                    print(f"\tNo custom object property defined, ignoring visibility control by property value")
            else:
                
                propName = preset.propertyName
                if self.settings.isVerbose or self.settings.isTestOnly:
                    print(f"\tObject visibility will be determined by the value of the '{propName}' custom object property")
                
                # Show objects by property value
                if len(preset.propertyValueForShowing) == 0:
                    if self.settings.isVerbose or self.settings.isTestOnly:
                        print(f"\tNo pattern defined to show objects based on property value, ignoring rule")
                        
                else:                    
                    
                    if self.settings.isVerbose or self.settings.isTestOnly:
                        print(f"\tTrying to show objects with property '{propName}' matching pattern: {preset.propertyValueForShowing}")
                    
                    for obj in objects:
                        if propName in obj.keys():
                            match = re.search(preset.propertyValueForShowing, obj[propName]) is not None
                            
                            if match:
                                if self.settings.isTestOnly:
                                    print(f"\t\t'{obj.name}' WOULD be made visible by property-based showing pattern")
                                else:
                                    obj.hide_set(False, view_layer=viewLayer)
                                    # obj.hide_viewport = obj.hide_render = False
                                    if self.settings.isVerbose:
                                        print(f"\t\t'{obj.name}' made visible by property-based showing pattern")
                            else:
                                if self.settings.isVerbose or self.settings.isTestOnly:
                                    print(f"\t\t'{obj.name}' is left intact by property-based showing pattern")  
                                    
                # Hide objects by property value
                if len(preset.propertyValueForHiding) == 0:
                    if self.settings.isVerbose or self.settings.isTestOnly:
                        print(f"\tNo pattern defined to hide objects based on property value, ignoring rule")
                        
                else:
                    
                    if self.settings.isVerbose or self.settings.isTestOnly:
                        print(f"\tTrying to hide objects with property '{propName}' matching pattern: {preset.propertyValueForHiding}")
                    
                    for obj in objects:
                        if propName in obj.keys():            
                            match = re.search(preset.propertyValueForHiding, obj[propName]) is not None
                            
                            if match:
                                if self.settings.isTestOnly:
                                    print(f"\t\t'{obj.name}' WOULD be made hidden by property-based hiding pattern")
                                else:
                                    obj.hide_set(True, view_layer=viewLayer)
                                    # obj.hide_viewport = obj.hide_render = True
                                    if self.settings.isVerbose:
                                        print(f"\t\t'{obj.name}' made hidden by property-based hiding pattern")  
                            else:
                                if self.settings.isVerbose or self.settings.isTestOnly:
                                    print(f"\t\t'{obj.name}' is left intact by property-based hiding pattern")  
            
            # Show/hide modifiers
            if self.settings.isVerbose:
                print(f"\tAbout to process modifiers rules for objects")                    
            
                if len(preset.modifiersToShow) == 0:                
                    print(f"\t\tNo pattern defined for showing modifiers, showing all")
                    
                if len(preset.modifiersToHide) == 0:                
                    print(f"\t\tNo pattern defined for hiding modifiers, skipping rule")
            
            # Process all objects in scope
            for obj in objects:
                
                if not obj.visible_get():
                    if self.settings.isVerbose:
                        print(f"\t\tObject '{obj.name}' became hidden, skipping processing its modifiers")
                    continue
                
                if self.settings.isVerbose:
                    print(f"\t\tProcessing '{obj.name}' with {len(obj.modifiers)} modifiers")
                
                # Use this to make sure we print an object's name only once
                objectAlreadyMentioned = False
                
                # Process the show pattern
                if len(preset.modifiersToShow) == 0:
                    for modifier in obj.modifiers:                    
                        if not objectAlreadyMentioned:
                            print(f"\t\tProcessing {obj.name}")
                            objectAlreadyMentioned = True
                        print(f"\t\t\tSetting modifier {modifier.name} to visible")
                        if self.settings.isTestOnly:
                            print(f"\t\t\t\t-- but this is just a test, nothing is actually changed")
                        else:
                            modifier.show_viewport = True
                else:    
                    # Process all modifiers
                    for modifier in obj.modifiers:                    
                        
                        # Show if its name matches the pattern
                        if re.search(preset.modifiersToShow, modifier.name):                        
                            if not objectAlreadyMentioned:
                                print(f"\t\tProcessing {obj.name}")
                                objectAlreadyMentioned = True
                            print(f"\t\t\tSetting modifier {modifier.name} to visible")
                            if self.settings.isTestOnly:
                                print(f"\t\t\t\t-- but this is just a test, nothing is actually changed")
                            else:
                                modifier.show_viewport = True
                        else:
                            if self.settings.isVerbose:
                                print(f"\t\t\tNo need to show modifier {modifier.name}")
                
                # Process the hide pattern only if it's not an empty string
                if len(preset.modifiersToHide) > 0:
                    
                    # Process all modifiers
                    for modifier in obj.modifiers:         
                        
                        # Hide if its name matches the pattern           
                        if re.search(preset.modifiersToHide, modifier.name):       
                            if not objectAlreadyMentioned:
                                print(f"\t\tProcessing {obj.name}")
                                objectAlreadyMentioned = True                 
                            print(f"\t\t\tSetting modifier {modifier.name} to hidden")
                            if self.settings.isTestOnly:
                                print(f"\t\t\t\t-- but this is just a test, nothing is actually changed")
                            else:
                                modifier.show_viewport = False
                        else:
                            if self.settings.isVerbose:
                                print(f"\t\t\tNo need to hide modifier {modifier.name}")

        except Exception as ex:
            whatHappened1 = f"Whoaaa, nothing can be perfect, and an error occurred while applying the preset: {ex}."
            whatHappened2 = f"Trying to revert original visibility of object and modifiers before canceling the operation"
            print(whatHappened1)
            print(whatHappened2)
            self.report({'ERROR'}, f"{whatHappened1}\r\n{whatHappened2}")
            
            # Restore visibility state
            for obj in root.all_objects:
                obj.hide_set(obj not in visibleObjects, view_layer=viewLayer)
                
            print("Visibility of objects restored.")
                
        finally:
            # Restore active and selected flags
            viewLayer.objects.active = activeObject
            
            # Restore selection state
            for obj in root.all_objects:
                obj.select_set(obj in selectedObjects)

            print()
            print(f"T1nk-R Focus Wizard Visibility Adjustment operation exited")
            print("=" * 80)
            print()

        return {'FINISHED'}
    

