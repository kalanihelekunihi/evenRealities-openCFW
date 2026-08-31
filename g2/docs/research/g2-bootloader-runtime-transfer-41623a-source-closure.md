# G2 bootloader address-identified two-phase runtime-transfer wrapper source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: software implemented and production-routed; physical validation blocked.

Superseded as the current frontier by
`g2-bootloader-runtime-wait-4162c4-source-closure.md`; the measurements below
remain the authenticated transfer-wrapper checkpoint.

The complete 138-byte entry `[0x0041623A,0x004162C4)` has SHA-256
`b30ed83bcec2f4c12f8987b6d05abe0138d2a8791063900e3c7664f45e7b3058`
and authenticated direct callers at `0x0042DD0A` and `0x0042E2B0`. A null
first argument or negative signed second argument returns `-4` before querying
context. Otherwise the entry performs an ordered two-call transfer sequence
through retained critical backend `0x00418FE8` or normal backend `0x00418E70`
and returns the result written by the second call. The critical path also
requests PendSV by writing `0x10000000` to `SCB->ICSR` at `0xE000ED04` when
the first call reports scheduling is required. Address-derived backend names
avoid unsupported claims about the retained platform objects.

`runtime_transfer_41623a.c` is a 2,408-byte MIT clean-room
implementation with SHA-256
`5578c14de783782b6a622fe81f59d95ba20fefcd80aafe176d595d98371ab89c`.
Apple clang emits a 128-byte, four-byte-aligned leaf with unrelocated SHA-256
`136f841a809d839aa0bbcc7da5efb8c75882f1db660d014ce0ebcf6a05440987`.
A two-byte alignment pad places it at overlay offset 3,408/runtime
`0x004351C8`; five strict calls at offsets 18, 42, 60, 96, and 112 produce
relocated SHA-256
`0cf94de76453967aaf8f6a22b8acfd8dd32cf280987aeab9db3fe6fc8efee8b9`.
Homebrew clang 22.1.8 emits a distinct unrelocated leaf with SHA-256
`b2124ea3218bbb02a1d0e53918fc35a429af9602cdcf3050d8326ae4844e9326`,
places it without padding at profile offset 3,396/runtime `0x004351BC`, and
produces relocated SHA-256
`617d3ec0342d8720b22f2534015a53db6a99dd8008cb29e1dc2b363577b3195a`.
The final four-byte word in each authenticated executable section is the
intended fixed `0xE000ED04` SCB literal; it has no unresolved relocation.

Host tests pin invalid-argument short circuits, exact normal and critical
two-call order and arguments, result propagation, and conditional PendSV
request behavior. Both reviewed toolchains compile and relocate under
fail-closed source, ABI, symbol-type, literal, and artifact pins. The stock
entry is replaced by `1ef0c5bf` plus 67 Thumb NOPs in the canonical provider.

The runtime tranche now contains 23 entries at
`[0x00415844,0x004162C4)`: 2,652 exact stock bytes, 123 authenticated caller
edges, 2,422 canonical compiled Thumb bytes, and 45 strict relocations. The
canonical overlay is 3,536 bytes with SHA-256
`07ab222c04a32c1dfe34fdd22b5a49a16881fdefc72f7759840f430d8825f660`.
The 152,136-byte provider hashes to
`88c5bd2b960f949a6b5dacb799dc150ad82f0a72171c6e35d100af7bd1465c64`,
has CRC-32C/MSB `0xE1DFE4F8`, and accounts for 3,527 source, 4,104 patch,
ten alignment, and 144,495 retained authenticated bytes. It ends at
`0x00435248`, leaving 11,704 bytes before Apollo main. The Linux overlay is
3,524 bytes with SHA-256
`882c7169773e791c8327a7305d7761edbaba7e0cbc4b7377dab632cf58899208`;
its 152,124-byte provider hashes to
`df3bbaaf72fd487b7c54f6a2776d04f29d19c5f768d965e18be5549bc71e5454`.

The canonical unsigned package is 4,733,714 bytes with SHA-256
`17edeb19a42af9d068db05727cb40e0cd21aa45f81e426fef28a914fd4dc80c6`.
Its 4,349,834-byte flash plan hashes to
`dbc306648ca92fada98d074eb50f59147fe9175c1dc1d7ef4a3e3b52a7b0cd1c`
and records 6,265 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,712 bytes with
SHA-256
`26d668e423cac3a843cd42cddf97c8d68fb8e8fc55c1a487784aea455e130f8f`;
its 2,314,917-byte plan hashes to
`7715e3b0eb0cc5e0abbc464b73dee6b8cc0c7f8d06e257ae81c32fb8c8c32198`
and records 3,328 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x004162C4`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
backend, PendSV, concurrency, or caller-path claim and does not declare
bootloader or firmware-wide functional completeness.
