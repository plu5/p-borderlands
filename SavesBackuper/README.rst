Saves Backuper
==============

Back up the contents of your saves folder each time you launch the game.

- You can set the number of backups that will be kept, to keep them below a certain threshold.
- You can set which folder to back up and where to back up to.

Open the configuration dialog by pressing C in the mod manager to check status and modify the paths.

Check the menu in Options -> Mods to adjust how many backups to keep, and whether to delete old ones.

`UserFeedback <https://bl-sdk.github.io/mods/UserFeedback/>`_ is required, make sure you remember to install that too.

For installation instructions and other general information, look at the README of the `base directory <https://github.com/plu5/p-borderlands>`_.

Dependencies
------------

- `UserFeedback <https://bl-sdk.github.io/mods/UserFeedback/>`_

Usage
-----

- On first enable, the paths configuration panel will pop up. There are some guesses made on where your SaveData folder might be. Status will tell you whether they are valid. Verify they are the paths you want or modify them as you see fit.
- On subsequent launches, the mod will be enabled automatically and save a backup, and no action is required. The panel will not pop up again unless there is a problem with the paths. You can open it manually by pressing C in the mod manager.
- By default, the number of backups to keep is set to 5. After this number is exceeded, the oldest one will be deleted. You can customise this behaviour in Options -> Mods.

There is pretty good logging in this mod. You can check what’s going on by looking at the console or log (in ``/Binaries/Win32/python-sdk.log``).

Implementation notes
--------------------

This mod is unusual in that it hardly even makes use of ``unrealsdk``. Technically the paths could be set to anything, so you don’t even have to use this backup your saves, you can use this to backup any folder upon launching the game, if you wanted to do that for some reason.

I wanted to be able to get from the game the saves path that is used, but I could only get a relative path. So, at the moment, the path is guessed to be ``C:/Users/{os.getlogin()}/Documents/My Games/Borderlands 2/WillowGame/SaveData``, where ``{os.getlogin()}`` is the user’s Windows username, and if that path does not exist the user is prompted to correct it. There are, of course, many situations where that would not be the correct path, and I am conscious of that.

The backups path is by default set to ``/backups`` child directory under the SaveData folder.

Regardless of validity of guessed paths, upon first launch the user is greeted with the Configuration dialog, so they can review and set the paths as they see fit. After that, the dialog will not pop up again in subsequent launches unless there is a problem with the paths. It can be opened manually in the mod manager by pressing C with the mod selected.

The Configuration dialog was made using the very useful ``UserFeedback`` library.

``backup`` and ``file_threshold`` are two helper modules which do not rely on anything specific to Saves Backuper, and are quite standalone. The former contains the backup logic, and the latter the threshold logic; i.e. the deletion of old backups below a set threshold. This is done in quite a safe manner, as only files that match a certain filter will be deleted. The regex Saves Backuper uses is ``'^' + base_name + r'.*\.zip$'``, where ``base_name`` is the name of the directory backed up. This means that if you for some reason wanted to prevent a certain backup from being deleted, you could rename it to make it not match this regex; like add anything to the beginning of the name, for instance an underscore.

Notable is that the 'backup to' path (``to_path``) (where backups are stored) is allowed to be inside the 'backup' path (``path``) (folder whose contents are backed up). ``backup`` checks for that special case and makes sure to skip any files inside the ``to_path``.

There is also the module ``zip_extra_fields``, which again is quite standalone. ZIP files can contain extra fields to give more information about the files therein. The one I use for Saves Backuper backups is the NTFS Extra Field, which can be used to store creation, modification, and access times. Without this field, only modification time would be stored. You can see more information about ZIP extra fields `here <https://fossies.org/linux/unzip/proginfo/extrafld.txt>`_.

There is pretty good logging in this mod, every major action is reported (as in, you can see what is going on if you check the console / log).

- All set (ready; paths confirmed valid)
- Preparing backup
- Backup success
- Backup failure
- Checking threshold
- If threshold exceeded: what was deleted
- Threshold not exceeded

Testing
-------

There are tests for the ``backup`` and ``file_threshold`` modules. To run them you will need to have the package ``pytest`` installed. To run the tests, simply type ``pytest`` in your terminal while in the root directory.

TODO
----

- Threading to speed up IO 

