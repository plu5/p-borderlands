import unrealsdk
from Mods import ModMenu


def _GetPlayerController():
    return unrealsdk.GetEngine().GamePlayers[0].Actor


def setModeExpBaserate(mode, new_value):
    gd = unrealsdk.FindObject("AttributeInitializationDefinition",
                              "GD_Balance_Experience.Formulas.\
Init_EnemyExperience_PerPlaythrough")
    ci = gd.ConditionalInitialization

    playthroughcount = 1 if mode == 'NVHM' else 2
    for conditional in ci.ConditionalExpressionList:
        if conditional.Expressions[0].ConstantOperand2 == playthroughcount:
            conditional.BaseValueIfTrue.BaseValueConstant = new_value
            break

    unrealsdk.Log(f"[{instance.Name}] Set {mode} baserate to\
 {new_value}")


def setExpLevelscale(level_difference, which, new_scale):
    gd = unrealsdk.FindObject("GlobalsDefinition",
                              "GD_Globals.General.Globals")
    scales = gd.ExpScaleByLevelDifference

    for scale in scales:
        if scale.LevelDifference == level_difference:
            if which == 'higher':
                scale.HigherLevelEnemyExpScale = new_scale
                break
            elif which == 'lower':
                scale.LowerLevelEnemyExpScale = new_scale
                break

    unrealsdk.Log(f"[{instance.Name}] Set {level_difference} {which} scale to\
 {new_scale}")


def setRewardsMultipier(
        rewards_object, multiplier, reward_type='exp'):
    r = rewards_object
    if reward_type == 'exp':
        r.ExperienceRewardPercentage.BaseValueScaleConstant = multiplier
    elif reward_type == 'credits':
        r.CreditRewardMultiplier.BaseValueScaleConstant = multiplier
    elif reward_type == 'other':
        r.OtherCurrencyReward.BaseValueScaleConstant = multiplier


def setMissionRewardsMultiplier(
        mission_definition, multiplier, reward_type='exp'):
    if mission_definition.Reward:
        setRewardsMultipier(mission_definition.Reward, multiplier, reward_type)
    if mission_definition.AlternativeReward:
        setRewardsMultipier(
            mission_definition.AlternativeReward, multiplier, reward_type)


def unchanged(slider):
    return slider.CurrentValue == slider.StartingValue


class ExpAdjuster(ModMenu.SDKMod):
    Name = "Exp Adjuster"
    Author = "plu5"
    Version = "1.1.0"
    Types = ModMenu.ModTypes.Utility
    Description = """Adds sliders to adjust XP amounts: baserates for each\
 mode, multipliers based on level difference from killed enemies, and\
 multipliers for mission rewards.

By default all the values are set to what they are normally. Check Options ->\
 Mods menu to adjust them."""

    SaveEnabledState = ModMenu.EnabledSaveType.LoadWithSettings

    def __init__(self):
        super().__init__()

        def slider(cap, desc, starting, min_, max_, inc):
            return ModMenu.Options.Slider(cap, desc, starting, min_, max_, inc)

        def baserateSlider(mode, normally):
            return slider(f"{mode} baserate", f"Normally {normally}.",
                          normally, 0, 50, 1)

        self.BaserateSliders = {
            'NVHM': baserateSlider('NVHM', 10),
            'TVHM': baserateSlider('TVHM', 10),
            'UVHM': baserateSlider('UVHM', 11),
        }

        self.BaserateNested = ModMenu.Options.Nested(
            Caption="Baserates",
            Description="Configure the exp baserate of each mode.",
            Children=list(self.BaserateSliders.values()),
        )

        def levelscaleSlider(num, which, normally):
            s = 's' if num > 1 else ''
            return slider(f"% for enemies {num} level{s} {which}",
                          f"Normally {normally}.",
                          normally, 0, 500, 1)

        levelscales_meta = {
            1: {'higher': 100, 'lower': 90},
            2: {'higher': 103, 'lower': 70},
            3: {'higher': 106, 'lower': 40},
            4: {'higher': 109, 'lower': 15},
            5: {'higher': 112, 'lower': 5},
            6: {'higher': 115, 'lower': 1}
        }
        self.LevelscaleSliders = {}
        for level, values in levelscales_meta.items():
            H = levelscaleSlider(level, 'higher', values['higher'])
            L = levelscaleSlider(level, 'lower', values['lower'])
            self.LevelscaleSliders[f"H{level}"] = H
            self.LevelscaleSliders[f"L{level}"] = L

        self.LevelscaleNested = ModMenu.Options.Nested(
            Caption="Levelscales",
            Description="Configure exp multipliers for killed enemies x levels\
 above or below you.",
            Children=list(self.LevelscaleSliders.values()),
        )

        def missionSlider(name):
            return slider(f"{name} percentage multiplier", "Normally 100%.",
                          100, 0, 10000, 10)

        self.MissionSliders = {
            'exp': missionSlider('Experience'),
            'credits': missionSlider('Credits'),
            'other': missionSlider('Other Currency'),
        }

        self.MissionNested = ModMenu.Options.Nested(
            Caption="Mission Rewards",
            Description="Configure mission rewards multipliers.",
            Children=list(self.MissionSliders.values()),
        )

        self.Options = [
            self.BaserateNested,
            self.LevelscaleNested,
            self.MissionNested,
        ]

    def Enable(self):
        super().Enable()

        # Address initial values
        for option in [*self.BaserateNested.Children,
                       *self.LevelscaleNested.Children]:
            if not unchanged(option):
                self.ModOptionChanged(option, option.CurrentValue)

    def Disable(self):
        # Set everything back to normal
        for option in [*self.BaserateNested.Children,
                       *self.LevelscaleNested.Children]:
            if not unchanged(option):
                self.ModOptionChanged(option, option.StartingValue)

        super().Disable()

    def ModOptionChanged(self, option, new_value):
        for mode, slider in self.BaserateSliders.items():
            if option == slider:
                setModeExpBaserate(mode, new_value)

                if mode in ['TVHM', 'UVHM']:
                    # If playthrough is set, make sure the value of the
                    #  TVHM/UVHM baserate reflects the rate for the mode we’re
                    #  currently on
                    self.updateBaseratesBasedOnCurrentPlaythrough(new_value)

                return

        for designation, slider in self.LevelscaleSliders.items():
            if option == slider:
                level_difference = int(designation[1])
                which = 'higher' if designation[0] == 'H' else 'lower'
                setExpLevelscale(level_difference, which, new_value / 100)
                return

    def updateBaseratesBasedOnCurrentPlaythrough(self, new_value=None):
        """Updates baserates of TVHM/UVHM depending on playthrough currently
 loaded. This is needed because TVHM and UVHM baserates are controlled by
 the same value in the `Init_EnemyExperience_PerPlaythrough' object."""
        PC = _GetPlayerController()
        playthrough_num = PC.GetCurrentPlaythrough()
        unrealsdk.Log(f"[{instance.Name}] Current playthrough: "
                      f"{playthrough_num}")
        if playthrough_num == 1:
            setModeExpBaserate(
                'TVHM', new_value or self.BaserateSliders['TVHM'].CurrentValue)
        elif playthrough_num == 2:
            setModeExpBaserate(
                'UVHM', new_value or self.BaserateSliders['UVHM'].CurrentValue)

    @ModMenu.Hook("WillowGame.WillowPlayerController.SpawningProcessComplete")
    def onSpawn(self, caller, function, params):
        if not (unchanged(self.BaserateSliders['TVHM']) and unchanged(
                self.BaserateSliders['UVHM'])):
            self.updateBaseratesBasedOnCurrentPlaythrough()

        return True

    @ModMenu.Hook(
        "WillowGame.WillowPlayerController.ServerGrantMissionRewards")
    def onMissionRewards(self, caller, function, params):
        if params and params.Mission:
            for reward_type, slider in self.MissionSliders.items():
                if unchanged(slider):
                    break
                val = slider.CurrentValue / 100
                setMissionRewardsMultiplier(params.Mission, val, reward_type)
                unrealsdk.Log(f"[{instance.Name}] Multiplied mission "
                              f"{reward_type} x{val}")
        return True


instance = ExpAdjuster()

# Allow hot-reloading of the mod with `pyexec ExpAdjuster/__init__.py'
if __name__ == "__main__":
    unrealsdk.Log(f"[{instance.Name}] Manually loaded")
    for mod in ModMenu.Mods:
        if mod.Name == instance.Name:
            if mod.IsEnabled:
                mod.Disable()
            ModMenu.Mods.remove(mod)
            unrealsdk.Log(f"[{instance.Name}] Removed last instance")

            # Fixes inspect.getfile()
            instance.__class__.__module__ = mod.__class__.__module__
            break

ModMenu.RegisterMod(instance)
