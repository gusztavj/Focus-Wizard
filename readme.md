# T1nk-R Focus Wizard add on for Blender

Part of **T1nk-R Utilities for Blender**

## TL;DR

You can use this add-on to create presets in the form of a set of rules:

* to control the visibility of Blender objects based on object name patterns and custom object property value patterns, as well as
* to control the visibility of object modifiers based on modifier name patterns.

With this add-on you can set up rules to easily view your model as it looks like at various LOD levels by showing respective objects and modifier effects and hiding others.

You need Blender 3.6 or newer for this addon to work.

Help, support, updates and anything else: [https://github.com/gusztavj/Custom-Object-Property-Manager](https://github.com/gusztavj/Custom-Object-Property-Manager)

## Legal Stuff

### Copyright

**Creative Commons CC BY-NC-SA:**

* This license enables re-users to distribute, remix, adapt, and build upon the material in any medium or format for noncommercial purposes only, and only so long as attribution is given to the creator.
* If you remix, adapt, or build upon the material, you must license the modified material under identical terms.

* CC BY-NC-SA includes the following elements:

  * BY: credit must be given to the creator.

    Credit text:
    > Original addon created by: T1nk-R - [janvari.gusztav@imprestige.biz](mailto:janvari.gusztav@imprestige.biz) / [https://github.com/gusztavj](https://github.com/gusztavj)

  * NC: Only noncommercial uses of the work are permitted.
  * SA: Adaptations must be shared under the same terms.

**For commercial use**, please contact me via [janvari.gusztav@imprestige.biz](janvari.gusztav@imprestige.biz). Don't be scared of
rigid contracts and high prices, above all I just want to know if this work is of your interest, and discuss options for commercial support and other services you may need.

Version: Please see the `version` tag under `bl_info` in `__init__.py`.

### Disclaimer

This add-on is provided as-is. Use at your own risk. No warranties, no guarantee, no liability, no matter what happens. Still I tried to make sure no weird things happen:

* This add-on may add and delete custom object properties based on your instructions.
* This add-on is not intended to modify your objects and other Blender assets in any other way.

You may learn more about legal matters on page [https://github.com/gusztavj/Custom-Object-Property-Manager](https://github.com/gusztavj/Custom-Object-Property-Manager)

## Usage and Help

## Key Scenario

While you can use the add-on to your will, the idea came when I wanted to create various LOD levels of my asset only by adding modifiers to objects. Having a lot of objects and lod levels, it became a bit awkward to select objects and select which modifiers to show when I wanted to see how the object looks at lod1 or lod2, for example.

The idea was to include a tag like \[lod0\], \[lod1\] and so on at the end of modifier names. The following shows an example of a modifier that I want to apply only when I want to see or export the LOD2 version of my asset:

![A modifier with a tag in the name](art/modifier-tagged.png)

You just simply click the name (_Decimate_ in the example) and type `[lod2]`.

Not only setting up the modifiers this way for dozens of objects takes time, but when you want to view your asset in LOD2.

This is when the add-on can help: just select LOD 2 from the **Preset** combo box, and the add-on will:

* Show all modifiers with a tag `[lod0]`, `[lod1]` and `[lod2]`, as these all shall be applied to get the LOD2 version.
* Hide all modifiers with a tag `[lod3]`, `[lod4]` and `[lod5]`, as none of these shall be visible, as they belong to higher levels.

![The add-on's panel with the preset combo box](art/panel.png)

## Reference

The following settings are offered:

* **Only process selected objects**. When checked, only selected objects will be processed, otherwise all objects in the view layer of the current scene.
* **Preset**. A couple of presets to quickly set show and hide patterns based on the key scenario, and to quickly set patterns to show or hide all modifiers.
  * Select **All** to show all modifiers.
  * Select **None** to hide all modifiers.
* **Show these**. A regular expression. If the name of a modifier added to an object matches this pattern, the modifier will be _shown_. If **Only process selected objects** is checked, only selected objects will be processed.
* **Hide these**. A regular expression. If the name of a modifier added to an object matches this pattern, the modifier will be _hidden_. If **Only process selected objects** is checked, only selected objects will be processed.
* **Verbose mode**. When checked, the log in the **System Console** will detail what is happening. For example it will list all objects in the scope and all modifiers processed. Otherwise the log will only list changes made.
* **Just a test**. When checked, nothing will actually happen. Open the **System Console** and learn the effects of your settings before actually applying them.
* **Go**. If you change a preset, modifier visibility is changed accordingly. However if you edit the patterns, you have to click Go to perform the configured changes.
