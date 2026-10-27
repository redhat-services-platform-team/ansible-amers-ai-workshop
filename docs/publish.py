#!/usr/bin/env python3
"""Merge a checked documentation build into the shared gh-pages store."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def branch_directory(branch):
    # Reserve '~' for encoded names so transformed names cannot collide with
    # ordinary branch names. Keep common names such as rh1 readable.
    if re.fullmatch(r'[A-Za-z0-9_-]+', branch) and len(branch) <= 100:
        return branch
    slug = re.sub(r'[^A-Za-z0-9_-]', '-', branch)[:80]
    return slug + '~' + hashlib.sha256(branch.encode()).hexdigest()[:16]


def remove(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def merge_site(store, build, branch, delete=False):
    if branch == 'main':
        if delete:
            return
        for path in store.iterdir():
            if path.name not in {'.git', 'branches', 'CNAME'}:
                remove(path)
        shutil.copytree(build, store, dirs_exist_ok=True)
    else:
        target = store / 'branches' / branch_directory(branch)
        if target.exists():
            remove(target)
        if not delete:
            shutil.copytree(build, target)
    (store / '.nojekyll').touch()


def main():
    branch = os.environ['PAGES_BRANCH']
    delete = os.environ.get('PAGES_DELETE') == 'true'
    if branch == 'gh-pages':
        raise SystemExit('gh-pages is reserved for generated documentation')
    store = Path('.pages-state')
    output = Path('.pages-site')
    if git('ls-remote', '--heads', 'origin', 'refs/heads/gh-pages'):
        git('fetch', 'origin', 'refs/heads/gh-pages')
        git('worktree', 'add', '--detach', str(store), 'FETCH_HEAD')
    else:
        git('worktree', 'add', '--detach', str(store), 'HEAD')
        git('-C', str(store), 'checkout', '--orphan', 'pages-initial')
        for path in store.iterdir():
            if path.name != '.git':
                remove(path)
    # A queued build must not resurrect a deleted branch or overwrite a newer
    # commit. Deletion events likewise must not remove a recreated branch.
    remote = git('ls-remote', '--heads', 'origin', 'refs/heads/' + branch)
    current = remote.split()[0] if remote else None
    if (delete and current is None) or (not delete and current == git('rev-parse', 'HEAD')):
        merge_site(store, Path('www'), branch, delete)
    else:
        print('Branch changed since this run started; retaining published content.')
    git('-C', str(store), 'config', 'user.name', 'github-actions[bot]')
    git('-C', str(store), 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('-C', str(store), 'add', '--all')
    if git('-C', str(store), 'diff', '--cached', '--name-only'):
        git('-C', str(store), 'commit', '-m', 'Update workshop documentation')
        git('-C', str(store), 'push', 'origin', 'HEAD:refs/heads/gh-pages')
    shutil.copytree(store, output, ignore=shutil.ignore_patterns('.git'))
    suffix = '' if branch == 'main' else 'branches/' + branch_directory(branch) + '/'
    repository = os.environ.get('GITHUB_REPOSITORY', '')
    if repository:
        owner, name = repository.split('/')
        url = f'https://{owner}.github.io/{name}/{suffix}'
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write(f'Branch preview {"removed" if delete else "path"}: {url}\n')


if __name__ == '__main__':
    main()
