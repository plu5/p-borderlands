import os
from unrealsdk import Log
from Mods import UserFeedback
from Mods.ModMenu import SaveModSettings

# Non-functional imports (only for type hints)
from Mods.ModMenu import SDKMod
from typing import Union, Callable


def pathExists(path: str) -> bool:
    return os.path.exists(path)


def parentPathExists(path: str) -> bool:
    parent_path = os.path.dirname(path)
    return pathExists(parent_path)


class Button(UserFeedback.OptionBoxButton):
    pass


class Configuration(UserFeedback.OptionBox):
    """Configuration dialog"""
    def __init__(self, mod: SDKMod) -> None:
        self.mod = mod
        self.all_set = False

        guessed_path = self.guessSaveDataPath()
        COULD_NOT_GUESS = "COULD NOT GUESS PATH"

        self.save_data_path = guessed_path or COULD_NOT_GUESS
        self.backup_to_path = (guessed_path + "/backups"
                               if guessed_path else COULD_NOT_GUESS)

        save_data_info = ("SaveData path (folder to back up)",
                          self.save_data_path)
        backup_to_info = ("Backup to path (folder to save backups to)",
                          self.backup_to_path)

        self.SaveDataPathInput = PathInput(*save_data_info,
                                           self.updateSaveDataPath)
        self.BackupToPathInput = PathInput(*backup_to_info,
                                           self.updateBackupToPath)

        self.SaveDataPathButton = Button(*save_data_info)
        self.BackupToPathButton = Button(*backup_to_info)

        self.Status = Button("Status", "")

        super().__init__(
            Title=f"{mod.Name} Configuration",
            Buttons=[
                self.Status,
                self.SaveDataPathButton,
                self.BackupToPathButton,
            ],
        )

    def guessSaveDataPath(self) -> Union[str, bool]:
        """Tries the usual Windows path for Borderlands 2 SaveData and returns
 it if it exists, or False if it does not exist."""
        # This is bad, but I failed to find a way to get the proper path out of
        #  the game (the FilePath you can get out of LoadInfo and other objects
        #  is relative). and the reason for not using os.path.join is
        #  TextInputBox doesn’t like backslashes.
        # User can change this path anyway.
        path = f"C:/Users/{os.getlogin()}/Documents/My Games/Borderlands 2/\
WillowGame/SaveData"
        if pathExists(path):
            return path
        else:
            return False

    def updateStatus(self):
        """Updates Status depending on validity of paths, notifying user what
 still needs correcting in order for backups to be saved."""
        need_correcting = []
        validities_str = ""
        summary_str = ""

        meta_validities = {'SaveData path': pathExists(self.save_data_path),
                           'Backup to path':
                           parentPathExists(self.backup_to_path)}

        for caption, valid in meta_validities.items():
            if not valid:
                need_correcting.append(caption)

            status = 'Valid' if valid else 'Invalid'

            if validities_str:
                validities_str += f"   |   {caption}: {status}"
            else:
                validities_str = f"{caption}: {status}"

        if not need_correcting:
            summary_str = "All’s well, backups will be saved when this menu\
 closes and on every subsequent game launch while mod is enabled. To see this\
 menu again, press C in the mod manager while this mod is selected."
            self.all_set = True
            Log(f"[{self.mod.Name}] All set")
        else:
            summary_str = f"Backups will not be saved until you correct the\
 {need_correcting[0]}"
            if len(need_correcting) == 2:
                summary_str += f" and the {need_correcting[1]}."
            else:
                summary_str += "."

        self.Status.Tip = f"{validities_str}\n\n{summary_str}"

    def Show(self) -> None:
        # Make sure paths are up to date to current values on the mod
        self._updateOwnSaveDataPathVars(self.mod.SaveDataPath.CurrentValue)
        self._updateOwnBackupToPathVars(self.mod.BackupToPath.CurrentValue)

        # Update status string
        self.updateStatus()

        super().Show()

    def OnPress(self, button: Button) -> None:
        """Show the path-editing dialogs when the corresponding buttons are
 pressed. When the Status button is pressed, do not hide the configuration
 dialog (it is informational only and does not do anything when pressed)."""
        if button == self.SaveDataPathButton:
            self.SaveDataPathInput.Show()
        elif button == self.BackupToPathButton:
            self.BackupToPathInput.Show()
        # Do not hide when Status button is pressed
        else:
            self.Show()

    def _updateOwnSaveDataPathVars(self, new_path: str) -> None:
        self.save_data_path = new_path
        self.SaveDataPathInput.DefaultMessage = new_path
        self.SaveDataPathButton.Tip = new_path

    def _updateOwnBackupToPathVars(self, new_path: str) -> None:
        self.backup_to_path = new_path
        self.BackupToPathInput.DefaultMessage = new_path
        self.BackupToPathButton.Tip = new_path

    def updateSaveDataPath(self, new_path: str) -> None:
        """If new_path is valid, update all corresponding variables and show
 success dialog. Otherwise, show error dialog."""
        if pathExists(new_path):
            self._updateOwnSaveDataPathVars(new_path)
            Success(f"SaveData path updated to '{new_path}'", self).Show()
            self.mod.SaveDataPath.CurrentValue = new_path
            SaveModSettings(self.mod)
        else:
            Error(
                f"Could not find path '{new_path}'\n\n\
Path was not updated. Please try again.", self).Show()

    def updateBackupToPath(self, new_path: str) -> None:
        """Same as updateSaveDataPath, but for backup to path."""
        if parentPathExists(new_path):
            self._updateOwnBackupToPathVars(new_path)
            Success(f"Backup to path updated to '{new_path}'", self).Show()
            self.mod.BackupToPath.CurrentValue = new_path
            SaveModSettings(self.mod)
        else:
            Error(
                f"Could not find parent path of '{new_path}'\n\n\
Path was not updated. Please try again.", self).Show()

    def OnCancel(self) -> None:
        """When the configuration dialog is closed, if everything is set
 correctly, set configuration to no longer pop up on startup, and attempt
 backup."""
        if self.all_set:
            self.mod.ShowConfigOnStartup.CurrentValue = False
            SaveModSettings(self.mod)
            self.mod.attemptBackup()


class PathInput(UserFeedback.TextInputBox):
    """Path editing dialog"""
    def __init__(self, Title: str, DefaultMessage: str,
                 submit_function: Callable) -> None:
        super().__init__(Title, DefaultMessage)
        self.submit_function = submit_function

    def OnSubmit(self, Message: str):
        self.submit_function(Message)


class Error(UserFeedback.TrainingBox):
    """Error dialog"""
    def __init__(self, Message: str, config: Configuration) -> None:
        super().__init__(f"{config.mod.Name}: Error", Message)
        self.config = config

    def OnExit(self) -> None:
        self.config.Show()


class Success(UserFeedback.TrainingBox):
    """Success dialog"""
    def __init__(self, Message: str, config: Configuration) -> None:
        super().__init__(f"{config.mod.Name}: Success", Message)
        self.config = config

    def OnExit(self) -> None:
        self.config.Show()
