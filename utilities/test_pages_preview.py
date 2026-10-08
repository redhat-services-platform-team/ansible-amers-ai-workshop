import tempfile
import unittest
from pathlib import Path

from pages_preview import update_site


class PagesPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'site'
        self.main = self.build('main', 'main v1')
        self.preview = self.build('preview', 'PR v1')

    def build(self, name, text):
        root = self.root / name
        root.mkdir()
        (root / 'index.html').write_text(text)
        (root / '_').mkdir()
        (root / '_' / 'style.css').write_text(text)
        return root

    def test_preview_updates_preserve_main_other_previews_and_git(self):
        update_site(self.site, self.main, '3', self.preview)
        update_site(self.site, self.main, '4', self.preview)
        (self.site / '.git').write_text('worktree metadata')
        (self.preview / 'old.html').write_text('stale')
        update_site(self.site, self.main, '3', self.preview)
        (self.preview / 'old.html').unlink()
        (self.preview / 'index.html').write_text('PR v2')
        update_site(self.site, self.main, '3', self.preview)
        self.assertEqual((self.site / 'index.html').read_text(), 'main v1')
        self.assertEqual((self.site / 'previews/pr-3/index.html').read_text(), 'PR v2')
        self.assertEqual((self.site / 'previews/pr-4/index.html').read_text(), 'PR v1')
        self.assertFalse((self.site / 'previews/pr-3/old.html').exists())
        self.assertEqual((self.site / '.git').read_text(), 'worktree metadata')

    def test_main_update_preserves_previews_and_removes_old_root_files(self):
        update_site(self.site, self.main, '3', self.preview)
        (self.site / 'old.html').write_text('stale')
        (self.main / 'index.html').write_text('main v2')
        update_site(self.site, self.main)
        self.assertEqual((self.site / 'index.html').read_text(), 'main v2')
        self.assertFalse((self.site / 'old.html').exists())
        self.assertTrue((self.site / 'previews/pr-3/index.html').exists())
        self.assertTrue((self.site / '.nojekyll').exists())

    def test_cleanup_removes_only_selected_preview_and_is_idempotent(self):
        update_site(self.site, self.main, '3', self.preview)
        update_site(self.site, self.main, '4', self.preview)
        for _ in range(2):
            update_site(self.site, self.main, '3', cleanup=True)
        self.assertFalse((self.site / 'previews/pr-3').exists())
        self.assertTrue((self.site / 'previews/pr-4/index.html').exists())
        self.assertTrue((self.site / 'index.html').exists())

    def test_bad_pr_or_missing_build_leaves_existing_site_unchanged(self):
        update_site(self.site, self.main, '3', self.preview)
        for pr in ('../..', '0', '-1', 'branch/name'):
            with self.assertRaises(ValueError):
                update_site(self.site, self.main, pr, cleanup=True)
        with self.assertRaises(ValueError):
            update_site(self.site, self.root / 'missing', '3', cleanup=True)
        with self.assertRaises(ValueError):
            update_site(self.site, self.main, '3', self.root / 'missing')
        self.assertTrue((self.site / 'previews/pr-3/index.html').exists())


if __name__ == '__main__':
    unittest.main()
