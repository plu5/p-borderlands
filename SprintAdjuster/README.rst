Sprint Adjuster
===============

- Change speed when sprinting, while preserving normal speed when not sprinting.
- Optionally set Air Control to allow better control in the air with the movement keys, to have a better chance of stopping yourself from flinging off a cliff for instance.
- Configurable keybinding to allow turning on and off on the fly.

Check the menu in Options -> Mods to control the values, and the menu in Options -> Keyboard / Mouse -> Modded Key Bindings to set a key to allow you to activate and deactivate this mod on the fly.

Updates on the fly, so you can be ingame and change settings from the menu.

For installation instructions and other general information, look at the README of the `base directory <https://github.com/plu5/p-borderlands>`_.

Implementation notes
--------------------

I apply the speed by modifying the first attribute effect of ``SprintDefinition'GD_PlayerShared.Sprint.SprintDefinition_Default'``, which controls foot speed while sprinting. It seems to update your speed on the fly so there is no need to call any function after change as I used to have to do back in version 1.0 when I was modifying ``GroundSpeed`` of the character controller’s class definition.

Air Control is set by modifying the ``AirControl`` property of the ``PlayerController``’s ``Pawn``. It is also possible to modify the global value ``PlayerAirControl`` in ``GD_Globals.General.Globals``, but the former way is better because it allows you to set it even when game is running and have it take effect. It does mean we need to have access to the Pawn first, which you do not have before it is initialised, so the function that sets it hooks into ``WillowGame.WillowPlayerController.SpawningProcessComplete``.

Changelog
---------

1.1.0 - 2021-05-17
^^^^^^^^^^^^^^^^^^

To apply the speed, instead of adjusting the ground speed of the character class definition I am now modifying the first attribute effect of ``SprintDefinition'GD_PlayerShared.Sprint.SprintDefinition_Default'``, which controls foot speed while sprinting. The former approach was interfering with class skills and possibly other things.

Since the new approach only affects the speed while sprinting, it only needs to be set once and there is no longer a need to have hooks on begin and end sprint, so they were removed.

The scale of the speed slider in the options was also changed, since we are now modifying a different value whose scale is totally different.

Also fixed a bug with the active toggle which was preventing air control from being set when toggling off and back on, which was caused by a syntax error (accidentally wrote ``AirControlSpinner`` instead of ``AirControlBoolean``).

1.0.0 - 2021-04-04
^^^^^^^^^^^^^^^^^^

Initial release.
