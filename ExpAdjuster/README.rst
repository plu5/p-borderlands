Exp Adjuster
============

Adds sliders to adjust XP amounts:

- baserates for each mode,
- as well as multipliers based on level difference from killed enemies.

By default all the values are set to what they are normally. Check Options -> Mods menu to adjust them.

- TODO: Add ability to adjust mission xp

For installation instructions and other general information, look at the README of the `base directory <..>`_.

Implementation notes
--------------------

Baserates for each mode are set by modifying the conditional expressions in the ``AttributeInitializationDefinition`` instance ``GD_Balance_Experience.Formulas.Init_EnemyExperience_PerPlaythrough``. There are two conditionals there with a baserate for ``PlayThroughCount`` 1 and 2. Through testing, I’ve discovered 1 only affects the rate in NVHM, and 2 affects both TVHM and UVHM. In order to allow users to set the TVHM and UVHM rates separately, I check which playthrough the user is on and set the appropriate values on each spawn and each time one of these rates is changed.

Levelscales are set by modifying the scales in the ``ExpScaleByLevelDifference`` property of the ``GlobalsDefinition`` instance ``GD_Globals.General.Globals``.
