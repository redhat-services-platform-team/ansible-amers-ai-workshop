#!/usr/bin/env python3
"""Regression checks for preserving independent branch publications."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from publish import branch_directory, merge_site


class PublicationTests(unittest.TestCase):
    def test_branch_lifecycle(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store, build = root / 'store', root / 'build'
            store.mkdir()
            build.mkdir()
            (build / 'index.html').write_text('main v1')
            merge_site(store, build, 'main')
            (build / 'index.html').write_text('rh1 v1')
            merge_site(store, build, 'rh1')
            (build / 'index.html').write_text('dev v1')
            merge_site(store, build, 'dev')
            (store / 'obsolete.html').touch()
            (build / 'index.html').write_text('main v2')
            merge_site(store, build, 'main')
            self.assertFalse((store / 'obsolete.html').exists())
            self.assertEqual((store / 'index.html').read_text(), 'main v2')
            self.assertEqual((store / 'branches/rh1/index.html').read_text(), 'rh1 v1')
            self.assertEqual((store / 'branches/dev/index.html').read_text(), 'dev v1')
            merge_site(store, build, 'rh1', delete=True)
            merge_site(store, build, 'rh1', delete=True)
            self.assertFalse((store / 'branches/rh1').exists())
            self.assertTrue((store / 'branches/dev/index.html').exists())
            merge_site(store, build, 'main', delete=True)
            self.assertEqual((store / 'index.html').read_text(), 'main v2')

    def test_names_are_safe_and_distinct(self):
        names = ['rh1', 'feature/docs', 'feature-docs', 'Feature/docs', '../escape', 'é', 'a' * 200]
        directories = [branch_directory(name) for name in names]
        self.assertEqual(directories[0], 'rh1')
        self.assertEqual(len(set(directories)), len(names))
        for directory in directories:
            self.assertNotIn('/', directory)
            self.assertNotIn('..', directory)
            self.assertLess(len(directory), 256)


if __name__ == '__main__':
    unittest.main()
