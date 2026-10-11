# CW221X reference source

This directory is evidence only. Its GPL-2.0 source is not compiled into the
CASE candidate.

- Repository: <https://github.com/rockchip-linux/kernel>
- Branch observed: `develop-6.1`
- Immutable commit: `77168c8d5ab82399f65a80e9f807b50ba37cf483`
- Source path: `drivers/power/supply/cw221x_battery.c`
- Source SHA-256: `e647e42f29a29b7d3ed7bcfe066b5789cb222710603c3178875c4cac4aacda07`
- License: `GPL-2.0` SPDX declaration in the source; kernel `COPYING` retained here,
  SHA-256 `fb5a425bd3b3cd6071a3a9aff9909a859e7c1158d54d32e07658398cd67eb6a0`.
- Retrieval: pinned raw GitHub content at this commit. Full kernel repository
  checkout was unnecessary for this one-file source correlation.

The source defines CW221X chip ID `0xa0` in register `0`, battery profile base
`0x10` and length `80`, mode register `8`, update flag in register `0x0b`, and
ready bits in register `0xa7`. These independently corroborate the CASE native
fuel-gauge control flow and typed RAM table. Its example 80-byte profile
matches only 25 CASE positions and differs from the first byte onward. It does
not supply the CASE board's battery-specific profile values. The CASE values
remain a genuine product-data contract; this source is not a replacement.
