Sprint Adjuster
===============

- Change speed when sprinting, while preserving normal speed when not sprinting.
- Optionally set Air Control to allow better control in the air with the movement keys, to have a better chance of stopping yourself from flinging off a cliff for instance.
- Configurable keybinding to allow turning on and off on the fly.

Check the menu in Options -> Mods to control the values, and the menu in Options -> Keyboard / Mouse -> Modded Key Bindings to set a key to allow you to activate and deactivate this mod on the fly (:kbd:`Ctrl` by default).

Speed updates on the fly, so you can be ingame and change settings from the menu. However, modifying Air Control require respawn to apply.

For installation instructions and other general information, look at the README of the `base directory <https://github.com/plu5/p-borderlands>`_.

Implementation notes
--------------------

I apply the speed by modifying the first attribute effect of ``SprintDefinition'GD_PlayerShared.Sprint.SprintDefinition_Default'``, which controls foot speed while sprinting. It seems to update your speed on the fly so there is no need to call any function after change as I used to have to do back in version 1.0 when I was modifying ``GroundSpeed`` of the character controller’s class definition.

Air Control is set by modifying ``PlayerAirControl`` in ``GD_Globals.General.Globals``. The downside of doing it like this is it only takes effect on respawn, so you can’t change it on the fly. The upside is it is simple (essentially one line of code), doesn’t require hooking into anything, and works in both BL2 and TPS the same way.

Changelog
---------

2.0.0 - 2024-01-05
^^^^^^^^^^^^^^^^^^

The implementation notes used to say:

  Air Control is set by modifying the ``AirControl`` property of the ``PlayerController``’s ``Pawn``. It is also possible to modify the global value ``PlayerAirControl`` in ``GD_Globals.General.Globals``, but the former way is better because it allows you to set it even when game is running and have it take effect. It does mean we need to have access to the Pawn first, which you do not have before it is initialised, so the function that sets it hooks into ``WillowGame.WillowPlayerController.SpawningProcessComplete``.

I’ve changed it now to what I described as the worse way. That is because the pawn way does not work in TPS. ``AirControl`` does exist on the player pawn in TPS, but it is a ``FloatAttributeProperty`` instead of a ``FloatProperty``; it’s not a simple number I can change, or at least I don’t know how to change it, and whether there would be an issue if I do. In general TPS seems to be doing more complex things with Air Control, as I have for example noticed ``AirControlModifierStack`` which does not exist in BL2.

I’ve looked into a way to apply ``PlayerAirControl`` to the pawn without having to respawn, like ``ApplyGlobalPlayerMovementSettings`` which seems to do just that, but I don’t think it’s possible to call this from PythonSDK.

Modifying the global does work both in BL2 and TPS so it’s consistent, simple, less involved (like not having to hook), and I don’t know if anyone cares about being able to modify Air Control on the fly anyway, so hopefully it is only a minor inconvenience.

Bumped major version because this is a breaking change; you used to be able to change Air Control on the fly, now you can’t.

1.1.0 - 2021-05-17
^^^^^^^^^^^^^^^^^^

To apply the speed, instead of adjusting the ground speed of the character class definition I am now modifying the first attribute effect of ``SprintDefinition'GD_PlayerShared.Sprint.SprintDefinition_Default'``, which controls foot speed while sprinting. The former approach was interfering with class skills and possibly other things.

Since the new approach only affects the speed while sprinting, it only needs to be set once and there is no longer a need to have hooks on begin and end sprint, so they were removed.

The scale of the speed slider in the options was also changed, since we are now modifying a different value whose scale is totally different.

Also fixed a bug with the active toggle which was preventing air control from being set when toggling off and back on, which was caused by a syntax error (accidentally wrote ``AirControlSpinner`` instead of ``AirControlBoolean``).

1.0.0 - 2021-04-04
^^^^^^^^^^^^^^^^^^

Initial release.
