# As per the block layouts described in
# https://fossies.org/linux/unzip/proginfo/extrafld.txt

import os
from datetime import datetime


def tobytes(integer: int, num_of_bytes: int) -> bytes:
    """integer to_bytes with little endian"""
    return integer.to_bytes(num_of_bytes, 'little')


def getExtendedTimestampExtraField(file_path: str) -> bytes:
    return b''.join([
        tobytes(0x5455, 2),     # Extended Timestamp Extra Field tag
        tobytes(13, 2),         # TSize: 1+4*3 = 13
        tobytes(7, 1),          # Flags: 00000111 (setting mtime, atime, ctime)
        tobytes(int(os.path.getmtime(file_path)), 4),
        tobytes(int(os.path.getatime(file_path)), 4),
        tobytes(int(os.path.getctime(file_path)), 4)
    ])


def getNTFSExtraField(file_path: str) -> bytes:
    # Dates need to be as 1/10th microseconds from Windows Epoch
    W_EPOCH = datetime(1601, 1, 1)

    def toNTFSFiletime(unix_time):
        return int((datetime.utcfromtimestamp(unix_time) -
                    W_EPOCH).total_seconds() * 10000000)

    mtime = toNTFSFiletime(os.path.getmtime(file_path))
    atime = toNTFSFiletime(os.path.getatime(file_path))
    ctime = toNTFSFiletime(os.path.getctime(file_path))

    return b''.join([
        tobytes(0x000a, 2),     # NTFS Extra Field tag
        tobytes(32, 2),         # TSize: Fixed at 32
        tobytes(0, 4),          # Reserved
        tobytes(1, 2),          # Tag for attribute #1
        tobytes(24, 2),         # Size of attribute #1, fixed at 24
        tobytes(mtime, 8),
        tobytes(atime, 8),
        tobytes(ctime, 8)
    ])
