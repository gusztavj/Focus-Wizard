# T1nk-R's Focus Wizard add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# This module contains the implementation of the preset manager window and logic.
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
# Help, support, updates and anything else: https://github.com/gusztavj/Focus-Wizard
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
# You may learn more about legal matters on page https://github.com/gusztavj/Focus-Wizard
#
# *********************************************************************************************************************************

from typing import List, Set
import bpy
import json
import os.path
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Context, Panel, Operator, AddonPreferences, PropertyGroup, PointerProperty


# Preset Property #################################################################################################################
class T1nkerFocusWizardPreset(bpy.types.PropertyGroup):
    
    # Properties ==================================================================================================================
    
    """
    Property group representing a preset. A preset is a set of settings describing which objects and modifiers to show/hide based on
    various conditions.
    """
    
    presetName: bpy.props.StringProperty(
        name="Preset name",
        description="The (unique) name of the preset"
        )
    """
    The (unique) name of the preset. If the name is not unique, behavior is up to Blender. It may choose the first object with the same name,
    but don't take it as granted and don't rely on this assumptions.
    """
    
    builtIn: bpy.props.BoolProperty(
        name="Built-in preset",
        description="Tells whether this preset is a built-in or custom one"
    )
    """
    Tells whether this preset is a built-in or custom one. The name of built-in presets cannot be changed.
    Built-in presets can be reverted to factory state.
    """
    
    objectsToShowByName: bpy.props.StringProperty(
        name="Objects by name to show",
        description="Name pattern of objects to show"
        )
    """
    Objects within the scope and with a name matching this pattern will be made visible.
    An empty string means all objects in the scope will be made visible.
    """
    
    objectsToHideByName: bpy.props.StringProperty(
        name="Objects by name to hide",
        description="Name pattern of objects to hide"
    )
    """
    Objects within the scope and with a name matching this pattern will be made hidden.
    An empty string means no objects in the scope will be made hidden.
    """
    
    propertyName: bpy.props.StringProperty(
        name="Visibility control property",
        description="The name of the custom object property governing object visibility"
        )
    """
    The name of the custom object property governing object visibility.
    """
    
    propertyValueForShowing: bpy.props.StringProperty(
        name="Objects by value to show",
        description="Value pattern of object properties for showing the object"
        )
    """
    If an object within the scope has the custom property specified in `propertyName`, and its value matches
    this regex, the object will be made visible.
    """
    
    propertyValueForHiding: bpy.props.StringProperty(
        name="Objects by value to hide",
        description="Value pattern of object properties for hiding the object"
        )
    """
    If an object within the scope has the custom property specified in `propertyName`, and its value matches
    this regex, the object will be made hidden.
    """
    
    modifiersToShow: bpy.props.StringProperty(
        name="Modifiers to show",
        description="Regex name pattern of modifiers to show for objects in scope"
        )
    """
    If an object is visible within the scope after applying `objectsToShowByName`, `objectsToHideByName`, `propertyValueForShowing`
    and `propertyValueForHiding`, all of its modifiers with a name matching this regex will be made visible in the viewport.
    """
    
    modifiersToHide: bpy.props.StringProperty(name="Modifiers to hide",
        description="Regex name pattern of modifiers to hide for objects in scope"
        )
    """
    If an object is visible within the scope after applying `objectsToShowByName`, `objectsToHideByName`, `propertyValueForShowing`
    and `propertyValueForHiding`, all of its modifiers with a name matching this regex will be made hidden in the viewport.
    """
    
# Addon settings ##################################################################################################################
class T1nkerFocusWizardSettings(bpy.types.PropertyGroup):
    """
    Main settings class for the add-on.
    """    
    
    # Event Handlers ==============================================================================================================
    
    # Returns the enum of presets for the combo box -------------------------------------------------------------------------------
    def _getLodLevels(self, context):
        """Returns the enum of presets for the enum property of the preset combo box.

        Returns:
            enum: Contents for the enum property in the structure of a list of (key, name description) tuples required by Blender.
        """
        
        presetNames = []
        for preset in context.scene.t1nkrFocusWizardSettings.presets:
            presetNames.append((preset.presetName, preset.presetName, f"Select preset {preset.presetName}" ))
        
        return presetNames
    
    # Event handler for selecting a different item in the Preset drop-down --------------------------------------------------------
    def _lodLevelChanged(self, context):
        """Event handler for selecting a different item in the Preset drop-down.

        This method stores the values of the selected preset in a shorthand object.
        """
        
        settings = context.scene.t1nkrFocusWizardSettings
        presets: T1nkerFocusWizardPreset = settings.presets

        for preset in presets:
            if preset.presetName == settings.presetLodLevel: # this is the currently selected item
                settings.selectedPreset.builtIn = preset.builtIn
                settings.selectedPreset.presetName = preset.presetName
                settings.selectedPreset.objectsToShowByName = preset.objectsToShowByName
                settings.selectedPreset.objectsToHideByName = preset.objectsToHideByName
                settings.selectedPreset.propertyName = preset.propertyName
                settings.selectedPreset.propertyValueForShowing = preset.propertyValueForShowing
                settings.selectedPreset.propertyValueForHiding = preset.propertyValueForHiding
                settings.selectedPreset.modifiersToShow = preset.modifiersToShow
                settings.selectedPreset.modifiersToHide = preset.modifiersToHide
                break
            
        
        # Item changed, execute operation
        # TODO: The following may drop an error, don't forget to check
        bpy.ops.t1nker.focuswizard()
        
    
    # Properties ==================================================================================================================
    
    presets: CollectionProperty(
        type=T1nkerFocusWizardPreset,
        name="Presets",
        description="Show/hide rules for each defined preset"
        )
    """
    Collection of presets (in the form of `T1nkerFocusWizardPreset` objects) governing object and modifier visibility.
    """
    
    selectedPreset: bpy.props.PointerProperty(type=T1nkerFocusWizardPreset)
    """
    Shorthand reference to the currently selected preset.
    """
    
    presetLodLevel: EnumProperty(        
        items=_getLodLevels,
        name="Select preset",
        description="Select a preset set of conditions to tell which objects/modifiers to show/hide",
        update=_lodLevelChanged
    )
    """
    A combo box to select presets.
    """

    rootCollection: bpy.props.PointerProperty(
        type=bpy.types.Collection,        
        name="Root collection",
        description="The top level collection containing your objects"
    )
    """
    The top level collection containing your objects. The add-on will never change the visibility of objects
    outside this collection.
    """

    affectSelectedObjectsOnly: BoolProperty(
        name="Only process selected objects",
        description="If unchecked, it will process all of your visible objects",
        default=False
    )
    """
    Controls whether to process only selected objects or all objects within and under `rootCollection`.
    """
        

    isVerbose: BoolProperty(
        name="Verbose mode",
        description="Check to get a detailed log on what happened and what not. Non-verbone mode only reports what actually happened.",
        default=False
    )
    """
    Controls log verbosity.
    """
    
    isTestOnly: BoolProperty(        
        name="Just a test", 
        description="Don't do anything, just show what you would do",
        default=False
    )    
    """
    Controls if actions are actually taken or just simulated.
    """
    
    confirmRevert: BoolProperty(
        name="Confirm resetting all built-in presets",
        description="Select to confirm your intent before clicking the button.",
        default=False
    )
    """
    Indicates if the user has confirmed his intention to the destructive operation of resetting built-in presets.
    """ 
    
    confirmReset: BoolProperty(
        name="Confirm deleting custom/resetting built-in presets",
        description="Select to confirm your intent before clicking the button.",
        default=False
    )
    """
    Indicates if the user has confirmed his intention to the destructive operation of resetting all presets.
    """ 
    
    presetFile: StringProperty(
        subtype="FILE_PATH",
        name="Preset file",
        description="The JSON file storing your presets or to store your presets",
        default="T1nk-R Focus Wizard Presets.json"
    )
    """
    Full path to the JSON file selected to store presets or to import presets from.
    """

# Control parameters for preset management operations #############################################################################
class T1nkerFocusWizardPresetOperationParameters(bpy.types.PropertyGroup):
    
    # Properties ==================================================================================================================
    
    action: bpy.props.EnumProperty(
        items=(
            ('ADD', "Add", "Add new preset"),
            ('REMOVE', "Remove", "Remove selected preset"),            
            ('REVERT', "Revert Built-In", "Revert built-in presets"),
            ('RESET', "Reset All", "Remove all custom and revert built-in presets"),
            ('EXPORT', "Export", "Save presets to file"),
            ('IMPORT', "Import & Append", "Load presets from file, skip existing"),
            ('REPLACE', "Import & Overwrite", "Load presets from file, overwrite existing")
            ))
    """
    Action flag to tell the operator what to perform.
    """
    
    selectedItemIndex: bpy.props.IntProperty(
        default=-1
    )
    """
    Index of the preset selected in the list of presets. Used for some actions. The default value of -1 means no item is selected.
    """

# Definition of a preset ##########################################################################################################
class PresetDefinition:
    """
    The definition of a preset. Instance-level properties initialized in the constructor include:
    * builtIn: Tells whether this preset is a built-in or custom one. The name of built-in presets cannot be changed.
    Built-in presets can be reverted to factory state.
    * name: The (unique) name of the preset. If the name is not unique, behavior is up to Blender. It may choose the first object with the same name,
    but don't take it as granted and don't rely on this assumptions.
    * objectsToShowByName: Objects within the scope and with a name matching this pattern will be made visible.
    An empty string means all objects in the scope will be made visible.
    * objectsToHideByName: Objects within the scope and with a name matching this pattern will be made hidden.
    An empty string means no objects in the scope will be made hidden.
    * propertyName: The name of the custom object property governing object visibility.
    * propertyValueForShowing: If an object within the scope has the custom property specified in `propertyName`, and its value matches
    this regex, the object will be made visible.
    * propertyValueForHiding: If an object within the scope has the custom property specified in `propertyName`, and its value matches
    this regex, the object will be made hidden.
    * modifiersToShow: If an object is visible within the scope after applying `objectsToShowByName`, `objectsToHideByName`, `propertyValueForShowing`
    and `propertyValueForHiding`, all of its modifiers with a name matching this regex will be made visible in the viewport.
    * modifiersToHide: If an object is visible within the scope after applying `objectsToShowByName`, `objectsToHideByName`, `propertyValueForShowing`
    and `propertyValueForHiding`, all of its modifiers with a name matching this regex will be made hidden in the viewport.    
    """    
    
    def __init__(
        self,
        builtIn: bool = True,
        name: str = "", 
        oShow: str = "", 
        oHide: str = "", 
        pName: str = "", 
        pShow: str = "", 
        pHide: str = "", 
        mShow: str = "", 
        mHide: str = ""):
        """Creates a new preset definition.

        Args:
            builtIn (bool, optional): Tells whether this preset is a built-in or custom one. The name of built-in presets cannot be changed. Built-in presets can be reverted to factory state. Defaults to True.
            
            name (str, optional): The (unique) name of the preset. If the name is not unique, behavior is up to Blender. It may choose the first object with the same name, but don't take it as granted and don't rely on this assumptions. Defaults to "".
            
            oShow (str, optional): Objects within the scope and with a name matching this pattern will be made visible. An empty string means all objects in the scope will be made visible. Defaults to "".
            
            oHide (str, optional): Objects within the scope and with a name matching this pattern will be made hidden. An empty string means no objects in the scope will be made hidden. Defaults to "".
            
            pName (str, optional): The name of the custom object property governing object visibility. Defaults to "".
            
            pShow (str, optional): If an object within the scope has the custom property specified in `propertyName`, and its value matches this regex, the object will be made visible. Defaults to "".
            
            pHide (str, optional): If an object within the scope has the custom property specified in `propertyName`, and its value matches this regex, the object will be made hidden. Defaults to "".
            
            mShow (str, optional): If an object is visible within the scope after applying `objectsToShowByName`, `objectsToHideByName`, `propertyValueForShowing` and `propertyValueForHiding`, all of its modifiers with a name matching this regex will be made visible in the viewport. Defaults to "".
            
            mHide (str, optional): If an object is visible within the scope after applying `objectsToShowByName`, `objectsToHideByName`, `propertyValueForShowing` and `propertyValueForHiding`, all of its modifiers with a name matching this regex will be made hidden in the viewport. Defaults to "".
        """
        # Keep doc strings in one line as VS Code only displays one line of text for an argument
        
        self.builtIn = builtIn
        self.name = name
        self.objectsToShowByName = oShow
        self.objectsToHideByName = oHide
        self.propertyName = pName
        self.propertyValueForShowing = pShow
        self.propertyValueForHiding = pHide
        self.modifiersToShow = mShow
        self.modifiersToHide = mHide

# Operator performing import/replace and export operations ########################################################################
class T1NKER_OT_FocusWizardPresetImportExport(Operator):    
    """Import/export UI for presets.
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------
    bl_idname = "t1nker.focuswizardpresetimportexport"
    bl_label = "T1nk-R Focus Wizard - Preset Importer/Exporter"
    bl_description = "Import/export T1nk-R Focus Wizard presets"
    bl_options = {'REGISTER', 'UNDO'}    
        
    # Other properties ------------------------------------------------------------------------------------------------------------
    
    action: bpy.props.EnumProperty(
        items=(            
            ('EXPORT', "Export", "Save presets to file"),
            ('IMPORT', "Import", "Import presets from file and append"),
            ('REPLACE', "Replace", "Import presets from file and overwrite existing")
            ))
    """
    Action flag to tell the operator what to perform.
    """
    
    # Public functions ============================================================================================================

    # Draw UI ---------------------------------------------------------------------------------------------------------------------
    def draw(self, context):
        """Draws the panel.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
        """
        
        settings = context.scene.t1nkrFocusWizardSettings
        layout = self.layout
        
        # We need a file selector and a button, with labels depending on the action flag
        match self.action: 
            case "EXPORT":
                layout.row().prop(settings, "presetFile", text="Export presets to file")
                layout.row().operator("t1nker.focuswizardpresetoperations", text="Save", icon="EXPORT").operationParameters.action = "EXPORT"
            case "IMPORT":
                layout.row().prop(settings, "presetFile", text="Import presets from file")
                layout.row().operator("t1nker.focuswizardpresetoperations", text="Load", icon="IMPORT").operationParameters.action = "IMPORT"
            case "REPLACE":
                layout.row().prop(settings, "presetFile", text="Import presets from file")
                layout.row().operator("t1nker.focuswizardpresetoperations", text="Load", icon="IMPORT").operationParameters.action = "REPLACE"
    
    # Poll callback for accessibility ---------------------------------------------------------------------------------------------
    @classmethod
    def poll(cls, context):
        """Standard method requested by Blender to tell if the UI can be drawn.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.

        Returns:
            Boolean: True if the UI can be drawn.
        """
        
        # We can always work, so let's just return true always
        return True
    

    # Show the UI -----------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):           
        """
        Display the UI.
        
        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
            event: Requested by Blender, not used by us.
        """
        
        self.settings = context.scene.t1nkrFocusWizardSettings
                
        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=600)                       
        
        return result  
    
    # Execute the operator --------------------------------------------------------------------------------------------------------
    def execute(self, context):
        """Execution of the operator.
        
        In this case we call other operators from the UI and need to do nothing locally.
        
        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
        """
        
        return {'FINISHED'}
        
        
# Preset manager ##################################################################################################################
class T1NKER_OT_FocusWizardPresetOperations(Operator):    
    """Perform preset management operations for T1nk-R Focus Wizard."""
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------
    bl_idname = "t1nker.focuswizardpresetoperations"
    bl_label = "T1nk-R Focus Wizard - Preset Manager"
    bl_description = "Perform action"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Other properties ------------------------------------------------------------------------------------------------------------
    
    operationParameters: bpy.props.PointerProperty(type=T1nkerFocusWizardPresetOperationParameters)
    """
    A `T1nkerFocusWizardPresetOperationParameters` specifying what to do and with which preset.
    """
            
    presetDefinitions = [
        # Presets with direct reference to lod levels (modifier set for lod n shall not be visible for other lod levels)
        # Expects lod levels be indicated in the form of /lodn/ or /lodn-m/
        PresetDefinition(name = "Direct: Lod 0", oShow = "lod0",                    oHide = "lod[12345]",                        pName = "Hide at Lod Level",    pShow = "",     pHide = "0",        mShow = "",     mHide = "lod[12345]"),
        PresetDefinition(name = "Direct: Lod 1", oShow = "lod.*1|lod0-",            oHide = "lod[02345]>|lod[234]-",             pName = "Hide at Lod Level",    pShow = "",     pHide = "[01]",     mShow = "",     mHide = "lod[02345]"),
        PresetDefinition(name = "Direct: Lod 2", oShow = "lod.*2|lod[01]-[345]",    oHide = "lod[01345]>|lod.*-1|lod[34]-",      pName = "Hide at Lod Level",    pShow = "",     pHide = "[012]",    mShow = "",     mHide = "lod[01345]"),
        PresetDefinition(name = "Direct: Lod 3", oShow = "lod.*3|lod[012]-[45]",    oHide = "lod[01245]>|lod.*-[012]|lod[4]-",   pName = "Hide at Lod Level",    pShow = "",     pHide = "[0123]",   mShow = "",     mHide = "lod[01245]"),
        PresetDefinition(name = "Direct: Lod 4", oShow = "lod.*4|lod[0123]-5",      oHide = "lod[01235]>|lod.*-[0123]|lod[4]-",  pName = "Hide at Lod Level",    pShow = "",     pHide = "[01234]",  mShow = "",     mHide = "lod[01235]"),
        PresetDefinition(name = "Direct: Lod 5", oShow = "lod.*5|lod[01234]-",      oHide = "lod[01234]>|lod.*-[01234]",         pName = "Hide at Lod Level",    pShow = "",     pHide = "[012345]", mShow = "",     mHide = "lod[01234]"),
        
        # Presets with incremental reference to lod levels (modifier set for lod n shall be visible for n and n+ levels)
        PresetDefinition(name = "Incremental: Lod 0", oShow = "lod0",                     oHide = "lod[12345]>",                       pName = "Hide at Lod Level",    pShow = "",     pHide = "0",        mShow = "",  mHide = "lod[12345]"),
        PresetDefinition(name = "Incremental: Lod 1", oShow = "lod.*1|lod0-",             oHide = "lod[02345]>|lod[234]-",             pName = "Hide at Lod Level",    pShow = "",     pHide = "[01]",     mShow = "",  mHide = "lod[2345]"),
        PresetDefinition(name = "Incremental: Lod 2", oShow = "lod.*2|lod[01]-[2345]",    oHide = "lod[01345]>|lod.*-1|lod[34]-",      pName = "Hide at Lod Level",    pShow = "",     pHide = "[012]",    mShow = "",  mHide = "lod[345]"),
        PresetDefinition(name = "Incremental: Lod 3", oShow = "lod.*3|lod[012]-[345]",    oHide = "lod[01245]>|lod.*-[012]|lod[4]-",   pName = "Hide at Lod Level",    pShow = "",     pHide = "[0123]",   mShow = "",  mHide = "lod[45]"),
        PresetDefinition(name = "Incremental: Lod 4", oShow = "lod.*4|lod[0123]-[45]",    oHide = "lod[01235]>|lod.*-[0123]|lod[4]-",  pName = "Hide at Lod Level",    pShow = "",     pHide = "[01234]",  mShow = "",  mHide = "lod[5]"),
        PresetDefinition(name = "Incremental: Lod 5", oShow = "lod.*5|lod[01234]-5",      oHide = "lod[01234]>|lod.*-[01234]",         pName = "Hide at Lod Level",    pShow = "",     pHide = "[012345]", mShow = "",  mHide = ""),
    ]
    """
    Definitions of the built-in presets in the form of `PresetDefinition`.
    """
    
    # Private functions ===========================================================================================================
    
    # Add a custom preset ---------------------------------------------------------------------------------------------------------    
    def _addCustomPreset(self, context: Context):
        """Add a custom preset. The function composes a unique name and leaves other preset properties empty.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
        """
        
        presets = context.scene.t1nkrFocusWizardSettings.presets        
        customPresetNameTrunk = "Custom Preset"
                    
        # Find a unique name for the preset
        #
        uniqueNameFound = False
        uid = 0
        
        while not uniqueNameFound:
            uid = uid + 1
            
            # Find if there's a preset with this name
            if len([p for p in presets if p.presetName == customPresetNameTrunk + " " + str(uid)]):
                continue
            
            # We only get here if the name is unique
            uniqueNameFound = True
        
        # Add the preset
        #
        item = presets.add()
        item.presetName = f"{customPresetNameTrunk} {str(uid)}"
    
    # Remove a custom preset ------------------------------------------------------------------------------------------------------
    def _removeCustomPreset(self, context: Context):
        """Removes a custom preset.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.

        Returns:
            Operator return set as requested by Blender (https://docs.blender.org/api/current/bpy.ops.html) to indicate success or failure.
        """
        
        presets = context.scene.t1nkrFocusWizardSettings.presets
        
        # We can only proceed if an item is selected for removal
        if hasattr(self.operationParameters, "selectedItemIndex") and self.operationParameters.selectedItemIndex is not None:            
            presets.remove(self.operationParameters.selectedItemIndex)
            self.report({'DEBUG'}, f"Preset {self.operationParameters.selectedItemIndex} removed")
        else:
            self.report({'ERROR'}, "No preset belongs to the 'Remove Custom Preset' button. This should not happen. The best is to file a bug.")
            return {'CANCELLED'}

    # Reset built-in presets without affecting user-defined presets ---------------------------------------------------------------
    def _revertFactoryPresets(self, context: Context):       
        """Reset built-in presets without affecting user-defined presets. You can use this method to help the user to get back
        to the start line if they messed up the built-in presets.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
        """
        
        presets = context.scene.t1nkrFocusWizardSettings.presets
        
        # Save custom presets
        customPresets = [p for p in presets if p.builtIn == False]
        
        # Drop everything from the preset list
        presets.clear()                
        
        # Add built-in presets
        for presetDefinition in T1NKER_OT_FocusWizardPresetOperations.presetDefinitions:                    
            preset = presets.add()
            preset.builtIn = True
            preset.presetName = presetDefinition.name
            preset.objectsToShowByName = presetDefinition.objectsToShowByName
            preset.objectsToHideByName = presetDefinition.objectsToHideByName
            preset.propertyName = presetDefinition.propertyName
            preset.propertyValueForShowing = presetDefinition.propertyValueForShowing
            preset.propertyValueForHiding = presetDefinition.propertyValueForHiding
            preset.modifiersToShow = presetDefinition.modifiersToShow
            preset.modifiersToHide = presetDefinition.modifiersToHide
        
        # Add previously saved custom presets
        for customPreset in customPresets:
            preset = presets.add()
            preset.builtIn = False
            preset.presetName = customPreset.presetName
            preset.objectsToShowByName = customPreset.objectsToShowByName
            preset.objectsToHideByName = customPreset.objectsToHideByName
            preset.propertyName = customPreset.propertyName
            preset.propertyValueForShowing = customPreset.propertyValueForShowing
            preset.propertyValueForHiding = customPreset.propertyValueForHiding
            preset.modifiersToShow = customPreset.modifiersToShow
            preset.modifiersToHide = customPreset.modifiersToHide

    # Reset a specific built-in preset to factory state ---------------------------------------------------------------------------
    def _revertBuiltInPreset(self, context: Context):
        """Reset a built-in preset to the factory state. You can use this function to help the user to get back to the start line 
        if they messed up a built-in preset.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
            
        Returns:
            * None if everything goes fine
            * Operator return set with the only item `'CANCELLED'` as requested by Blender (https://docs.blender.org/api/current/bpy.ops.html) 
            to indicate failure in case of — guess what — a failure.
        """
        
        # Can only proceed if a preset is selected
        if not hasattr(self.operationParameters, "selectedItemIndex") or self.operationParameters.selectedItemIndex is None:
            self.report({'ERROR'}, "No preset belongs to the 'Revert Built-in Preset' button. This should not happen. The best is to file a bug report.")
            return {'CANCELLED'}
        
        presets = context.scene.t1nkrFocusWizardSettings.presets
        
        # Get the one to revert
        presetToRevert = presets[self.operationParameters.selectedItemIndex]
        
        # Make sure the preset is built-in
        if not presetToRevert.builtIn:
            self.report({'ERROR'}, "This preset is not built-in. You shouldn't have been directed here. Sorry, and please file a bug report.")
            return {'CANCELLED'}
        
        # Recreate it from the corresponding preset definition. As names of built-in presets cannot be changed,
        # that's a good unique key.
        for presetDefinition in T1NKER_OT_FocusWizardPresetOperations.presetDefinitions:                    
            if presetToRevert.presetName == presetDefinition.presetName:
                presetToRevert.builtIn = True
                presetToRevert.presetName = presetDefinition.name
                presetToRevert.objectsToShowByName = presetDefinition.objectsToShowByName
                presetToRevert.objectsToHideByName = presetDefinition.objectsToHideByName
                presetToRevert.propertyName = presetDefinition.propertyName
                presetToRevert.propertyValueForShowing = presetDefinition.propertyValueForShowing
                presetToRevert.propertyValueForHiding = presetDefinition.propertyValueForHiding
                presetToRevert.modifiersToShow = presetDefinition.modifiersToShow
                presetToRevert.modifiersToHide = presetDefinition.modifiersToHide
        
    # Total reset: delete all custom presets and revert built-in ones -------------------------------------------------------------   
    def _resetFactoryPresets(self, context: Context):
        """
        Delete all custom presets and revert built-in presets to factory state.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
        """
        presets = context.scene.t1nkrFocusWizardSettings.presets
        presets.clear()
        
        self._revertFactoryPresets(context)    
    
    # JSON encoder for classes ----------------------------------------------------------------------------------------------------    
    def _objectEncoder(self, obj):
        """
        Convert `obj` to JSON-compatible format.
        
        Args:
            obj: Any object you like.
        """
        
        return obj.__dict__

    # Export presets --------------------------------------------------------------------------------------------------------------
    def _savePresetsToFile(self):
        """
        Export presets to a file. The file path is stored in `self.settings.presetFile`.
        """
        presetsProperty = self.settings.presets        
        presetDef: PresetDefinition
        presetDefinitions = []
        
        # Make a list of PresetDefinition objects for the JSON export
        for preset in presetsProperty:
            presetDef = PresetDefinition(
                builtIn=preset.builtIn,
                name=preset.presetName,
                oShow=preset.objectsToShowByName,
                oHide=preset.objectsToHideByName,
                pName=preset.propertyName,
                pShow=preset.propertyValueForShowing,
                pHide=preset.propertyValueForHiding,
                mShow=preset.modifiersToShow,
                mHide=preset.modifiersToHide                
            )
            
            presetDefinitions.append(presetDef)
        
        # Open file
        with open(self.settings.presetFile, "w") as jsonFile:
            # Write the objects, using the JSON encoder
            json.dump(presetDefinitions, fp=jsonFile, default=self._objectEncoder, indent=2)
    
    # Import presets --------------------------------------------------------------------------------------------------------------        
    def _loadPresetsFromFile(self, append: bool):
        """
        Imports presets from a JSON file.
        
        * In append mode (`append` is `True`), if there is an existing preset with a name also found in the file, the preset in the file
        will not be imported. That is, existing presets won't be changed.
        * In overwrite mode (`append` is `False`), if there is an existing preset with a name also found in the file, the preset in the file
        will be imported and will overwrite the existing one.

        Args:
            append (bool): `True` to not import presets with a name already existing, `False` to overwrite existing presets with the same name.
        """
        
        # Read the file
        with open(self.settings.presetFile, "r") as jsonFile:
            importedPresets = json.load(jsonFile)
        
        # Drop items with no name (as the name is the key for the preset selector enum)
        for ix, importedPreset in enumerate(importedPresets):            
            # Check if there's a valid name set and ignore if there's not
            if not "name" in importedPreset or len(str.strip(importedPreset["name"])) == 0:
                self.report({'WARNING'}, f"Preset in object {ix} of the file has no valid name; skipping item.")
                continue
        
        # Check name conflicts
        if append: # make sure existing preset are left intact
            # Skip importing presets matching the name of an existing preset
            for preset in self.settings.presets:
                for importedPreset in importedPresets:
                    if "name" in importedPreset and importedPreset["name"] == preset.presetName:
                        importedPresets.remove(importedPreset)            
        else: # do not append but replace
            # Remove the preset with the same name if there's any
            for importedPreset in importedPresets:                        
                for ix, preset in enumerate(self.settings.presets):
                    if "name" in importedPreset and importedPreset["name"] == preset.presetName:
                        self.settings.presets.remove(ix)
                        break
        
        # Convert JSON objects to preset properties
        for ix, importedPreset in enumerate(importedPresets):
            preset = self.settings.presets.add()
            preset.builtIn                  = importedPreset["builtIn"]                 if "builtIn" in importedPreset                  else False
            preset.presetName               = importedPreset["name"]                    # exists for sure, no-names has been already dropped
            preset.objectsToShowByName      = importedPreset["objectsToShow"]           if "objectsToShow" in importedPreset            else ""
            preset.objectsToHideByName      = importedPreset["objectsToHide"]           if "objectsToHide" in importedPreset            else ""
            preset.propertyName             = importedPreset["propertyName"]            if "propertyName" in importedPreset             else ""
            preset.propertyValueForShowing  = importedPreset["propertyValueForShowing"] if "propertyValueForShowing" in importedPreset  else ""
            preset.propertyValueForHiding  = importedPreset["propertyValueForHiding"]  if "propertyValueForHiding" in importedPreset   else ""
            preset.modifiersToShow          = importedPreset["modifiersToShow"]         if "modifiersToShow" in importedPreset          else ""
            preset.modifiersToHide          = importedPreset["modifiersToHide"]         if "modifiersToHide" in importedPreset          else ""  
        
    # Public functions ============================================================================================================
        
    # Execute the operator --------------------------------------------------------------------------------------------------------    
    def execute(self, context: Context):
        """
        The execution facility of the operator called in response to clicking buttons on the UI. This works as a dispatcher based on 
        operation parameters specified in `operationParameters`.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.

        Returns:
            Operator return set as requested by Blender (https://docs.blender.org/api/current/bpy.ops.html) to indicate success or failure.
        """
        self.settings = context.scene.t1nkrFocusWizardSettings
        
        # Dispatch only if an action is defined
        if hasattr(self.operationParameters, "action"):
            match self.operationParameters.action:
                case "ADD": # Add new preset
                    self._addCustomPreset(context)
                    
                    return {'FINISHED'}
                    
                case "REMOVE": # Delete an existing preset
                    # Check if an item is selected for the operation
                    if hasattr(self.operationParameters, "selectedItemIndex") and self.operationParameters.selectedItemIndex is not None:            
                        self._removeCustomPreset(context)
                        self.report({'DEBUG'}, f"Preset {self.operationParameters.selectedItemIndex} removed")
                    else:
                        self.report({'ERROR'}, "No preset belongs to the 'Remove Custom Preset' button. This should not happen. The best is to file a bug.")
                        return {'CANCELLED'}
                    
                    return {'FINISHED'}
                    
                case "EXPORT": # Export presets to a file
                    try:
                        self._savePresetsToFile()
                    except Exception as ex:
                        self.report({'ERROR'}, f"Could not save presets to '{self.settings.presetFile}' for an error of {ex}.")
                        return {'CANCELLED'}
                        
                    return {'FINISHED'}
                    
                case "IMPORT": # Import presets from a file without overwriting existing presets
                    # Fail if the file specified is not a file at all
                    if os.path.isfile(self.settings.presetFile):
                        self._loadPresetsFromFile(append=True)
                    else:
                        self.report({'ERROR'}, f"The value specified ({self.settings.presetFile}) is not a file. Cannot load presets.")
                        return {'CANCELLED'}
                    
                    return {'FINISHED'}
                
                case "REPLACE": # Import presets from a file with potentially overwriting existing presets
                    # Fail if the file specified is not a file at all
                    if os.path.isfile(self.settings.presetFile):
                        self._loadPresetsFromFile(append=False)
                    else:
                        self.report({'ERROR'}, f"The value specified ({self.settings.presetFile}) is not a file. Cannot load presets.")
                        return {'CANCELLED'}
                    
                    return {'FINISHED'}
                    
                case "REVERT": # Revert built-in presets to factory state
                    # See if there's an item selected for the operation
                    if self.operationParameters.selectedItemIndex > -1: # No, so revert all built-in preset
                        self._revertBuiltInPreset(context)
                    else: # only revert a specific preset
                        # Check if confirmation checkbox is checked
                        if self.settings.confirmRevert:
                            self._revertFactoryPresets(context)
                            self.report({'DEBUG'}, f"Built-in presets reverted to factory state")
                            
                            # Revert confirmation to prevent accidental future clicks
                            self.settings.confirmRevert = False
                        else:
                            self.report({'ERROR'}, "Please check the confirmation box above to confirm your intent")
                            return {'CANCELLED'}
                        
                    return {'FINISHED'}
                                                                
                case "RESET": # Delete all custom presets and revert built-in presets to factory state
                    # Check if confirmation checkbox is checked
                    if self.settings.confirmReset:
                        self._resetFactoryPresets(context)
                        self.report({'DEBUG'}, f"Custom presets deleted and built-in presets reverted to factory state")
                        
                        # Revert confirmation to prevent accidental future clicks
                        self.settings.confirmReset = False
                                                
                    else:
                        self.report({'ERROR'}, "Please check the confirmation  above to confirm your intent")
                        return {'CANCELLED'}
                    
                    return {'FINISHED'}
                
                case _: # Who knows what happened, but let's not do anything
                    pass
        
        # If we reached here, everything is fine and we are ready
        return {'FINISHED'}


        
# Preset editor panel #############################################################################################################
class T1NKER_OT_FocusWizardPresetEditor(Operator):    
    """
    Preset editor dialog for T1nker Focus Wizard.
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------
    bl_idname = "t1nker.focuswizardpreseteditor"
    bl_label = "T1nker Focus Wizard - Preset Editor"
    bl_options = {'REGISTER', 'UNDO'}    
    

    # Lifecycle management ========================================================================================================
    def __init__(self):
        """
        Just to create an instance-level variable
        """
        self.settings = None                
    
    # Public functions ============================================================================================================
    
    # Draw UI ---------------------------------------------------------------------------------------------------------------------
    def draw(self, context: Context):
        """Draws the UI.

        Args:
            context (Context): A bpy.context object passed by Blender.
        """
        
        # Store the settings in a shorthand variable
        self.settings = context.scene.t1nkrFocusWizardSettings
        
        # We'll create a grid and a bottom button bar
        layout = self.layout
        box = layout.box()
        
        # First let's create the grid with an action column.
        row = box.row(align=True)
        
        # Create columns. Instead of specifying column headers, add them as the first row, or headers will be missing
        # from some columns (those which contain other than editable props)
        presetNameColumn = row.column(align=True)
        nameToShowColumn = row.column(align=True)
        nameToHideColumn = row.column(align=True)        
        propertyNameColumn = row.column(align=True)
        propToShowColumn = row.column(align=True)
        propToHideColumn = row.column(align=True)
        modifierToShowColumn = row.column(align=True)
        modifierToHideColumn = row.column(align=True)
        actionColumn = row.column(align=True)
        
        # This didn't work as headers were not displaed for columns containing other than editable props
        """presetNameColumn.label(text="Preset name", icon="DOT")
        nameToShowColumn.label(text="Objects: Show by name", icon="DOT")
        nameToShowColumn.label(text="Objects: Show", icon="DOT")
        nameToHideColumn.label(text="Objects: Hide by name", icon="DOT")
        propertyNameColumn.label(text="Custom property name", icon="DOT")
        propToShowColumn.label(text="Objects: Show by value", icon="DOT")
        propToHideColumn.label(text="Objects: Hide by value", icon="DOT")
        modifierToShowColumn.label(text="Modifiers to show", icon="DOT")
        modifierToHideColumn.label(text="Modifiers to hide", icon="DOT")
        actionColumn.label(text="Actions", icon="DOT")"""
        
        
        # Create column headers in two rows
        presetNameColumn.label(text=" ")
        presetNameColumn.label(text="Preset name", icon="DOT")
        nameToShowColumn.label(text="Objects by name", icon="DOT")
        nameToShowColumn.label(text="Show", icon="DOT")
        nameToHideColumn.label(text=" ")
        nameToHideColumn.label(text="Hide", icon="DOT")        
        propertyNameColumn.label(text=" ")
        propertyNameColumn.label(text="Custom property name", icon="DOT")
        propToShowColumn.label(text="Objects by property value", icon="DOT")
        propToShowColumn.label(text="Show", icon="DOT")
        propToHideColumn.label(text=" ")
        propToHideColumn.label(text="Hide", icon="DOT")
        modifierToShowColumn.label(text="Modifiers", icon="DOT")
        modifierToShowColumn.label(text="Show", icon="DOT")
        modifierToHideColumn.label(text=" ")
        modifierToHideColumn.label(text="Hide", icon="DOT")        
        actionColumn.label(text=" ")
        actionColumn.label(text="Actions", icon="DOT")
        
        # Populate the grid with presets
        for ix, presetItem in enumerate(self.settings.presets):
            
            item: T1nkerFocusWizardPreset = presetItem
            
            # Make sure name of built-in presets cannot be edited
            if item.builtIn:
                presetNameColumn.label(text=item.presetName)
            else:
                presetNameColumn.prop(item, "presetName", text="")
                
            nameToShowColumn.prop(item, "objectsToShowByName", text="")
            nameToHideColumn.prop(item, "objectsToHideByName", text="")
            propertyNameColumn.prop(item, "propertyName", text="")
            propToShowColumn.prop(item, "propertyValueForShowing", text="")
            propToHideColumn.prop(item, "propertyValueForHiding", text="")
            modifierToShowColumn.prop(item, "modifiersToShow", text="")
            modifierToHideColumn.prop(item, "modifiersToHide", text="")        
        
            # Actions depent on prese type        
            if item.builtIn: # you can revert it
                op = actionColumn.operator("t1nker.focuswizardpresetoperations", text="Revert", icon="LOOP_BACK")
                op.operationParameters.action = "REVERT"
                op.operationParameters.selectedItemIndex = ix
            else: # you can delete it
                op = actionColumn.operator("t1nker.focuswizardpresetoperations", text="Delete", icon="X")
                op.operationParameters.action = "REMOVE"
                op.operationParameters.selectedItemIndex = ix
        
        # And now the bottom button bar
        
        bottomBar = layout.row(align=True)
        
        boxAdd = bottomBar.column()
        boxAdd.label(text="")        
        boxAdd.operator("t1nker.focuswizardpresetoperations", text="Add", icon="ADD").operationParameters.action = "ADD"
        
        boxExport = bottomBar.column()
        boxExport.label(text="")        
        boxExport.operator("t1nker.focuswizardpresetimportexport", text="Export", icon="EXPORT").action = "EXPORT"
        
        boxImport = bottomBar.column()
        boxImport.label(text="Won't overwrite existing presets")
        boxImport.operator("t1nker.focuswizardpresetimportexport", text="Import & Append", icon="IMPORT").action = "IMPORT"
        
        boxReplace = bottomBar.column()
        boxReplace.label(text="May overwrite exiting presets")        
        boxReplace.operator("t1nker.focuswizardpresetimportexport", text="Import & Overwrite", icon="IMPORT").action = "REPLACE"
        
        boxRevert = bottomBar.column()
        boxRevert.prop(self.settings, "confirmRevert")
        boxRevert.operator("t1nker.focuswizardpresetoperations", text="Revert Built-in", icon="LOOP_BACK").operationParameters.action = "REVERT"
        
        boxReset = bottomBar.column()
        boxReset.prop(self.settings, "confirmReset")
        boxReset.operator("t1nker.focuswizardpresetoperations", text="Reset All", icon="TRASH").operationParameters.action = "RESET"
        
    
    # Poll callback for accessibility ---------------------------------------------------------------------------------------------
    @classmethod
    def poll(cls, context):
        """
        Standard method requested by Blender to tell if the UI can be drawn.

        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.

        Returns:
            Boolean: True if the UI can be drawn.
        """
        
        # We can work regardless of objects are selected or not, so let's just return true always
        return True
    
    # Show the UI -----------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):           
        """
        Show the UI if it can be shown.
        
        Args:
            context (bpy.types.Context): The bpy.context object passed by Blender.
        """
        
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            try:
                self.settings = context.scene.t1nkrFocusWizardSettings
                self.settings.confirmReset = False
                self.settings.confirmRevert = False
            except:
                pass

        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=1600)                       
        
        return result    
    
    # Execute the operator --------------------------------------------------------------------------------------------------------
    def execute(self, context):
        """
        As this class is basically the UI of a dialog and operations are performed by other operators called from `draw()`, 
        there's nothing to do here but to report success.
        """
        
        return {'FINISHED'}
    
    
