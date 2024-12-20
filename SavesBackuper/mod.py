import os
import re
from unrealsdk import Log
from Mods.ModMenu import Options, SDKMod, ModTypes, EnabledSaveType

from Mods.SavesBackuper.configuration import Configuration
from Mods.SavesBackuper.backup import backup
from Mods.SavesBackuper.file_threshold import deleteMatchingOverThreshold


class Label(Options.Field):
    def __init__(self, Caption: str, Description: str = "",
                 IsHidden: bool = False) -> None:
        self.Caption = Caption
        self.Description = Description
        self.IsHidden = IsHidden


class SavesBackuper(SDKMod):
    Name = "Saves Backuper"
    Author = "plu5"
    Version = "1.0"
    Types = ModTypes.Utility
    Description = """Back up the contents of your saves folder each time you\
 launch the game. You can set the number of backups that will be kept. You can\
 set which folder to back up and where to back up to.

Open the configuration dialog by pressing C to check status and modify the\
 paths.

Check the menu in Options -> Mods to adjust how many backups to keep, and\
 whether to delete old ones."""
    SaveEnabledState = EnabledSaveType.LoadWithSettings

    SettingsInputs = SDKMod.SettingsInputs.copy()
    SettingsInputs["C"] = "Configure"

    def __init__(self) -> None:
        super().__init__()

        self.PathsInfo = Label(
            Caption="Paths Info",
            Description="In the mod manager, select the mod and press C to\
 open the paths configuration dialog.",
        )

        thresholdslider_caption = "Number of Backups"

        self.ThresholdBoolean = Options.Boolean(
            Caption="Delete Old Backups",
            Description=f"Whether to delete old backups below\
 '{thresholdslider_caption}', or keep accumulating an infinite amount.",
            StartingValue=True,
            Choices=["No", "Yes"]  # False, True
        )

        self.ThresholdSlider = Options.Slider(
            Caption=thresholdslider_caption,
            Description=f"The number of backups to keep. Ignored if\
 '{self.ThresholdBoolean.Caption}' is set to\
 '{self.ThresholdBoolean.Choices[0]}'.",
            StartingValue=5,
            MinValue=1,
            MaxValue=50,
            Increment=1
        )

        self.config = Configuration(self)

        self.ShowConfigOnStartup = Options.Hidden(
            Caption="Show Config on Startup",
            StartingValue=True,
        )

        self.SaveDataPath = Options.Hidden(
            Caption="SaveData path",
            StartingValue=self.config.save_data_path,
        )

        self.BackupToPath = Options.Hidden(
            Caption="Backup to path",
            StartingValue=self.config.backup_to_path,
        )

        self.Options = [
            self.SaveDataPath,
            self.BackupToPath,
            self.ShowConfigOnStartup,
            self.ThresholdSlider,
            self.ThresholdBoolean,
            self.PathsInfo,
        ]

    def Enable(self) -> None:
        super().Enable()

        self.config.init()

        # Optionally display config dialog
        if (
            self.config.all_set is False or
            self.ShowConfigOnStartup.CurrentValue is True
        ):
            self.config.Show()
        # Or, if paths are already set correctly, attempt backup
        elif self.config.all_set is True:
            self.attemptBackup()

    def SettingsInputPressed(self, action) -> None:
        if action == "Configure":
            self.config.Show()
        else:
            super().SettingsInputPressed(action)

    def attemptBackup(self) -> None:
        Log(f"[{self.Name}] Preparing backup...")
        try:
            path = self.SaveDataPath.CurrentValue
            to_path = self.BackupToPath.CurrentValue
            base_name = os.path.basename(path)

            output_path = backup(path, to_path, base_name)
            Log(f"[{self.Name}] Backup successful! Saved to {output_path}")
        except Exception as e:
            Log(f"[{self.Name}] Backup failed!")
            raise e
        else:
            if self.ThresholdBoolean.CurrentValue is True:
                self.stayBelowThreshold(to_path, base_name)

    def stayBelowThreshold(self, path: str, base_name: str) -> None:
        Log(f"[{self.Name}] Checking if number of backups exceeded\
 threshold...")
        threshold = self.ThresholdSlider.CurrentValue
        regex = re.compile('^' + base_name + r'.*\.zip$')

        deleted_entries = deleteMatchingOverThreshold(path, regex, threshold)
        if deleted_entries:
            num_deleted_entries = len(deleted_entries)
            s = 's' if num_deleted_entries > 1 else ''
            Log(f"[{self.Name}] Deleted {num_deleted_entries} old backup{s}\
 in order to maintain {threshold} threshold.", "\n",
                f"Deleted files: {[entry.name for entry in deleted_entries]}",
                "\n",
                f"If this was undesired, configure {self.Name} options to\
 change this behaviour.")
        elif deleted_entries is False:
            Log(f"[{self.Name}] Threshold not exceeded; no action taken.")
