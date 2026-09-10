"""Install JP defaults without changing the signed upstream runtime packages."""
from pathlib import Path
import shutil
import subprocess

def configure_jp(ctx):
    source = Path('/usr/local/share/omarchy-jp')
    dest = ctx.target / 'usr/local/share/omarchy-jp'
    shutil.copytree(source, dest, dirs_exist_ok=True)
    units = ctx.target / 'etc/systemd'
    (units / 'user').mkdir(parents=True, exist_ok=True)
    (units / 'system').mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / 'voxtype.service', units / 'user/voxtype.service')
    shutil.copy2(source / 'omarchy-jp-defaults.service', units / 'system/omarchy-jp-defaults.service')
    locale_gen = ctx.target / 'etc/locale.gen'
    lines = locale_gen.read_text().splitlines()
    if 'ja_JP.UTF-8 UTF-8' not in lines:
        lines.append('ja_JP.UTF-8 UTF-8')
    locale_gen.write_text('\n'.join(lines) + '\n')
    subprocess.run(['arch-chroot', str(ctx.target), 'locale-gen'], check=True)
    (ctx.target / 'etc/locale.conf').write_text('LANG=ja_JP.UTF-8\n')
    subprocess.run(['arch-chroot', str(ctx.target), 'systemctl', 'enable', 'omarchy-jp-defaults.service'], check=True)
    subprocess.run(['arch-chroot', str(ctx.target), 'python', '/usr/local/share/omarchy-jp/jp_defaults.py'], check=True)
