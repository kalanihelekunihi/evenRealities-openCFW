# G2 bootloader MSPI control source closure

The executable `am_hal_mspi_control` route at `[0x004251C0,0x0042612C)` is
now production-owned BSD-3-Clause C. It consists of a 124-byte stock-request
ABI adapter at `[0x004251C0,0x0042523C)` and a 3,824-byte maintained
AmbiqSuite Apollo510 body at `[0x0042523C,0x0042612C)`. The adapter implements
the two stock-only SDR250 requests (ordinals 10 and 11) and translates the
remaining stock ordinals to the public AmbiqSuite 5.1.0 request ABI.

This is a functional source replacement, not a claim that the new code is
byte-identical to the entire 4,384-byte stock envelope. Apple Clang 21 emits
provider `909724a6fcc567e737e15641bb9899a7fdf8a138d5cd62e157c651d500156d4a`;
Linux Clang 22.1.8 emits provider
`8f04dc3ae3cb7536c602e0cd71e8f3c1f6105f0d4817ff4c6b8a5feca15dca4c`.
Both profiles produce the same 124-byte adapter and a 3,824-byte adapted body,
with profile-specific reviewed hashes and strict relocation contracts. The
vendored AmbiqSuite source remains unchanged at
`5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`.

The stock 4,384-byte control envelope and all four direct callers remain
authenticated. It is independently cross-checked against the separately
mapped Apollo-main body at `[0x004C0F78,0x004C2098)`: 4,297 bytes match and
87 address-coupled bytes differ in 53 bounded runs. A host-executable semantic
model covers all valid stock requests (`0..39`), low-byte aliases, validation,
register/state changes, queue and sequence transitions, and subordinate
failure propagation.

Retained boundaries remain explicit:

- the 28-byte literal pool at `[0x004251A4,0x004251C0)` is authenticated data;
- the 436 bytes at `[0x0042612C,0x004262E0)` are the unreachable stock tail
  after the compiled adapted body returns;
- `am_hal_mspi_blocking_transfer` at `[0x004262E0,0x0042644C)` is the next
  executable software frontier, followed by four retained alignment bytes and
  the interrupt enable/disable/status entries through `0x00426506`.

Canonical Apple accounting is now 34,019 source-owned bytes and 113,331
retained official bytes. No wider MSPI code-interval or firmware-wide
functional completeness is claimed.

Hardware validation is blocked by unavailable physical evidence. Authorized
qualification must still cover register writes, XIP transitions, timing,
FIFO, interrupt, flash-bus, and cold-boot behavior. This closure performed no
signing, flashing, erasing, reset, MMIO, or device operation.
