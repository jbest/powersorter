import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import url_gen

URL_BASE = 'https://web.corral.tacc.utexas.edu/torch/'
ROOT = '/corral-repl/projects/TORCH/web'


class GenerateUrlTests(unittest.TestCase):
    def url(self, web_base, coll='BRIT', folder='BRIT0001000', name='BRIT1234.jpg'):
        return url_gen.generate_url(file_base_path=web_base,
                                    file_path=f'{ROOT}/{coll}/{folder}/{name}',
                                    url_base=URL_BASE)

    def test_web_base_forms_all_give_the_same_url(self):
        expected = URL_BASE + 'BRIT/BRIT0001000/BRIT1234.jpg'
        for web_base in (ROOT + '/',            # web root, trailing slash (BRIT_v3)
                         ROOT,                  # web root, no slash
                         ROOT + '/BRIT',        # collection dir, no slash
                         ROOT + '/BRIT/',       # collection dir, trailing slash (HSU, BRIT_v3_TACC)
                         ROOT + '/BRIT//',
                         ROOT + '//'):
            with self.subTest(web_base=web_base):
                self.assertEqual(self.url(web_base), expected)

    def test_hsu_style_config(self):
        self.assertEqual(
            self.url(ROOT + '/HSU/', coll='HSU', folder='HSU0001000', name='HSU1.jpg'),
            URL_BASE + 'HSU/HSU0001000/HSU1.jpg')

    def test_prefix_with_hyphen(self):
        self.assertEqual(
            self.url(ROOT + '/WBU', coll='WBU', folder='WBU-V-00000', name='WBU-V-00001_med.jpg'),
            URL_BASE + 'WBU/WBU-V-00000/WBU-V-00001_med.jpg')


if __name__ == '__main__':
    unittest.main()
