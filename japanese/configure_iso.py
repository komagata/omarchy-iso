#!/usr/bin/python
"""Apply the small JP overlay to an extracted, verified Omarchy 4.0.4 ISO."""
from pathlib import Path
import sys

EXTRA_PACKAGES = ('fcitx5-mozc', 'fcitx5-configtool', 'voxtype-bin', 'wtype', 'wl-clipboard', 'noto-fonts-cjk')

def patch_iso(root):
    packages = root / 'usr/share/omarchy-iso/omarchy-base.packages'
    lines = packages.read_text().splitlines()
    for name in EXTRA_PACKAGES:
        if name not in lines:
            lines.append(name)
    packages.write_text('\n'.join(lines) + '\n')
    main = root / 'usr/share/omarchy-iso/orchestrator/main.py'
    text = main.read_text()
    anchor = '        ("Finalizing user",            run_chroot_finalizer),'
    if text.count(anchor) != 1:
        raise ValueError('Unexpected stable ISO installation phase order')
    text = text.replace('from .ui import error, info', 'from .ui import error, info\nfrom .jp import configure_jp')
    main.write_text(text.replace(anchor, anchor + '\n        ("Preparing Japanese input", configure_jp),'))

if __name__ == '__main__':
    patch_iso(Path(sys.argv[1]))
