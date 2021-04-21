# Workaround for pytest, which insists on running __init__.py during the
#  collection phase, such that there is no opportunity to mock things. So the
#  contents of __init__.py got separated into a different module which is
#  loaded here when run ingame, but skipped when run via pytest.

unrealsdk_defined = None

# Check if we’re in the right environment
try:
    import unrealsdk  # noqa: F401
    unrealsdk_defined = True
except ImportError:
    unrealsdk_defined = False

# If so, load and register mod
if unrealsdk_defined is True:
    from Mods.ModMenu import RegisterMod
    from Mods.SavesBackuper.mod import SavesBackuper

    instance = SavesBackuper()
    RegisterMod(instance)
