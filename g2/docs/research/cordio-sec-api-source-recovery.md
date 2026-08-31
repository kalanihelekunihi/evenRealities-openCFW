# Cordio `sec_api` source recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Disposition

Implemented in maintained source and production-routed; live hardware validation
is blocked by unavailable authorized physical evidence. This closes the former
speculative “first-party Even cryptographic backend” software-gap row. The live
Apollo code is Packetcraft Cordio `sec_api`, not a separately identified Even
cryptographic implementation.

## Identity and boundary

The authenticated G2 image contains the Cordio r20.05c security service at
`[0x00536234,0x005367D2)`. Its behavior and organization match Packetcraft
commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, specifically `sec_main.c`,
`sec_aes.c`, `sec_cmac_hci.c`, and `sec_ecc_hci.c`, under Apache-2.0. The
maintained implementation is
`components/apollo_main/core_overlay/cordio_sec_api.c`.

The source owns the Cordio service layer: random buffering, message queues,
non-`0xff` token allocation, AES request/completion, CMAC subkey/block framing,
ECC public-key/shared-secret byte order, and completion delivery. AES, random,
public-key, and Diffie-Hellman primitives continue through the retained HCI and
controller providers. That is an explicit hardware/controller dependency, not
an unimplemented software backend.

## Authenticated stock surface

The audit authenticates 20 function entries comprising 1,392 stock body bytes.
Three inter-function literal/alignment gaps total 46 bytes, so the full bounded
physical span is 1,438 bytes. Per-entry hashes and the outer physical-span hash
are enforced by `tools/analyze_g2_cordio_sec_api.py`; any boundary or body drift
fails closed.

## Production routing

All 20 entries redirect to isolated Cortex-M55 leaves. The canonical Apple
profile emits 1,952 compiled text bytes plus 16 alignment bytes under 65 strict
relocations. Each leaf is tagged Apache-2.0 in the overlay metadata. Host tests
cover the random ring/refill path, AES queue completion, CMAC shifting, and ECC
byte order/completion; all 20 selectors separately compile freestanding with
`-Wall -Wextra -Werror`.

Canonical artifacts after this closure are:

- overlay: 428,950 bytes, SHA-256
  `0a6b9fe566a2452cd9720c2db22eb43e530c31b76996d05541fa7f24ea9ee745`;
- Apollo component: 3,952,346 bytes, SHA-256
  `dc578472f06af2d499b9cb771fc185df4f739a05de558098088b56da9a5e4ce0`;
- unsigned source package: 4,730,840 bytes, SHA-256
  `d77d88162f777a6c9889d1813323a836d1dc140fe7488009fe485ed787d8fe70`;
- flash plan: 4,299,871 bytes, SHA-256
  `6820a0dc5b6be70fdca78144fdb39d56a9f898b7b0b832c8d76b18cef33608f6`.

The package replay is byte-identical with 6,193 placed and two unresolved
regions. No image was signed, flashed, or installed.

## Validation boundary

Run `make cordio-sec-api-closure`. Live random-command, AES/CMAC/ECC controller
completion, radio concurrency, timing, and paired-temple validation requires a
responsive authorized right G2/EM9305 setup. That evidence is unavailable: the
authorized right temple is nonresponsive and the authorized left must remain
stock. Hardware validation is therefore explicitly
`blocked_unavailable_authorized_physical_evidence`; firmware-wide functional
completeness is not claimed.
