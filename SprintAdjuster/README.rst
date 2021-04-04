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

The way I do it is when player begins sprinting changing the ``GroundSpeed`` of the controller’s character class definition, then to update the actual values calling ``ApplyCharacterClassDefaults`` with the modified definition. When player stops sprinting, I do the same thing but with the old ``GroundSpeed`` value.

I think a better way would be to simply add an attribute effect to PlayerClass.SprintSettings.AttributeEffects, but I have not worked out how to do that yet.

Air Control is set by modifying the ``AirControl`` property of the ``PlayerController``’s ``Pawn``. It is also possible to modify the global value ``PlayerAirControl`` in ``GD_Globals.General.Globals``, but the former way is better because it allows you to set it even when game is running and have it take effect. It does mean we need to have access to the Pawn first, which you do not have before it is initialised, so the function that sets it hooks into ``WillowGame.WillowPlayerController.SpawningProcessComplete``.
