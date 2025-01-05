import unrealsdk
from Mods import ModMenu


def setSpeed(value):
    sd = unrealsdk.FindObject(
        "SprintDefinition",
        "GD_PlayerShared.Sprint.SprintDefinition_Default")
    foot_attr = sd.AttributeEffects[0]
    foot_attr.BaseModifierValue.BaseValueScaleConstant = value
    unrealsdk.Log(f"[{instance.Name}] Set Sprint Speed to {value}")


def getGlobals():
    return unrealsdk.FindObject(
        "GlobalsDefinition", "GD_Globals.General.Globals")


def getAirControl():
    return getGlobals().PlayerAirControl


def setAirControl(value):
    getGlobals().PlayerAirControl = value
    unrealsdk.Log(f"[{instance.Name}] Set Air Control to {value}")


def toggleActive():
    text = ""
    # Toggle off
    if instance.active:
        instance.active = False
        text = "now inactive"
        instance.unapply()
    # Toggle on
    else:
        instance.active = True
        text = "now active"
        instance.apply()

    unrealsdk.Log(f"[{instance.Name}] {text}")


class MessageField(ModMenu.Options.Field):
    """
    A field which displays in the options list but holds no value.
    (Can't use ModMenu.Options.Field directly for this because it is abstract)

    Attributes:
        Caption: The name of the field.
        Description: A short description of the field to show when hovering
                     over it in the menu.
        IsHidden: If the field is hidden from the options menu.
    """
    def __init__(self, Caption, Description="", IsHidden=False):
        self.Caption = Caption
        self.Description = Description
        self.IsHidden = IsHidden


class SprintAdjuster(ModMenu.SDKMod):
    Name = "Sprint Adjuster"
    Author = "plu5"
    Version = "2.0.0"
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
    normal_air_control = getAirControl()
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

        self.AirControlRespawnHint = MessageField(
            Caption="Note: Requires respawn after",
            Description="Modifying Air Control requires respawn to take \
effect.",
        )

        self.AirControlNested = ModMenu.Options.Nested(
            Caption="Air Control",
            Description="Configure Air Control values.",
            Children=[self.AirControlBoolean, self.AirControlSlider,
                      self.AirControlRespawnHint],
        )

        self.Options = [
            self.SpeedSlider,
            self.AirControlNested,
        ]

    def apply(self, speed=True, air_control=True):
        """Apply the set user-defined values of Speed and AirControl"""
        if speed:
            setSpeed(self.SpeedSlider.CurrentValue)
            self.speed_modified = True
        if air_control and self.AirControlBoolean.CurrentValue is True:
            setAirControl(self.AirControlSlider.CurrentValue / 10)
            self.air_control_modified = True

    def unapply(self, speed=True, air_control=True):
        """Restore normal values of Speed and AirControl"""
        if speed and self.speed_modified:
            setSpeed(self.normal_speed)
            self.speed_modified = False
        if air_control and self.air_control_modified:
            setAirControl(self.normal_air_control)
            self.air_control_modified = False

    def ModOptionChanged(self, option, new_value):
        # Update values if related options changed.
        # If AirControlBoolean changed
        if option == self.AirControlBoolean:
            if new_value is True:
                self.apply(speed=False, air_control=True)
            # If user turned off AirControlBoolean, restore normal Air Control
            else:
                self.unapply(speed=False, air_control=True)
        # If AirControlSlider changed
        elif (option == self.AirControlSlider and
              self.AirControlBoolean.CurrentValue is True):
            setAirControl(new_value / 10)
            self.air_control_modified = True
        # If SpeedSlider changed
        elif option == self.SpeedSlider:
            setSpeed(new_value)
            self.speed_modified = True

    def Enable(self):
        super().Enable()

        # Apply initial speed and air control values
        self.apply()

    def Disable(self):
        # Set speed and air control back to normal
        self.unapply()

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
