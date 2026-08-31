# G2 bootloader runtime-state gate acquisition source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: software implemented and production-routed; physical validation blocked.

Aggregate package and accounting values below record this historical
checkpoint and are superseded by the gate-state mapper closure that follows.

The complete 48-byte entry `[0x00416058,0x00416088)` has SHA-256
`805717a87092e08f4225a51f07e8c0d26de600cd697ca91f552be3abc70fcf61`
and one authenticated direct caller at `0x0042E39E`. It first invokes the
source-owned critical-context predicate. A nonzero result returns `-6`
without querying runtime state or touching SRAM. Otherwise it calls the
retained runtime-state query at `0x00418B56`; a value other than one returns
`-1`. State one then reads the gate word at `0x200270D4`: a nonzero word
returns `-1`, while zero is atomically advanced to one and returns zero.
Host tests pin each short circuit, call order, return code, and store effect.

`runtime_gate_acquire.c` is a 969-byte MIT clean-room
implementation with SHA-256
`f3177d38d79fe95c61c5462efaf9dff04a88a4e86b68a06fadf193b943012ab6`.
Apple clang emits a 48-byte leaf at overlay offset 2,976/runtime
`0x00435018`. Its unrelocated SHA-256 is
`482bfda39fe3d23dd041da0aa6a69a66bf4ef839a94595a453ce7de299256924`
and its relocated SHA-256 is
`6384b19b04601b7e6feebffcc0625833b33ccf3802bf4415d29bb1c4db6696fd`.
Strict `R_ARM_THM_CALL` relocations at offsets two and fourteen bind only the
source-owned critical-context leaf and retained state query. The stock body is
replaced exactly by `1ef0debf` and 22 Thumb NOPs. Homebrew clang 22.1.8 emits
the same raw body at profile offset 2,968, with relocated SHA-256
`2c013c523533e1f118a114d99745be033a0792f88b7dd8df32ab735bb4896eb7`.

The canonical overlay is 3,024 bytes with SHA-256
`84fd6a9f7e7758c81933aa0908aaa2fdc354980ca1bb834a432704b8ff9a22d3`.
The 151,624-byte provider hashes to
`617e0e342659033480d84bde938d8c00b7cbdfee3148dfe6bed6e71210705470`,
has CRC-32C/MSB `0x336B26F6`, and accounts for 3,017 source, 3,532 patch,
eight alignment, and 145,067 retained authenticated bytes. It ends at
`0x00435048`, leaving 12,216 bytes before Apollo main. The Linux overlay is
3,016 bytes with SHA-256
`97984bb50cded3117a32f9883181de11ca92fa4d875a85b643543fff7e8079bf`;
its 151,616-byte provider hashes to
`4d7e952a97a45d49373adf24ccb3e0b92a055dd2ac2eaca5a28c55e723587780`.

The canonical unsigned package is 4,733,202 bytes with SHA-256
`03bd0707aa415aa0425c35284408094b36a6fa3d4c63742adbe7a879f4c0c2c0`.
Its 4,337,692-byte flash plan hashes to
`35e3b7dc7d3b458e55aab05f66cf2e47bfca55d009e9f28d3d505838cf22e025`
and records 6,248 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,204 bytes with
SHA-256
`94055ef946f6bcf9fd2d14ef1bdc50d76c74e286e56c4dc05dad422aeec12434`;
its 2,308,898-byte plan hashes to
`fd2c4dc1b397f02c9e060c2174a71e1bebf13bcc7f7801af5f07c21ff8d19bad`
and records 3,320 placed regions plus the same two unresolved boundaries.

The next distinct 40-byte callable body begins at `0x00416088`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
gate/concurrency claim and does not declare bootloader or firmware-wide
functional completeness.
