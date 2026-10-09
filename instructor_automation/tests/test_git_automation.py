"""Exercise discovery decisions, password persistence, and remote account creation."""
import importlib.util
import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


discovery = load('discovery', 'roles/workshop_git/library/workshop_git_discovery.py')
passwords = load('passwords', 'roles/workshop_git/library/workshop_git_passwords.py')
remote = load('remote', 'roles/workshop_git/library/workshop_git_users.py')


class DiscoveryTests(unittest.TestCase):
    def test_public_zone_selection_and_override(self):
        zones = [dict(Id='/hostedzone/Z1', Name='lab.example.com.', Config={'PrivateZone': False}),
                 dict(Id='/hostedzone/Z2', Name='private.example.com.', Config={'PrivateZone': True})]
        self.assertEqual(discovery.select_public_zone(zones)['Id'], '/hostedzone/Z1')
        zones.append(dict(Id='Z3', Name='other.example.com.', Config={'PrivateZone': False}))
        with self.assertRaises(ValueError):
            discovery.select_public_zone(zones)
        self.assertEqual(discovery.select_public_zone(zones, zone_name='LAB.EXAMPLE.COM')['Id'], '/hostedzone/Z1')
        with self.assertRaises(ValueError):
            discovery.select_public_zone(zones, zone_id='Z2')
        with self.assertRaises(ValueError):
            discovery.select_public_zone([])

    def test_invalid_networks_are_rejected_before_discovery(self):
        discovery.validate_networks('10.77.0.0/16', '10.77.1.0/24')
        for vpc, subnet in [('10.77.0.0/16', '10.78.0.0/24'),
                            ('10.77.0.0/16', '10.77.1.1/24'),
                            ('10.77.0.0/29', '10.77.0.0/29'),
                            ('2001:db8::/32', '2001:db8::/64')]:
            with self.assertRaises(ValueError):
                discovery.validate_networks(vpc, subnet)

    def test_existing_dns_must_belong_to_the_deployment(self):
        record = {'Name': 'git.lab.example.com.', 'Type': 'A', 'ResourceRecords': [{'Value': '192.0.2.1'}]}
        marker = {'Name': '_workshop-owner.git.lab.example.com.', 'Type': 'TXT',
                  'ResourceRecords': [{'Value': '"workshop/demo-a"'}]}
        with self.assertRaises(ValueError):
            discovery.verify_dns_ownership([record], 'git.lab.example.com', 'workshop/demo-a')
        discovery.verify_dns_ownership([record, marker], 'git.lab.example.com', 'workshop/demo-a')
        with self.assertRaises(ValueError):
            discovery.verify_dns_ownership([record, marker], 'git.lab.example.com', 'another/demo-a')
        with self.assertRaises(ValueError):
            discovery.verify_dns_ownership([dict(record, Type='CNAME'), marker], 'git.lab.example.com', 'workshop/demo-a')


class PasswordTests(unittest.TestCase):
    def test_rerun_reuses_passwords_and_new_student_gets_a_password(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'private' / 'passwords.json'
            changed, initial = passwords.reconcile_passwords(path, ['alice', 'bob'])
            self.assertTrue(changed)
            self.assertNotEqual(initial['alice'], initial['bob'])
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            changed, repeated = passwords.reconcile_passwords(path, ['alice', 'bob'])
            self.assertFalse(changed)
            self.assertEqual(initial, repeated)
            changed, expanded = passwords.reconcile_passwords(path, ['alice', 'bob', 'charlie'])
            self.assertTrue(changed)
            self.assertEqual(initial['alice'], expanded['alice'])
            passwords.reconcile_passwords(path, ['alice'])
            self.assertIn('bob', json.loads(path.read_text()))
            _, renamed = passwords.reconcile_passwords(path, ['ALICE'])
            self.assertEqual(initial['alice'], renamed['ALICE'])

    def test_partial_state_cannot_regenerate_provisioned_passwords(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'passwords.json'
            _, initial = passwords.reconcile_passwords(path, ['alice', 'bob'])
            path.write_text(json.dumps({'bob': initial['bob']}))
            original = path.read_text()
            for check_mode in [False, True]:
                with self.assertRaisesRegex(ValueError, 'previously provisioned'):
                    passwords.reconcile_passwords(path, ['ALICE', 'bob'], check_mode,
                                                  required_students=['alice', 'bob'])
                self.assertEqual(path.read_text(), original)
            changed, expanded = passwords.reconcile_passwords(path, ['bob', 'new'],
                                                             required_students=['bob'])
            self.assertTrue(changed)
            self.assertEqual(expanded['bob'], initial['bob'])
            self.assertIn('new', expanded)

    def test_existing_password_parent_permissions_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o755)
            path = root / 'passwords.json'
            passwords.reconcile_passwords(path, ['alice'])
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o755)
            passwords.reconcile_passwords(path, ['alice', 'bob'])
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o755)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_check_mode_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'private' / 'passwords.json'
            passwords.reconcile_passwords(path, ['alice'], check_mode=True)
            self.assertFalse(path.parent.exists())

    def test_invalid_names_and_symlink_are_rejected(self):
        for students in [[], ['Alice', 'alice'], ['x;echo bad'], ['api'], ['foo..bar'], ['alice.keys']]:
            with self.assertRaises(ValueError):
                passwords.validate_students(students)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'target'
            target.write_text('{}')
            link = Path(directory) / 'link'
            link.symlink_to(target)
            with self.assertRaises(ValueError):
                passwords.reconcile_passwords(link, ['alice'])


class RemoteTests(unittest.TestCase):
    def test_every_missing_student_is_created_and_existing_passwords_are_not_reset(self):
        users = [dict(username=name, email=name + '@example.com', password='secret-' + name,
                      admin=True, must_change_password=True) for name in ['alice', 'bob', 'charlie']]
        run = Mock(return_value='')
        created = remote.create_missing_users(users, {'alice'}, run)
        self.assertEqual(created, ['bob', 'charlie'])
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            self.assertIn('--admin=true', call.args[0])
            self.assertIn('--must-change-password=true', call.args[0])
        self.assertEqual(remote.create_missing_users(users, {'alice', 'bob', 'charlie'}, run), [])
        self.assertEqual(run.call_count, 2)
        self.assertEqual(remote.create_missing_users(users, set(), Mock()), ['alice', 'bob', 'charlie'])

    def test_cli_list_ignores_log_lines(self):
        self.assertEqual(remote.usernames_from_list('2026/10/09 migration complete\nID Username Email\n1 Alice alice@example.com\n2 bob bob@example.com\n'), {'alice', 'bob'})

    def test_check_mode_does_not_create_users(self):
        run = Mock()
        user = dict(username='new', email='new@example.com', password='example', admin=False,
                    must_change_password=True)
        self.assertEqual(remote.create_missing_users([user], set(), run, check_mode=True), ['new'])
        run.assert_not_called()

    def test_existing_username_match_is_exact_and_ignores_case(self):
        run = Mock()
        user = dict(username='ann', email='ann@example.com', password='example', admin=False,
                    must_change_password=True)
        self.assertEqual(remote.create_missing_users([user], {'anna'}, run), ['ann'])
        run.reset_mock()
        self.assertEqual(remote.create_missing_users([dict(user, username='ANN')], {'ann'}, run), [])
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
