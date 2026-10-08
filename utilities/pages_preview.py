#!/usr/bin/env python3
"""Update a combined Pages tree while preserving unrelated PR previews."""

import argparse
import re
import shutil
from pathlib import Path


def remove(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def update_site(site, main, pr=None, preview=None, cleanup=False):
    # Validate before modifying the persistent tree.
    if not (main / 'index.html').is_file():
        raise ValueError('Main build must contain index.html')
    if pr is not None and not re.fullmatch(r'[1-9][0-9]*', pr):
        raise ValueError('PR must be a positive integer')
    if pr is None and (preview is not None or cleanup):
        raise ValueError('Preview changes require a PR number')
    if pr is not None and not cleanup and (preview is None or not (preview / 'index.html').is_file()):
        raise ValueError('Preview build must contain index.html')
    if any((main / name).exists() for name in ('.git', 'previews')):
        raise ValueError('Main build contains a reserved directory')
    site.mkdir(parents=True, exist_ok=True)
    for child in site.iterdir():
        if child.name not in ('.git', 'previews'):
            remove(child)
    shutil.copytree(main, site, dirs_exist_ok=True)
    (site / '.nojekyll').touch()
    if pr is not None:
        target = site / 'previews' / f'pr-{pr}'
        remove(target)
        if not cleanup:
            shutil.copytree(preview, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', required=True, type=Path)
    parser.add_argument('--main', required=True, type=Path)
    parser.add_argument('--pr')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--preview', type=Path)
    group.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    update_site(args.site, args.main, args.pr, args.preview, args.remove)


if __name__ == '__main__':
    main()
