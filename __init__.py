# T1nk-R's Focus Wizard add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# This module contains the lifecycle management of the add-on.
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

# Blender-specific properties #####################################################################################################

bl_info = {
    "name": "T1nk-R Focus Wizard",
    "author": "T1nk-R (GusJ)",
    "version": (2, 0, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar (N) > T1nk-R Utils",
    "description": "Control visibility of objects and modifiers to see how your model looks at a specific LOD level",
    "category": "Object",
    "doc_url": "https://github.com/gusztavj/Focus-Wizard",
}

# Lifecycle management ############################################################################################################

# Reimport libraries to make sure everything is up to date
if "bpy" in locals():
    from importlib import reload
    
    libs = [presetManager, focusWizard]
    
    for lib in libs:        
        try:
            reload(lib)
        except:
            pass

    del reload

# Library imports -----------------------------------------------------------------------------------------------------------------
import bpy
from . import presetManager
from . import focusWizard


# Properties ######################################################################################################################

addon_keymaps = []
"""
Store keymaps here (if any)
"""


classes = [
    presetManager.T1nkerFocusWizardPreset,
    presetManager.T1NKER_OT_FocusWizardPresetImportExport,
    presetManager.T1NKER_OT_FocusWizardPresetEditor,
    
    presetManager.T1nkerFocusWizardPresetOperationParameters,
    presetManager.T1NKER_OT_FocusWizardPresetOperations,
    
    presetManager.T1nkerFocusWizardSettings, 

    focusWizard.T1nkerFocusWizardPanel,    
    focusWizard.T1NKER_OT_FocusWizard
]
"""
List of classes that need to be registered by Blender
"""

# Unregister the add-on -----------------------------------------------------------------------------------------------------------
def register():
    """
    Register classes and create add-on specific settings upon enabling the add-on. Settings are created in the current scene of 
    your Blender file and therefore travel with your file.
    """
    
    # Make sure to avoid double registration
    unregister()
    
    # Register classes
    for c in classes:
        bpy.utils.register_class(c)        
    
    bpy.types.Scene.t1nkrFocusWizardOperationSettings = bpy.props.PointerProperty(type=presetManager.T1nkerFocusWizardPresetOperationParameters)
    bpy.types.Scene.t1nkrFocusWizardSettings = bpy.props.PointerProperty(type=presetManager.T1nkerFocusWizardSettings)            
    
    # Set CTRL+SHIFT+Y as shortcut
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        # km = wm.keyconfigs.addon.keymaps.new(name='Material Manager', space_type='EMPTY')
        # kmi = km.keymap_items.new(FocusWizard.T1NKER_OT_RenameCollection.bl_idname, 'M', 'PRESS', ctrl=True, shift=True)
        # addon_keymaps.append((km, kmi))
        pass

# Unregister the add-on -----------------------------------------------------------------------------------------------------------
def unregister():
    """
    Unregister everything that have been registered upon disabling the add-on.
    """
    
    # Unregister key mappings (if any)
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            # Don't panic, it was not added either
            pass
        
    addon_keymaps.clear()
    
    # Delete settings one by one so that we can proceed even if some has already been deleted
    
    try:
        del bpy.types.Scene.t1nkrFocusWizardSettings
    except:
        # Don't panic, it was not added either
        pass
        
    try:
        del bpy.types.Scene.t1nkrFocusWizardOperationSettings
    except:
        # Don't panic, it was not added either
        pass

    # Unregister classes (in reverse order)
    for c in reversed(classes):
        try:
            bpy.utils.unregister_class(c)
        except:
            # Don't panic, it was not registered at all
            pass

# Run w/o installation ############################################################################################################
# Let you run registration without installing. You'll find the command in the Edit menu.
if __name__ == "__main__":
    register()
