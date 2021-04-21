import re
from unittest.mock import patch, call

from SavesBackuper.file_threshold import deleteMatchingOverThreshold


class FakeDirEntry:
    def __init__(self, name, ctime):
        self.name = name
        self.path = name
        self.ctime = ctime

    def stat(self):
        return FakeStat(self.ctime)


class FakeStat:
    def __init__(self, st_ctime):
        self.st_ctime = st_ctime


@patch('os.scandir')
@patch('os.remove')
class TestDeleteMatchingOverThreshold:
    def test_zero_threshold_with_matches(self, m_remove, m_scandir):
        regex = re.compile('^test$')
        mock_entries = [FakeDirEntry('test', 1),
                        FakeDirEntry('notest', 2),
                        FakeDirEntry('test', 2)]
        m_scandir.return_value = iter(mock_entries)

        expected_deleted = [mock_entries[2], mock_entries[0]]
        assert deleteMatchingOverThreshold('', regex, 0) == expected_deleted
        m_remove.assert_has_calls([call(d.path) for d in expected_deleted])

    def test_zero_threshold_no_matches(self, m_remove, m_scandir):
        regex = re.compile('^test$')
        mock_entries = [FakeDirEntry('notest', 1),
                        FakeDirEntry('notest', 2),
                        FakeDirEntry('egg', 2)]
        m_scandir.return_value = iter(mock_entries)

        assert deleteMatchingOverThreshold('', regex, 0) is False
        m_remove.assert_not_called()

    def test_empty_directory(self, m_remove, m_scandir):
        regex = re.compile('^test$')
        m_scandir.return_value = iter([])

        assert deleteMatchingOverThreshold('', regex, 0) is False
        m_remove.assert_not_called()

    def test_two_threshold_three_matches(self, m_remove, m_scandir):
        regex = re.compile('^test$')
        mock_entries = [FakeDirEntry('test', 7),
                        FakeDirEntry('no', 2),
                        FakeDirEntry('test', 1),
                        FakeDirEntry('test', 3)]
        m_scandir.return_value = iter(mock_entries)

        # We expect only the oldest one to be deleted
        expected_deleted = [mock_entries[2]]
        assert deleteMatchingOverThreshold('', regex, 2) == expected_deleted
        m_remove.assert_has_calls([call(d.path) for d in expected_deleted])
