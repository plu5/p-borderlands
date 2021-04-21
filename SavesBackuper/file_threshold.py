import os

# Non-functional imports (only for type hints)
from re import Pattern
from typing import Union


def deleteMatchingOverThreshold(
        path: str,
        regex: Pattern,
        threshold: int
) -> Union[list, bool]:
    """Check if number of files in 'path' whose name matches 'regex' exceeds
 'threshold', in which case delete oldest ones in order to match it,
 returning either a list of ``DirEntry``s of the files that were deleted, or
 False if no matching over threshold.

Args:
    path: Absolute path of the directory to scan.
    regex: Regular expression object from the ``re`` library, that will be used
        as a filter. Filenames are matched against this regex using the
        ``search`` function.
    threshold: Keeps newest matching files below this threshold.

Returns:
    Either a list of ``DirEntry``s of the files that were deleted, or
    False if no matching over threshold.
"""
    matching = [entry for entry
                in sorted(os.scandir(path),
                          key=lambda e: e.stat().st_ctime, reverse=True)
                if regex.search(entry.name)]

    overdraft = len(matching) - threshold

    if overdraft > 0:
        entries_to_delete = matching[threshold:]
        for entry in entries_to_delete:
            os.remove(entry.path)

        return entries_to_delete

    return False
