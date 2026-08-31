# G2 bootloader address-identified masked runtime-wait wrapper source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: software implemented and production-routed; physical validation blocked.

Superseded as the current frontier by
`g2-bootloader-runtime-notify-416378-source-closure.md`; the evidence below
remains the pinned wait-leaf checkpoint.

The complete 180-byte entry `[0x004162C4,0x00416378)` has SHA-256
`48f58a21c85b21ba530c63f1bc88a6bc17c080da9f2c370f6c2cfc3a3430f42d`
and authenticated direct callers at `0x0042DD3A`, `0x0042E37C`, and
`0x0042E3EE`. It returns `-6` in critical context and `-4` for a mask whose
signed high bit is set. Otherwise it accumulates observed bits across ordered
calls to retained backend `0x00418DAC`, supports wait-any or wait-all behavior
through option bit zero, suppresses the backend clear mask through option bit
one, recomputes a wrap-safe remaining timeout from retained tick source
`0x0041835A`, maps zero-timeout exhaustion to `-3`, and maps finite-timeout
exhaustion to `-2`. Address-derived names avoid unsupported claims about the
retained platform objects.

`runtime_wait_4162c4.c` is a 2,549-byte MIT clean-room
implementation with SHA-256
`9f3aa5e7fe42a33b59888d9b7d8a43118df0ee868703e75cf6eedd769d0c6ed1`.
Both reviewed compilers emit the same 178-byte, two-byte-aligned unrelocated
leaf with SHA-256
`e6dca7f52c68da57fd4f46b8ee17306d860b54ac18dd29e3f8d24e05bd36bba7`.
Apple clang places it at overlay offset 3,536/runtime `0x00435248`; four
strict calls at offsets 12, 56, 82, and 136 produce relocated SHA-256
`494280f9f8beee690310f3907623bd0574d885866a2b861413227a7537ba8bc6`.
Homebrew clang 22.1.8 places it at profile offset 3,524/runtime `0x0043523C`
and produces relocated SHA-256
`34f965ebe87ec8da5e7e60c32e265932f734370c4200367a8b8fc4c8d0a451b5`.
The canonical stock entry is replaced by `1ef0c0bf` plus 88 Thumb NOPs.

Host tests pin critical and invalid-mask short circuits, wait-any success,
option-controlled clear masks, wait-all accumulation, remaining-timeout
recomputation, a final zero-timeout probe, and both timeout result mappings.
Both reviewed toolchains compile and relocate under fail-closed source, ABI,
symbol-type, and artifact pins.

The runtime tranche now contains 24 entries at
`[0x00415844,0x00416378)`: 2,832 exact stock bytes, 126 authenticated caller
edges, 2,600 canonical compiled Thumb bytes, and 49 strict relocations. The
canonical overlay is 3,714 bytes with SHA-256
`5d647fe0862152ae9b8b77e4d7505b4b23f93a741c65845b7fae2a723c39631f`.
The 152,314-byte provider hashes to
`d222577a0ec28801a3428fa031bd838480bb8cc4fd066372608f1c3eaffb9039`,
has CRC-32C/MSB `0x27AAC01E`, and accounts for 3,705 source, 4,284 patch,
ten alignment, and 144,315 retained authenticated bytes. It ends at
`0x004352FA`, leaving 11,526 bytes before Apollo main. The Linux overlay is
3,702 bytes with SHA-256
`8a0ccf0e8e8be4de7bb6451fa6bd1d37e6f01a1cde4d07600bc3f349e4f73952`;
its 152,302-byte provider hashes to
`5f3205557a583b3e46c0ec18715874ecb8fb5b8f2fc9745271158b035efa0946`.

The canonical unsigned package is 4,733,892 bytes with SHA-256
`d7141c1c6245d41f460b01a0f8665931b8457b1bcd39369d5f00cb18f8fa3af5`.
Its 4,351,281-byte flash plan hashes to
`0eb4e44ad23ba0ea518826c143837697fbb4dc74448c549e85daed9f6ed89988`
and records 6,267 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,890 bytes with
SHA-256
`09ac7157f87c183aad9c7fd475ee703f4c4b56a476f7694f7dfd73935007af4b`;
its 2,315,677-byte plan hashes to
`0de8d523b0281f838904704b72ad8cc3f89287d5c7f4ecf0bbac897b522cfdf7`
and records 3,329 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x00416378`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
wait, tick, concurrency, or caller-path claim and does not declare bootloader
or firmware-wide functional completeness.
