A few Borderlands 2 PythonSDK_ mods
===================================

.. _PythonSDK: https://github.com/bl-sdk/PythonSDK

.. contents::

`Sprint Adjuster <SprintAdjuster/>`_
------------------------------------

- Change speed when sprinting, while preserving normal speed when not sprinting.
- Optionally set Air Control to allow better control in the air with the movement keys, to have a better chance of stopping yourself from flinging off a cliff for instance.
- Configurable keybinding to allow turning on and off on the fly.

`Exp Adjuster <ExpAdjuster/>`_
------------------------------

Adds sliders to adjust XP amounts:

- baserates for each mode,
- as well as multipliers based on level difference from killed enemies.

By default all the values are set to what they are normally. Check Options -> Mods menu to adjust them.


Installation
------------

First you need to have PythonSDK_ installed. There are installation instructions on the PythonSDK repository and also on `the site <https://bl-sdk.github.io/>`_. It is quite simple: just extract the PythonSDK archive to ``Binaries/Win32`` in your Borderlands 2 folder. To check all is well, when launching the game you should have a Mods submenu on your menu with the mods that are provided by default.

To add one of the mods provided here, download its archive from `releases <https://github.com/plu5/p-borderlands/releases/latest>`_ and extract the folder inside (which should be the mod name) into the PythonSDK Mods folder, which is in ``Binaries/Win32`` in your Borderlands 2 folder. If you have the game running, you will need to restart it before you’ll see the mod appearing on the Mods submenu. To enable it, select it in the Mods submenu and press :kbd:`Enter`.

For convenience, in releases there is also an archive called ``All`` with subfolders of every mod in this repository in it, so that you can easily install them all at once by extracting these folders into the PythonSDK Mods folder.

To update, just get latest and follow the same steps, overwriting the old files.

Issues
------

Bug reports and proposals for enhancement are welcome! Submit them on the `issue tracker <https://github.com/plu5/p-borderlands/issues>`_.

A good step to understand what’s gone wrong is to look at the output, which you can do by either opening the console or looking at ``python-sdk.log`` which can be found in the ``Binaries/Win32`` folder of your Borderlands 2 installation, which is 1 level up from the Mods subdirectory. Of particular interest are any Python errors that may be in there. When submitting a bug report it can be helpful to provide the contents of this file which you can paste to pastebin.com or other such sites. Reproduction steps will help too.