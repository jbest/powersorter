import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import powersorter as ps


class RecordingLogger:
    """Stands in for SortLogger (a singleton that writes a CSV) and keeps the rows."""
    def __init__(self):
        self.rows = []

    def log(self, **row):
        self.rows.append(row)


class MoveFileTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.src_dir = root / 'staging'
        self.dest_dir = root / 'web' / 'BRIT0001000'
        self.src_dir.mkdir()
        self.source = self.src_dir / 'BRIT1234.jpg'
        self.source.write_text('new')
        self.logger = RecordingLogger()

    def move(self, **kwargs):
        return ps.move_file(source=self.source, destination_directory=self.dest_dir,
                            filename='BRIT1234.jpg', filetype='web_jpg',
                            sort_logger=self.logger, dry_run=False, username='tester', **kwargs)

    def test_move_to_new_destination_is_logged_as_success(self):
        result = self.move()
        self.assertTrue(result['move_success'])
        self.assertEqual(self.logger.rows[-1]['result'], 'success')
        self.assertFalse(self.source.exists())
        self.assertEqual((self.dest_dir / 'BRIT1234.jpg').read_text(), 'new')

    def test_collision_is_not_moved_and_is_logged_as_fail(self):
        self.dest_dir.mkdir(parents=True)
        (self.dest_dir / 'BRIT1234.jpg').write_text('old')
        result = self.move()
        self.assertFalse(result['move_success'])
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(self.logger.rows[-1]['result'], 'fail')
        self.assertEqual(self.logger.rows[-1]['details'], 'filename exists')
        self.assertTrue(self.source.exists())
        self.assertEqual((self.dest_dir / 'BRIT1234.jpg').read_text(), 'old')

    def test_collision_with_force_overwrite_is_logged_as_success(self):
        self.dest_dir.mkdir(parents=True)
        (self.dest_dir / 'BRIT1234.jpg').write_text('old')
        result = self.move(force_overwrite=True)
        self.assertTrue(result['move_success'])
        self.assertEqual(self.logger.rows[-1]['result'], 'success')
        self.assertEqual(self.logger.rows[-1]['details'], 'duplicate file name - overwritten')
        self.assertEqual((self.dest_dir / 'BRIT1234.jpg').read_text(), 'new')

    def test_dry_run_moves_nothing(self):
        result = ps.move_file(source=self.source, destination_directory=self.dest_dir,
                              filename='BRIT1234.jpg', filetype='web_jpg',
                              sort_logger=self.logger, dry_run=True, username='tester')
        self.assertTrue(result['move_success'])
        self.assertTrue(self.source.exists())
        self.assertFalse(self.dest_dir.exists())
        self.assertEqual(self.logger.rows[-1]['action'], 'DRY_RUN-move')


if __name__ == '__main__':
    unittest.main()
