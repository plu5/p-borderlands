import unrealsdk
from Mods import ModMenu


def _GetPlayerController():
    return unrealsdk.GetEngine().GamePlayers[0].Actor


def setSpeed(value):
    sd = unrealsdk.FindObject(
        "SprintDefinition",
        "GD_PlayerShared.Sprint.SprintDefinition_Default")
    foot_attr = sd.AttributeEffects[0]
    foot_attr.BaseModifierValue.BaseValueScaleConstant = value
    unrealsdk.Log(f"[{instance.Name}] Set Sprint Speed to {value}")


def getNormalAirControl():
    g = unrealsdk.FindObject("GlobalsDefinition", "GD_Globals.General.Globals")
    return g.PlayerAirControl


def setAirControl(value):
    PC = _GetPlayerController()
    if PC and PC.Pawn:
        PC.Pawn.AirControl = value
        unrealsdk.Log(f"[{instance.Name}] Set Air Control to {value}")


def toggleActive():
    text = ""
    # Toggle off
    if instance.active:
        ModMenu.HookManager.RemoveHooks(instance)
        instance.active = False
        text = "now inactive"

        # Restore normal values of GroundSpeed and AirControl
        if instance.speed_modified:
            setSpeed(instance.normal_speed)
        if instance.air_control_modified:
            setAirControl(instance.normal_air_control)
    # Toggle on
    else:
        ModMenu.HookManager.RegisterHooks(instance)
        instance.active = True
        text = "now active"

        # Set user-defined speed
        setSpeed(instance.SpeedSlider.CurrentValue)
        # Set user-defined Air Control
        if instance.AirControlBoolean.CurrentValue is True:
            setAirControl(instance.AirControlSlider.CurrentValue / 10)
            instance.air_control_modified = True

    unrealsdk.Log(f"[{instance.Name}] {text}")


class SprintAdjuster(ModMenu.SDKMod):
    Name = "Sprint Adjuster"
    Author = "plu5"
    Version = "1.0"
    Types = ModMenu.ModTypes.Utility
    Description = """Change speed when sprinting, while preserving normal\
 speed when not sprinting. Optionally set Air Control to allow better control\
 in the air with the movement keys, to have a better chance of stopping\
 yourself from flinging off a cliff for instance.

Check the menu in Options -> Mods to control the values, and the menu in\
 Options -> Keyboard / Mouse -> Modded Key Bindings to set a key to allow you\
 to activate and deactivate this mod on the fly."""
    normal_speed = 1
    speed_modified = False
    normal_air_control = getNormalAirControl()
    air_control_modified = False
    active = True

    SaveEnabledState = ModMenu.EnabledSaveType.LoadWithSettings

    Keybinds = [
        ModMenu.Keybind("Toggle active", "LeftControl",
                        OnPress=toggleActive),
    ]

    def __init__(self):
        super().__init__()

        self.SpeedSlider = ModMenu.Options.Slider(
            Caption="Speed",
            Description="The value to set sprint speed to. 0 is the same speed\
 as walking. Normally 1.",
            StartingValue=10,
            MinValue=0,
            MaxValue=50,
            Increment=1
        )

        self.AirControlBoolean = ModMenu.Options.Boolean(
            Caption="Set Air Control",
            Description=(
                "Whether to set Air Control."
                f" {True}: Set it to the value in the slider below / 10;"
                f" {False}: Don't change it."
            ),
            StartingValue=True,
            Choices=["No", "Yes"]  # False, True
        )

        self.AirControlSlider = ModMenu.Options.Slider(
            Caption="Air Control * 10",
            Description=f"The value * 10 to set PlayerAirControl. \
Normally ~0.1 (1). Ignored if '{self.AirControlBoolean.Caption}' is set to \
'{self.AirControlBoolean.Choices[0]}'.",
            StartingValue=8,
            MinValue=0,
            MaxValue=10,
            Increment=1
        )

        self.AirControlNested = ModMenu.Options.Nested(
            Caption="Air Control",
            Description="Configure Air Control values.",
            Children=[self.AirControlBoolean, self.AirControlSlider],
        )

        self.Options = [
            self.SpeedSlider,
            self.AirControlNested,
        ]

    def ModOptionChanged(self, option, new_value):
        # Update values if related options changed.
        # If AirControlBoolean changed
        if option == self.AirControlBoolean:
            if new_value is True:
                setAirControl(self.AirControlSlider.CurrentValue / 10)
                self.air_control_modified = True
            else:
                if self.air_control_modified:
                    setAirControl(self.normal_air_control)
        # If AirControlSlider changed
        elif option == self.AirControlSlider:
            setAirControl(new_value / 10)
        # If SpeedSlider changed
        elif option == self.SpeedSlider:
            setSpeed(new_value)
            self.speed_modified = True

    @ModMenu.Hook("WillowGame.WillowPlayerController.SpawningProcessComplete")
    def onPawnAcquired(self, caller, function, params):
        if self.AirControlBoolean.CurrentValue is True:
            setAirControl(self.AirControlSlider.CurrentValue / 10)
            self.air_control_modified = True
        # If user turned off AirControlBoolean, restore normal Air Control
        elif self.air_control_modified:
            setAirControl(self.normal_air_control)
        return True

    def Enable(self):
        super().Enable()

        # Apply initial speed value
        self.ModOptionChanged(self.SpeedSlider, self.SpeedSlider.CurrentValue)

    def Disable(self):
        # Set speed back to normal (air control is per-instance so no need)
        self.ModOptionChanged(self.SpeedSlider, self.normal_speed)

        super().Disable()


instance = SprintAdjuster()

# Allow hot-reloading of the mod with `pyexec SprintAdjuster/__init__.py'
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
