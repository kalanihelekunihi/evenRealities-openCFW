# PCM2.2 selector 17 transition handler

Selector 17 is the locked routine at `[0x429718, 0x42984e)`: 310 bytes,
SHA-256 `1800926f5cd512a3f3b45b77aa8f9edc1969de9c3a658341aa6a23650c6e6480`.
The verifier authenticates the firmware image, Ghidra extent, exact body hash,
and one-byte-short/one-byte-long negative controls. `handler17.disasm` records
the authenticated instructions.

The C handler implements the observed timer gate on bit 0 of `0x400083e0`, the
60-iteration ready poll of bit 30 at `0x40008064`, one-microsecond delay calls,
and the `0x42a04a` timer service call. It applies the signed trim delta rule:
`max((new_low - current_low), 0) * 2`, adds that to current trim, and saturates
at 127. Stock first writes this intermediate value to `0x40020048`, then writes
temperature and active fields at `0x40020080`, and finally replaces the low
seven bits of `0x40020048` with the new trim. The push/pop ABI also returns the
four low-voltage bytes in R0 and the final `0x40020048` value in R1.

`comparison.json` passes 14 direct fixtures and one natural walker fixture.
It covers positive and nonpositive deltas, saturation, timer disabled, timer
ready and not-ready states 2/7/26, and compares return registers, all observed
state, ordered writes, wait calls, callee-saved registers, SP, and PRIMASK. The
9-to-10 transition selects sequence 17 and both stock and source call the
handler with `[10, 9, 3, 1]`; both return `[17, 1]` from the outer walker.

The source candidate is `/tmp/opencfw-root-pcm22-relocated/record-candidate.elf`,
SHA-256 `4b1fb7505187310b0b9bcd84f1479693a313db9485d4741960a1fbdf6210c645`.
The source machine executes its initialized-data installer first. The installed
1371 bytes normalize to the stock decoder hash
`e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843`; selector
17 retains its stock target until the isolated fixture binds slot 17 to the
separate addon at `0x30001`. No base candidate is modified. The source machine
traps on execution into locked-image addresses; stock executes the authenticated
handler and walker. The ROM cycle-wait service at `0x40` is the only controlled
timing boundary.

The comparison visits 107/310 stock handler bytes, 31/130 walker bytes, and
70/390 selector bytes. Exact unvisited handler addresses are recorded in the
JSON receipt. This is a bounded differential, not a whole-firmware or hardware
equivalence claim. Run `make verify` to rebuild the isolated addon and regenerate
the receipt.
