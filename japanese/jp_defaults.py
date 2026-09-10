#!/usr/bin/python
"""Seed the Japanese ISO settings once per user, before the first desktop login."""
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys

ASSETS = Path('/usr/local/share/omarchy-jp')

def write(home, relative, text):
    path = home / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

def configure_user(home, layout):
    marker = home / '.local/state/omarchy/done/jp-defaults-v1'
    if marker.exists():
        return False
    write(home, '.config/fcitx5/profile', f'''[Groups/0]
Name=Default
Default Layout={layout}
DefaultIM=mozc

[Groups/0/Items/0]
Name=keyboard-{layout}
Layout=

[Groups/0/Items/1]
Name=mozc
Layout=

[GroupOrder]
0=Default
''')
    config_path = home / '.config/omarchy/shell.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {'version': 1, 'bar': {'layout': {'right': []}}}
    widgets = config['bar']['layout']['right']
    if not any(w.get('id') == 'komagata.input-method' for w in widgets):
        widgets.insert(0, {'id': 'komagata.input-method'})
    write(home, '.config/omarchy/shell.json', json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    write(home, '.local/state/omarchy/done/jp-defaults-v1', '')
    return True

def main():
    if sys.argv[1:] == ['--user']:
        home = Path.home()
        if (home / '.local/state/omarchy/done/jp-defaults-v1').exists():
            return
        # X11 layout is set by the installer independently from the locale.
        layout = 'us'
        xkb = Path('/etc/X11/xorg.conf.d/00-keyboard.conf')
        if xkb.exists():
            import re
            match = re.search(r'Option\s+"XkbLayout"\s+"([a-z0-9_-]+)"', xkb.read_text())
            if match:
                layout = match[1]
        else:
            vconsole = Path('/etc/vconsole.conf')
            if vconsole.exists() and 'jp' in vconsole.read_text():
                layout = 'jp'
        plugin = home / '.config/omarchy/plugins/komagata.input-method'
        shutil.copytree(ASSETS / 'input-method', plugin, dirs_exist_ok=True)
        configure_user(home, layout)
        return
    if os.geteuid() != 0:
        raise SystemExit('Run as root, or pass --user for the current account.')
    for user in pwd.getpwall():
        if 1000 <= user.pw_uid < 65534 and Path(user.pw_dir).is_dir():
            subprocess.run(['runuser', '-u', user.pw_name, '--', '/usr/bin/python', __file__, '--user'], check=True)

if __name__ == '__main__':
    main()
