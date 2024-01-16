# Modifier Manager
# - part of T1nk-R Utilities for Blender
#
# COPYRIGHT **************************************************************************************************
# Creative Commons CC-BY-SA. Simply to put, you can create derivative works based on this script,
# and if you are nice, you don't remove the following attribution:
#
#       Original addon created by: T1nk-R - na.mondhatod@gmail.com
#
# Version 1.0.2 @ 2023-12-07
#
# DISCLAIMER *************************************************************************************************
# This script is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen.
#
# USAGE ******************************************************************************************************
# You can use this add-on to add, edit and remove custom object properties in batches.
# 
# New versions, support, feature requests, saying Hi: [https://github.com/gusztavj/Modifier-Manager](https://github.com/gusztavj/Modifier-Manager)
#

bl_info = {
    "name": "T1nk-R Focus Wizard",
    "author": "T1nk-R (GusJ)",
    "version": (1, 0, 2),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar (N) > T1nk-R Utils",
    "description": "Control visibility of objects and modifiers to see how your model looks at a specific LOD level",
    "category": "Object",
    "doc_url": "https://github.com/gusztavj/Modifier-Manager",
}

if "bpy" in locals():
    from importlib import reload
    reload(presetManager)
    reload(visibilityManager)    
    del reload

import bpy
from . import presetManager
from . import visibilityManager


# Store keymaps here to access after registration
addon_keymaps = []

# Define menu item
def menuItem(self, context):
    self.layout.operator(visibilityManager.T1NKER_OT_FocusWizard.bl_idname)

# Class registry
classes = [
    presetManager.T1nkerFocusWizardPreset,
    presetManager.T1NKER_OT_FocusWizardPresetImportExport,
    presetManager.T1NKER_OT_FocusWizardPresetEditor,
    
    presetManager.T1nkerFocusWizardPresetOperationParameters,
    presetManager.T1NKER_OT_FocusWizardPresetOperations,
    
    presetManager.T1nkerFocusWizardSettings, 

    visibilityManager.T1nkerFocusWizardPanel,    
    visibilityManager.T1NKER_OT_FocusWizard
]

# Register the plugin
def register():
    
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

# Unregister the plugin
def unregister():
    
    # Unregister key mapping
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            # Don't panic, it was not added either
            pass
        
    addon_keymaps.clear()
    
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
    
    try:
        # Delete menu item
        bpy.types.TOPBAR_MT_edit.remove(menuItem)        
    except:
        # Don't panic, it was not added at all
        pass

# Let you run registration without installing. You'll find the command in the Edit menu.
if __name__ == "__main__":
    register()
