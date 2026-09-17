#!/bin/bash
# Run only inside the disposable Arch build VM, as root.
set -euo pipefail
scripts=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$scripts/.." && pwd)
downloads="$repo/release/jp-downloads"
source_iso="$downloads/omarchy-4.0.4.iso"
build=${OMARCHY_JP_BUILD_DIR:-/var/tmp/omarchy-jp-build}
if (( EUID != 0 )); then
  echo 'Run this script as root inside a disposable Arch Linux build VM.' >&2
  exit 1
fi
if [[ -e $build ]]; then
  echo "Build directory already exists: $build. Select a fresh OMARCHY_JP_BUILD_DIR." >&2
  exit 1
fi
mkdir -p "$build"
printf '%s  %s\n' ddeded2758c48318d201dfdac905ecb28f570441883f0c052ea3cd5d05acf92d "$source_iso" | sha256sum -c -
printf '%s  %s\n' 1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b "$downloads/ggml-small.bin" | sha256sum -c -
xorriso -osirrox on -indev "$source_iso" -extract /arch/x86_64/airootfs.sfs "$build/original.sfs"
unsquashfs -processors 6 -d "$build/root" "$build/original.sfs"
root="$build/root"
mirror="$root/var/cache/omarchy/mirror/offline"
(cd "$mirror" && sha256sum ./*.pkg.tar.zst > "$build/original-packages.sha256")
for pkg in "$mirror/"*.pkg.tar.zst; do pacman -Qp "$pkg"; done > "$build/original-packages.txt"
# Add packages to the existing offline mirror. Resolve existing dependencies
# from that mirror first, so none of the stable ISO packages are upgraded.
pacman-key --add "$repo/builder/omarchy.gpg"
pacman-key --lsign-key 40DFB630FF42BCFFB047046CF0134EE680CAC571
cat > "$build/pacman-jp.conf" <<EOF
[options]
Architecture = auto
SigLevel = Required DatabaseOptional
ParallelDownloads = 5
[offline]
SigLevel = Never
Server = file://$mirror
[core]
Server = https://stable-mirror.omarchy.org/\$repo/os/\$arch
[extra]
Server = https://stable-mirror.omarchy.org/\$repo/os/\$arch
[multilib]
Server = https://stable-mirror.omarchy.org/\$repo/os/\$arch
[omarchy]
Server = https://pkgs.omarchy.org/stable/\$arch
EOF
mkdir -p "$build/db"
printf '%s  %s\n' d6a9b7de8c99a1278c256dc91b2e2b7b2e16c886bef9f0736de6df3678f9b521 "$downloads/voxtype-bin-1.0.1-1-x86_64.pkg.tar.zst" | sha256sum -c -
cp "$downloads/voxtype-bin-1.0.1-1-x86_64.pkg.tar.zst" "$mirror/"
pacman --config "$build/pacman-jp.conf" --dbpath "$build/db" --cachedir "$mirror" -Syw --noconfirm fcitx5-mozc fcitx5-configtool voxtype-bin wtype wl-clipboard noto-fonts-cjk
(cd "$mirror" && sha256sum -c "$build/original-packages.sha256" > "$build/original-packages-verified.log")
repo-add "$mirror/offline.db.tar.gz" "$mirror/"*.pkg.tar.zst > "$build/repo-add.log"
# Record the entire resulting package inventory.
for pkg in "$mirror/"*.pkg.tar.zst; do pacman -Qp "$pkg"; done > "$build/packages.txt"
python - "$build" <<'PYVERIFY'
import sys
from pathlib import Path
root=Path(sys.argv[1])
def versions(name):
    result={}
    for line in (root/name).read_text().splitlines():
        pkg,version=line.split()
        result.setdefault(pkg,set()).add(version)
    return result
before=versions('original-packages.txt');after=versions('packages.txt')
changed={name:(version,after.get(name)) for name,version in before.items() if version != after.get(name)}
assert not changed, f'Stable package versions changed: {changed}'
print(f'Preserved {len(before)} original package versions')
PYVERIFY
grep '^omarchy 4.0.4-1$' "$build/packages.txt"
python "$scripts/configure_iso.py" "$root"
cp "$scripts/jp.py" "$root/usr/share/omarchy-iso/orchestrator/jp.py"
assets="$root/usr/local/share/omarchy-jp"
mkdir -p "$assets/input-method"
cp "$scripts/"{jp_defaults.py,voxtype.service} "$assets/"
cp "$downloads/ggml-small.bin" "$assets/"
cp "$scripts/WHISPER-LICENSE" "$assets/"
# Keep public Git metadata so the standard plugin updater remains usable.
git clone https://github.com/komagata/omarchy-input-method.git "$assets/input-method"
git -C "$assets/input-method" checkout 292ad4b2d90c1f6fddd2cc9aadaf00216f242ac6
cp "$build/packages.txt" "$assets/packages.txt"
printf '%s\n' 'Omarchy Japanese ISO based on official 4.0.4' 'Input Methods v0.1.9 292ad4b2d90c1f6fddd2cc9aadaf00216f242ac6' 'Whisper small 1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b' > "$assets/build-info.txt"
python -m py_compile "$assets/jp_defaults.py" "$root/usr/share/omarchy-iso/orchestrator/jp.py" "$root/usr/share/omarchy-iso/orchestrator/main.py"
mksquashfs "$root" "$build/airootfs.sfs" -comp zstd -Xcompression-level 15 -b 1M -noappend -processors 6 > "$build/mksquashfs.log" 2>&1
(cd "$build" && sha512sum airootfs.sfs > airootfs.sha512)
xorriso -indev "$source_iso" -outdev "$build/omarchy-4.0.4.jp.iso" -boot_image any replay -map "$build/airootfs.sfs" /arch/x86_64/airootfs.sfs -map "$build/airootfs.sha512" /arch/x86_64/airootfs.sha512 -commit
(cd "$build" && sha256sum omarchy-4.0.4.jp.iso > omarchy-4.0.4.jp.iso.sha256)
xorriso -indev "$build/omarchy-4.0.4.jp.iso" -report_el_torito plain -report_system_area plain > "$build/boot-layout.txt" 2>&1
printf '\nJP ISO build complete: %s\n' "$build/omarchy-4.0.4.jp.iso"
