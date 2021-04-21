import os
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

from .zip_extra_fields import getNTFSExtraField

# Non-functional imports (only for type hints)
from typing import Optional


def isParentPath(parent: str, child: str) -> bool:
    """Return if 'child' path is child of 'parent' path."""
    parent_path = os.path.normpath(parent)
    child_path = os.path.normpath(child)
    try:
        b = parent_path == os.path.commonpath([parent_path, child_path])
    except ValueError:
        return False
    return b


def backup(
        path: str,
        to_path: str,
        output_base_name: Optional[str] = None,
        timestamp_fmt: str = "%Y-%m-%d_%H-%M-%S",
        output_name_fmt: str = "{output_base_name}_{timestamp}.zip"
) -> str:
    """Backup files in 'path' to a zip archive in 'to_path', returning path of
 the resulting archive.

Args:
    path: Absolute path of directory containing files to backup.
    to_path: Absolute path to save the output to.
    output_base_name: Base name that will by default form the first part of
        the name of the resulting archive.
    timestamp_fmt: Formatting for the timestamp that will by default form the
        second part of the name of the resulting archive.
    output_name_fmt: Formatting for the name of the resulting archive. May
        refer to variables {output_base_name} and {timestamp}, and should end
        in the file extension (.zip).

Returns:
    Path of the resulting archive.
    """
    # If 'output_base_name' not provided, set it to the name of the directory
    #  whose files we’re backing up
    if output_base_name is None:
        output_base_name = os.path.basename(path)

    # Variables that may appear in 'output_name_fmt'
    namespace = {
        'output_base_name': output_base_name,
        'timestamp': datetime.now().strftime(timestamp_fmt),
    }

    output_name = output_name_fmt.format(**namespace)
    output_path = f"{to_path}/{output_name}"

    if not os.path.exists(to_path):
        os.makedirs(to_path)

    to_path_is_inside_path = isParentPath(path, to_path)
    print(to_path_is_inside_path)

    with ZipFile(output_path, "x") as zf:
        for root, _, filenames, in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, path)

                # In case 'to_path' is inside 'path': If this is a file inside
                #  'to_path', skip it
                if to_path_is_inside_path and isParentPath(to_path, file_path):
                    continue

                zip_info = ZipInfo.from_file(file_path)
                # Avoid absolute paths within archive
                zip_info.filename = rel_path
                # Preserve timestamp attributes
                zip_info.extra = getNTFSExtraField(file_path)

                data = None
                with open(file_path, 'r+b') as f:
                    data = f.read()

                zf.writestr(zip_info, data, ZIP_DEFLATED)

    return output_path
