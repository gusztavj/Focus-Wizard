# T1nk-R's Focus Wizard add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info below.
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
#
# ** MIT License **
# 
# Copyright (c) 2023-2024, T1nk-R (Gusztáv Jánvári)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ** Commercial Use **
# 
# I would highly appreciate to get notified via [janvari.gusztav@imprestige.biz](mailto:janvari.gusztav@imprestige.biz) about 
# any such usage. I would be happy to learn this work is of your interest, and to discuss options for commercial support and 
# other services you may need.
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
    "name": "T1nk-R Focus Wizard (T1nk-R Utilities)",
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
        # kmi = km.keymap_items.new(FocusWizard.T1NKER_OT_MaterialManager.bl_idname, 'M', 'PRESS', ctrl=True, shift=True)
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
