import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import powersorter as ps


def compiled_patterns(config_name='BRIT_v3.json'):
    with open(ROOT / 'config' / config_name) as fh:
        config = json.load(fh)
    catalog = config['collection']['catalog_number_regex']
    return {name: re.compile(ps.build_regex(catalog, ft['file_regex']))
            for name, ft in config['file_types'].items()}


class BuildRegexTests(unittest.TestCase):
    def setUp(self):
        self.patterns = compiled_patterns()

    def matching_types(self, filename):
        return [name for name, rx in self.patterns.items() if rx.match(filename)]

    def test_expected_file_names_match_one_file_type(self):
        cases = {'BRIT1234.jpg': 'web_jpg', 'BRIT1234.JPG': 'web_jpg', 'BRIT1234.jpeg': 'web_jpg',
                 'BRIT1234_a.jpg': 'web_jpg', 'BRIT1234_med.jpg': 'web_jpg_med',
                 'BRIT1234_thumb.jpg': 'web_jpg_thumb', 'BRIT1234.dng': 'archive_dng',
                 'BRIT1234_ocr.txt': 'ocr', 'BRIT1234_ocr.json': 'ocr'}
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(self.matching_types(filename), [expected])

    def test_trailing_text_after_the_extension_does_not_match(self):
        for filename in ('BRIT1234.jpgx', 'BRIT1234.jpg.bak', 'BRIT1234.jpg~', 'BRIT1234.jpg ',
                         'BRIT1234.jpg\n', 'BRIT1234_med.jpg.bak', 'BRIT1234_thumb.jpgx',
                         'BRIT1234.dng.tmp', 'BRIT1234_ocr.txt.old', 'BRIT1234.jpg.jpg'):
            with self.subTest(filename=filename):
                self.assertEqual(self.matching_types(filename), [])

    def test_named_groups_are_still_captured(self):
        m = self.patterns['web_jpg'].match('BRIT1234_a.JPG')
        self.assertEqual((m['catNum'], m['numerical'], m['suffix'], m['ext']),
                         ('BRIT1234', '1234', 'a', 'JPG'))
        self.assertEqual(self.patterns['web_jpg_med'].match('BRIT7_med.jpg')['size'], 'med')

    def test_inline_case_flag_in_a_config_is_still_removed(self):
        rx = re.compile(ps.build_regex(r'(?P<catNum>(?P<numerical>\d+))', r'(\.)(?i)(?P<ext>jpg)'))
        self.assertTrue(rx.match('12.JPG'))
        self.assertFalse(rx.match('12.JPG.bak'))

    def test_top_level_alternation_in_file_regex_stays_anchored_to_the_catalog_number(self):
        rx = re.compile(ps.build_regex(r'(?P<catNum>(?P<numerical>\d+))', r'\.jpg|\.png'))
        self.assertTrue(rx.match('12.png'))
        self.assertFalse(rx.match('.png'))
        self.assertFalse(rx.match('12.png.bak'))


class ScanFilesTests(unittest.TestCase):
    def test_scan_skips_backup_and_partial_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('BRIT1.jpg', 'BRIT1.jpg.bak', 'BRIT2.jpgx', 'BRIT3.JPG'):
                (Path(tmp) / name).write_text('x')
            sub = Path(tmp) / 'nested'
            sub.mkdir()
            (sub / 'BRIT4.jpg').write_text('x')
            (sub / 'BRIT4.jpg.bak').write_text('x')
            pattern = compiled_patterns()['web_jpg'].pattern
            found = sorted(Path(m['file_path']).name for m in
                           ps.scan_files(path=tmp, pattern=pattern, file_type='web_jpg'))
        self.assertEqual(found, ['BRIT1.jpg', 'BRIT3.JPG', 'BRIT4.jpg'])


if __name__ == '__main__':
    unittest.main()
