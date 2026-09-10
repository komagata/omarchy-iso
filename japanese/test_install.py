import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import jp

class InstallTest(unittest.TestCase):
    def test_missing_installation_user_is_rejected_before_writes(self):
        with patch.object(jp.shutil, 'copytree') as copy:
            with self.assertRaisesRegex(RuntimeError, 'installation user'):
                jp.configure_jp(SimpleNamespace(username=''))
            copy.assert_not_called()

    def test_only_installer_user_is_configured_and_system_locale_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'etc').mkdir()
            locale = root / 'etc/locale.conf'
            locale.write_text('LANG=en_US.UTF-8\n')
            (root / 'etc/locale.gen').write_text('en_US.UTF-8 UTF-8\n')
            with patch.object(jp.shutil, 'copytree'), patch.object(jp.shutil, 'copy2'), patch.object(jp.subprocess, 'run') as run:
                jp.configure_jp(SimpleNamespace(target=root, username='alice'))
            self.assertEqual(locale.read_text(), 'LANG=en_US.UTF-8\n')
            self.assertIn('ja_JP.UTF-8 UTF-8', (root/'etc/locale.gen').read_text())
            calls = [call.args[0] for call in run.call_args_list]
            self.assertIn(['arch-chroot', str(root), 'runuser', '-u', 'alice', '--', 'python', '/usr/local/share/omarchy-jp/jp_defaults.py', '--user'], calls)
            self.assertFalse(any('systemctl' in command for command in calls))

if __name__ == '__main__':
    unittest.main()
