# G2 PT font-CRC production routing

The canonical G2 PT provider now owns the two font-integrity operations in
semantic C. This closes the retained `platform\product_test\product_common.c`
validator dependency that sat below the previously routed board wrappers.

## Authenticated stock semantics

- Validator body: `[0x0058F208,0x0058F486)`, 638 bytes, SHA-256
  `9eb5db1335d59c956064c9537e9edd3adb23760da29fb326453ba18931b4567b`.
- Wrappers: `0x0058F486` loads `0x80100000`; `0x0058F490` loads
  `0x80700000`.
- Valid XIP window: `[0x80000000,0x82000000)`.
- Header read: 70 bytes. Length is little-endian at `0x40`; expected CRC16 is
  little-endian at `0x44`.
- Payload begins at `base + 0x45` and is processed in chunks no larger than
  `0x400` bytes.
- CRC is non-reflected CRC-16/CCITT with polynomial `0x1021`; the first stock
  call passes a null seed and therefore starts at `0xFFFF`, while later chunks
  resume from the prior CRC.
- `base + length + 0x45` must not exceed `0x82000000`. Success returns zero;
  every validation failure returns one.

## Source implementation and evidence

`pt_protocol_board_leaf_candidates.c` implements the validator with bounded
header and 1-KiB stack buffers, explicit overflow checks, XIP acquire/release,
and a source-owned CRC update loop. It makes no call to retained validator
address `0x0058F208` or its Thumb entry `0x0058F209`.

The host fixture covers valid one-byte and 1,025-byte images, both fixed font
routes, invalid lower/upper bases, zero length, length overflow, and CRC
mismatch. The Apple and reviewed Linux-Clang providers both link with zero
writable image bytes. Live XIP arbitration, exact external font contents, and
on-display consequences are **deferred by project direction**.
