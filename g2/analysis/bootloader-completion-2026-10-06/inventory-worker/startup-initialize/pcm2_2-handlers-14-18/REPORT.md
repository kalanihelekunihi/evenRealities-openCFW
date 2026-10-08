# PCM2.2 transition handlers 14 and 18

This folder reconstructs two indirect targets reached by the SPOT sequence
dispatcher. The locked image is SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
`verify.py` authenticates each target's exact function record and extent,
including one-byte-short and one-byte-long negative extent controls.

| Sequence | Stock range | Bytes | SHA-256 |
|---|---|---:|---|
| 14 | `0x42944a..0x42951c` | 210 | `7c3fc667225097109aae57cd92a34f6858a8bdfff93e2fb6d9a700d042ce3760` |
| 18 | `0x42984e..0x429a1e` | 464 | `ebb8217a646d3261e01b47fa26f9ca9195377c11a6eefe3e47970b5b0dc77651` |

The source ABI is
`uint32_t handler(uint32_t new_power, uint32_t current_power,
uint32_t new_ton, uint32_t current_ton)` in r0-r3. The locked root-target
receipt reports 240 calls to each target and records `(3, 0, 0, 0)` for each
sampled call argument. The compiled implementations are
`opencfw_spot_pcm22_transition14` and `opencfw_spot_pcm22_transition18` in
[handlers.c](handlers.c).

Handler 14 reads the current and target state words and the packed low-voltage
trim fields at `0x20026c04`. It updates cached power/Ton and trim fields, then
applies the target VDDF trim while preserving the rest of its register. Its
return value is the four packed 7-bit trim values reconstructed from the
stock stack word. Handler 18 caches the new state, applies temporary
double-boost trim writes in stock order, delays for stabilization, then writes
the final trims and core-LDO fields. Its return value is the target state-word
pointer, matching the stock function's stack-slot reuse.

The pinned upstream reference is
`../gx-native/upstream/am_hal_spotmgr_pcm2_2.c`. Its BSD-3-Clause source was
consulted to interpret state and trim fields; its implementation text was not
copied. The handlers follow locked instruction behavior where it differs from
that public translation unit. The timer service is linked from the separately
reconstructed `../pcm2_2-native/timer_support.c` plus the actual clock manager,
status-poll, and critical-save sources. There are no successful return stubs or
locked executable bytes in the source ELF.

`comparison.json` preserves the original 44 stock/source handler-fixture
pairs. The added `comparison-timer-enabled-local.json` passes 56 pairs against
the rebuilt source ELF, including six timer-enabled combinations per handler:
ongoing states 2, 7, and 26 each with ready and not-ready status. These cases
exercise the real linked timer service, sequence helpers, timer stop, and
clock providers. They compare state, ordered MMIO writes, ROM wait calls,
callee-saved registers, SP, and PRIMASK. The exact locked instruction extents
were visited completely (210/210 and 464/464 bytes) across the combined
fixture set.

The timer-control gate comes from `LSLS #31` on `0x400083e0`, which tests bit
0; the status-ready gate comes from `LSLS #1` on `0x40008064`, which tests bit
30. Timer-enabled fixtures set those bits from the corresponding instruction
semantics. The prior source had the status mask one bit too high; the corrected
source matches the locked instruction path. Both the local linked ELF receipt
and `comparison-timer-enabled-candidate.json` pass. The latter uses the
parent's freshly rebuilt combined candidate ELF and exercises the same 56
handler-fixture pairs. The prior mask counterexample is retained in
`comparison-timer-enabled-mask-failure.json`.

Run `make verify` in this directory to rebuild the source ELF and execute the
comparison. The test uses the locked image only on the stock machine. The
source machine loads ELF segments only and traps if execution enters the locked
image. This is offline emulator evidence, not hardware behavior or a claim of
complete PCM2.2 source/build equivalence.
