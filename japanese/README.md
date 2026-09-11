# Omarchy 4.0.3 Japanese ISO

Japanese ISO based on the official Omarchy 4.0.3 ISO. This is not an official Omarchy release.

## Download

- [Download the VM-tested ISO](https://storage.googleapis.com/komagata-omarchy-iso/4.0.3-jp.1/omarchy-4.0.3.jp.iso)
- [SHA-256 checksum](https://storage.googleapis.com/komagata-omarchy-iso/4.0.3-jp.1/omarchy-4.0.3.jp.iso.sha256)

This single-file build uses source commit `190c48482e595e3e76d8afe77503cd46e4871dd6` and applies Japanese settings only to the installation user. After downloading both files to the same directory, verify the ISO:

```sh
sha256sum -c omarchy-4.0.3.jp.iso.sha256
```

## Defaults

- User locale: `ja_JP.UTF-8` for the account created by the installer. The upstream system locale remains unchanged.
- Physical keyboard layout: chosen during installation, independent of the locale.
- Japanese input: Fcitx 5 + Mozc; Ctrl+Space switches input methods.
- Input Methods bar plugin: `komagata.input-method`, v0.1.9 (commit `292ad4b2d90c1f6fddd2cc9aadaf00216f242ac6`).
- Voice input: Voxtype 1.0.1, local multilingual Whisper `small`, language `ja`.
- Model bundled: no API key or first-use download needed.
- Dictation: hold F9, or toggle with Super+Ctrl+X.
- Output: paste mode using Ctrl+Shift+V (terminal paste / browser plain-text paste).

The user locale also selects Japanese translations in applications that supply them. This overlay contains no translation of Omarchy's own shell strings.

## Build

Run the build **inside a disposable Arch Linux VM**, from this repository checkout:

```bash
./japanese/download-assets.sh
sudo ./japanese/build.sh
```

Downloads are stored in `release/jp-downloads` (ignored by Git). The build defaults to `/var/tmp/omarchy-jp-build`; the ISO and checksum are written there. This directory must not already exist. To use another fresh directory, run `sudo env OMARCHY_JP_BUILD_DIR=/path/to/new-build ./japanese/build.sh`.

The build changes the build VM's pacman keyring and extracts a root filesystem, so do not run it on your everyday desktop. The public plugin repository is cloned at its pinned commit, retaining Git metadata for normal plugin updates.

Build dependencies: `squashfs-tools`, `libisoburn`, `git`, `jq`, `python`, `arch-install-scripts`, `pacman` and current Arch signing keys.

Input assets:

| Asset | Source / pinned SHA256 |
|---|---|
| Official ISO | https://iso.omarchy.org/omarchy-4.0.3.iso |
| ISO SHA256 | `03d60bc74306dca51f96e1a84b690871d8d606826b260edd0208962da8507d14` |
| Whisper small | https://huggingface.co/ggerganov/whisper.cpp/resolve/5359861c739e955e79d9a303bcbc70fb988958b1/ggml-small.bin |
| Model SHA256 | `1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b` |
| Voxtype package | https://pkgs.omarchy.org/stable/x86_64/voxtype-bin-1.0.1-1-x86_64.pkg.tar.zst |
| Voxtype SHA256 | `d6a9b7de8c99a1278c256dc91b2e2b7b2e16c886bef9f0736de6df3678f9b521` |
| Plugin | https://github.com/komagata/omarchy-input-method/tree/v0.1.9 |

The original ISO's offline package mirror has priority during dependency resolution. The build verifies that every original package remains byte-for-byte identical, adds the Japanese packages and payload, then recreates the SquashFS and replays the original BIOS/UEFI boot metadata. The original signature does not apply to this modified image; use the accompanying JP SHA256.

Packages and the model are shared system resources; the payload lives at `/usr/local/share/omarchy-jp`. The installer generates the Japanese locale data without changing `/etc/locale.conf`, then initializes only its selected account. There is no boot-time scan of users, and subsequently created accounts receive no JP defaults. Deferred provisioning without an installation user is not supported by this overlay.

The user's language is stored in `~/.config/locale.conf`. A symlink at `~/.config/environment.d/20-omarchy-jp.conf` supplies it to user services, and `~/.config/uwsm/env.d/20-omarchy-jp` loads it for the desktop session. Edit the locale file and log out and back in to change the desktop language. Input method, plugin, and dictation settings remain under the user's `~/.config`. The marker `~/.local/state/omarchy/done/jp-defaults-v1` prevents repeated initialization from overwriting personal choices.

This is a fresh-install change. Previously built ISOs and existing installations retain their former system-wide defaults until separately migrated.

## Tests

```
python -m unittest discover -s japanese -p 'test_*.py'
```

End-to-end verification uses a separate QEMU/KVM VM and a disposable 64GB disk. Test credentials, SSH keys, and audio fixtures belong only to the external test harness and are not included in the ISO.

## Review scope

This branch preserves the official builder and adds an opt-in Japanese ISO build workflow under `japanese`. `configure_iso.py` contains the installer changes: additional offline packages and the Japanese setup phase. `jp.py` installs the system payload; `jp_defaults.py` initializes the installation user once.

The base ISO is pinned to 4.0.3 rather than rebuilding from a moving package channel. A future upstream PR may move these settings into a shared locale/profile mechanism; this branch records the implementation used for the Japanese ISO without choosing that API in advance.

## Validation record

The original Japanese ISO was installed into a fresh QEMU/KVM UEFI VM on 2026-09-09. The desktop locale, automatic Fcitx/Voxtype startup, plugin validation, Mozc conversion (`nihongo` to `日本語`), and Japanese audio recording through a virtual microphone followed by clipboard paste into Foot were verified. Whisper ran locally on CPU, without an API key. All 1,249 original package versions and package file hashes were preserved. The final image also booted to the installer welcome screen in BIOS mode.

On 2026-09-10, commit `fb2a34475105de935dd1f94ddea72641f96c584b` was rebuilt using `japanese/build.sh` from this fork, then installed into another fresh 64GB QEMU/KVM UEFI disk (8 vCPUs, 8GB RAM). The build and ISO checksum check passed. The initial desktop session passed locale, package, service, plugin, Mozc conversion, and local Whisper-to-paste checks. A 5.2-second virtual-microphone recording was transcribed in 3.97 seconds on CPU and pasted into Foot as `水をマレーシアから買わなくてはならないのです。`. After reboot, the Japanese defaults, plugin, and both user services remained active, and the Voxtype configuration hash was unchanged. The test VM used `virtio-vga,edid=off` and a 1280x768 desktop to avoid a QEMU capture issue at its automatically selected width; these display adjustments are not part of the ISO.

Rebuilt artifact SHA256: `66dc188e4db0da7a396b4b81aeed07b44e8b610940dbac2f214ea50e5cccabea` (`omarchy-4.0.3.jp.iso`). Timestamps and package mirror availability mean rebuilding is not guaranteed to produce identical ISO bytes.

On 2026-09-11, source commit `190c48482e595e3e76d8afe77503cd46e4871dd6` was rebuilt and installed from the resulting ISO into a fresh 64GB QEMU/KVM UEFI disk (8 vCPUs, 8GB RAM). Nine automated tests passed. The installer completed, preserving `en_US.UTF-8` for the system and setting `ja_JP.UTF-8` only for the installation user. Mozc converted `nihongo` to `日本語`. The Input Methods plugin validated, and Fcitx and Voxtype started automatically. Local Whisper transcribed a Japanese virtual-microphone recording in 3.91 seconds on CPU and pasted the result into Foot. A second account retained English and received no JP settings. Disk-only boot with the ISO removed and a normal OS reboot both passed. Locale, Voxtype, and shell configuration hashes remained unchanged; Fcitx added comments when saving its profile, with its US keyboard and Mozc selection unchanged.

Current per-user ISO SHA256: `68311f887589a0db5316e689168ec5e9e379f3615c4e510f6622f612437edcf2` (`omarchy-4.0.3.jp.iso`). All 1,249 original package versions and package file hashes were preserved. The completed ISO filesystem was extracted and compared byte-for-byte with the verified build filesystem, and the ISO checksum was rechecked after copying to the host. This checksum supersedes the earlier system-wide build above.

Physical microphones, GPUs, Wi-Fi devices, and other hardware-specific behavior have not been tested. No test credentials, SSH keys, audio fixtures, ISO files, or model binaries are committed.
