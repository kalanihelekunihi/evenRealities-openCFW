# Security-audit behavior incorporated into the reconstruction

The compile-tested functional model incorporates the trust-critical behavior established by
[`../r1-bootloader-security-decompilation.md`](../r1-bootloader-security-decompilation.md) and
[`../r1-firmware-security-follow-up.md`](../r1-firmware-security-follow-up.md).

## Retained behavior

- ECDSA-P256/SHA-256 verification is mandatory before version policy.
- Missing, wrong-type, wrong-length, hash-failing, or signature-failing init commands are rejected.
- A signed total bounds DATA object creation; one object is limited to `0x1000` bytes.
- Fragment writes cannot pass the current object or total image size.
- Full staged-image SHA-256 is independently checked before activation.
- Bank codes `0x01`, `0xa5`, `0xaa`, and `0xac` select application, SoftDevice, bootloader, or
  combined SoftDevice/bootloader activation.
- A valid settings backup restores bank, progress, init-command, and validation state over a
  writable primary page.
- Application handoff write-protects `0xf8000...0xfefff` and flash from address zero through the
  page-aligned application end.

The model also preserves the observed fail-open settings case as data behavior: when the primary is
valid and the protected backup is invalid, the primary is accepted wholesale. The documentation
marks this as a conditional storage-fault risk; the tested ring's captured backup is valid and
byte-identical to the security-bearing primary structure.

## Hardened malformed-input behavior

The live image has three bounded-read defects: short BLE control-point operations, an unterminated
nested nanopb varint, and an unchecked 20-byte advertising-name length. The clean model rejects all
three before reading beyond the provided object. This preserves valid protocol behavior without
reproducing memory-unsafety.

## Debug validation and physical debug

The captured bootloader uses Nordic debug-validation behavior, so installed-application CRC is not
meaningfully compared. The SDK overlay keeps that option off by default and exposes only an
explicit research comparison macro. The tested legacy nRF52840 also has physical debug protection
disabled; that manufacturing state is documented but not reproduced as a software bypass.

## MBR boundary

The audit identified unauthenticated MBR copy/vector primitives, but both require state in the
ACL-protected MBR parameter page for persistence. The reconstruction documents and models the ACL
boundary; it does not include a path to remove it, alter the signature gate, or authorize unsigned
updates.
