import os
from unittest.mock import patch

from SavesBackuper.backup import backup


@patch('os.path.exists')
@patch('os.makedirs')
@patch('os.walk')
@patch('SavesBackuper.backup.ZipFile')
@patch('SavesBackuper.backup.ZipInfo')
@patch('SavesBackuper.backup.getNTFSExtraField')
@patch('builtins.open')
class TestBackup:
    def test_return_value(
            self, m_open, m_extrafield, m_zipinfo, m_zipfile, m_walk,
            m_makedirs, m_exists):
        assert backup('path', 'to_path', output_name_fmt="testbackup") ==\
            "to_path/testbackup"

    def test_empty_directory(
            self, m_open, m_extrafield, m_zipinfo, m_zipfile, m_walk,
            m_makedirs, m_exists):
        m_walk.return_value = iter([('path', [], [])])

        assert backup('path', 'to_path', output_name_fmt="testbackup") ==\
            "to_path/testbackup"
        m_open.assert_not_called()
        m_zipfile.writestr.assert_not_called()

    def test_one_file(
            self, m_open, m_extrafield, m_zipinfo, m_zipfile, m_walk,
            m_makedirs, m_exists):
        m_walk.return_value = iter([('path', [], ['file1'])])

        assert backup('path', 'to_path', output_name_fmt="testbackup") ==\
            "to_path/testbackup"
        m_open.assert_called_once_with(os.path.join('path', 'file1'), 'r+b')
        m_writestr = m_zipfile.return_value.__enter__.return_value.writestr
        m_writestr.assert_called_once()

    def test_to_path_inside_path(
            self, m_open, m_extrafield, m_zipinfo, m_zipfile, m_walk,
            m_makedirs, m_exists):
        m_walk.return_value = iter([('path', ['to_path'], ['file1']),
                                    ('path/to_path', [], ['file2'])])

        assert backup('path', 'path/to_path', output_name_fmt="testbackup") ==\
            "path/to_path/testbackup"
        m_open.assert_called_once_with(os.path.join('path', 'file1'), 'r+b')
        m_writestr = m_zipfile.return_value.__enter__.return_value.writestr
        m_writestr.assert_called_once()
