# G2 bootloader address-identified registered runtime-callback adapter source closure

Status: software implemented and production-routed; physical validation blocked.

Superseded as the current frontier by
`g2-bootloader-runtime-register-4163b2-source-closure.md`; the evidence below
remains the pinned callback-adapter checkpoint.

The complete 24-byte entry `[0x0041639A,0x004163B2)` has SHA-256
`17d06f6db0e1d0bded2fd9f0bb6742fbb1a933eb67061eb9c4cb7079545f596b`.
It has no direct `BL` caller, so routing required an explicit stored-pointer
ingress audit. The stock image contains exactly one Thumb entry literal,
`0x0041639B`, at `0x004169A0`. PC-relative loads at `0x00416452` and
`0x0041646A` pass that literal as the registered callback to retained backends
`0x004192DE` and `0x004192A8`. This authenticates two real registration paths
rather than treating the no-direct-call topology as dead code.

At invocation the adapter passes its owner argument to retained provider
`0x004196C2`, clears the low flag bit of the returned callback-record address,
returns when the resulting address is null, and otherwise invokes the function
word at offset zero with the argument word at offset four. Address-derived
names avoid unsupported claims about the retained runtime object's type.

`runtime_callback_41639a.c` is a 1,118-byte MIT clean-room
implementation with SHA-256
`15e3c18b56001b6936345c1f7516b4363a337e4e74440f615e34ff55931045fa`.
Apple clang emits a 24-byte, two-byte-aligned unrelocated leaf with SHA-256
`a42d83c170e27cb80bb90e2efc297cad160fa5a0dea7f0a145b15709f0a621d2`.
At overlay offset 3,742/runtime `0x00435316`, its strict call at offset two
produces relocated SHA-256
`7bfc008d49acd9aa557c0daaa1d99ead58ce7fc89af50ed4a4e108f6e0329449`.
Homebrew clang 22.1.8 emits a distinct but ABI-equivalent 24-byte unrelocated
leaf with SHA-256
`ad41b3e291952256888ed67d52b32f0a0bdb2d1e420268853b1616480fe3fd8a`.
At profile offset 3,730/runtime `0x0043530A`, relocation produces SHA-256
`073f72e4295c96ea683a2d996404ba9dcce760aa8154d24a8b4902c412e14063`.
The canonical stock entry is replaced by `1ef0bcbf` plus ten Thumb NOPs.

Host tests pin the complete body, absence of direct callers, unique entry
literal, both registration-load encodings, exact owner forwarding, null-record
behavior, low-bit clearing, and exact indirect callback argument. Both reviewed
toolchains compile and relocate under fail-closed source, ABI, symbol-type,
placement, and artifact pins.

The runtime tranche now contains 26 entries at
`[0x00415844,0x004163B2)`: 2,890 exact stock bytes, 128 authenticated direct
caller edges, two authenticated registered-pointer ingress paths, 2,652
canonical compiled Thumb bytes, and 52 strict relocations. The canonical
overlay is 3,766 bytes with SHA-256
`2e281f298cd2372e8ac45046b14a22355fc2d95d096c719881449d63a33dc2be`.
The 152,366-byte provider hashes to
`0ee093f0771ce96c91a4b72c87a87d96e2c2700afba81c419810b1f79726cfc1`,
has CRC-32C/MSB `0xAA2A34E1`, and accounts for 3,757 source, 4,342 patch,
ten alignment, and 144,257 retained authenticated bytes. It ends at
`0x0043532E`, leaving 11,474 bytes before Apollo main. The Linux overlay is
3,754 bytes with SHA-256
`1df6c64c897869c54a628296130809229783cee9a06a03f26341991e2a26cebd`;
its 152,354-byte provider hashes to
`00b23979bfbca0468d6172c6c278049d82c63ca7e35b2cae56802847c85f6033`.

The canonical unsigned package is 4,733,944 bytes with SHA-256
`dc1ab1c5bfde31a16ba1cc78c42a603f4f5278c9e1f7e0c35bee592689c2251e`.
Its 4,354,231-byte flash plan hashes to
`cd07856ef6b89d570851381170c03334f1499478656c0c79e5a9759e571fb8af`
and records 6,271 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,942 bytes with
SHA-256
`ec95e7ff45fbb854019e02c7c59663feec0d23e9936cfb235e47891190b6716f`;
its 2,317,225-byte plan hashes to
`19df9e34c61b539edc4b72a46207d70450a420985d51e51d35101c7e14adbb6a`
and records 3,331 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x004163B2`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
callback-registration, scheduling, concurrency, or caller-path claim and does
not declare bootloader or firmware-wide functional completeness.
