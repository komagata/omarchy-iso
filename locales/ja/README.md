# Japanese profile

`--locale ja` adds Mozc, the Fcitx configuration tool, and CJK fonts. It selects `ja_JP.UTF-8` for the installation user while keeping the physical keyboard selected in the installer. Ctrl+Space switches input methods.

Add `--with-dictation` to configure local Japanese Whisper recognition and paste output. The default runtime supplies F9 hold-to-dictate and Super+Ctrl+X toggle bindings.

## Earlier downloadable prototype

- [Download the 4.0.4 Japanese prototype (7.02 GB)](https://storage.googleapis.com/komagata-omarchy-iso/4.0.4-jp.1/omarchy-4.0.4.jp.iso)
- [SHA-256](https://storage.googleapis.com/komagata-omarchy-iso/4.0.4-jp.1/omarchy-4.0.4.jp.iso.sha256)
- [Prototype source](https://github.com/komagata/omarchy-iso/tree/6cb157a/japanese)

This unofficial image predates the source-based locale-profile implementation. It repacks the released 4.0.4 ISO and includes dictation and the third-party Input Methods plugin by default. It demonstrates the earlier Japanese user experience, not a build or validation of the current branch.

SHA-256: `109ce925e91ea061ab7dfaa40ecebc0b4f70ae134ea008f0739782ececb8e3bc`.

On September 17, 2026, that prototype passed a fresh QEMU/KVM UEFI installation, Mozc conversion, local CPU Whisper-to-paste, installation-user-only locale checks, and a normal reboot with GTK display. All 1,248 original package versions and hashes were preserved. A headless disk boot encountered an unresolved Plymouth timeout. Physical hardware was not tested.
