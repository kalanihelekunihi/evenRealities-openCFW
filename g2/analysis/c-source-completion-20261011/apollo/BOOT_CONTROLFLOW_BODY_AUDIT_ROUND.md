# Boot rooted body control-flow audit

The selected Boot candidate remains 373 C/ASM units, 1,010 definitions, and
three genuine ROM imports. The corrected coherent target receipt is
`boot-coplacement-selector17-reread-round/receipt.json` with
`PASS_BOUNDED_LINK` and 158,628 candidate bytes versus 148,599 stock bytes.
This is source compilation and bounded composition, not runtime equality or
hardware qualification.

Eight large rooted bodies moved from header-only leads to explicit reviewed
bindings in `manual_body_bindings.json`:

| Native entry | Selected C body | Control/effect checks |
| --- | --- | --- |
| `0x41bf84` | `opencfw_bl_mspi_mode_enter` | selector 23 early gate, selector 20 callbacks/clocks, critical set, poll and delay |
| `0x41c17a` | `opencfw_bl_mspi_mode_leave` | selector 29/28 branches, critical clear, release predicate, poll and callbacks |
| `0x41d294` | `opencfw_boot_device_info_initialize` | status/debug reads, source-owned factor tables and ten delays |
| `0x4213e6` | `opencfw_boot_info_read_dispatch` | selector limits, wrapped offset bound, OTP-ready and INFO0/1 address path |
| `0x42863e` | `opencfw_spot_pcm22_transition5` | early return, timer, profile snapshots, control register ordering and packed result |
| `0x429718` | `opencfw_spot_pcm22_transition17` | trim ramp, timer and two-step MMIO writes after source correction |
| `0x429c46` | `opencfw_spot_pcm22_transition21` | TON/boost, conditional cache state and ordered MMIO updates |
| `0x42bdf0` | `hw_state_compose_42bdf0_native` | three INFO reads, early failures, profile field commits and timer start |

For `0x41c17a`, direct Thumb disassembly proves the selected R0 selector
call to `0x41c0be`. In that child, the descriptor-copy call writes four words
over the saved R0–R3 stack slots before the group check. Its apparent ambient
R3 in pseudocode is therefore descriptor word 3, matching selected C. The
status-poll arguments also match the caller's R0–R3 plus stacked fifth word.
For the INFO reader, stock and C both compare the unsigned 32-bit wrapped
`offset + count`; this is not widened arithmetic.

The regenerated crosswalk covers 903 catalogue labels and 654 conservatively
rooted labels. The rooted header-only proof queue is **172**, down from 180;
the whole catalogue header-only queue is **270**, down from 278. These queues
are attribution work, not measured missing C body counts. All 654 rooted
labels still have some machine/provider crosswalk; imported ROM behavior,
indirect roots, complete source data/layout, and runtime equality remain open.

## Corrected source behavior

The native selector-17 body `0x429718` rereads `0x40020080` before its
second temperature/core field write and rereads `0x40020048` before its
final trim write. The selected C reused a value sampled before the first
write. `startup_pcm22_sequence17.c` now performs both volatile rereads. The
stock literal pool resolves `0x429a28` to `0x40020080` and `0x42a080` to
`0x40020048`. Corrected target object `unit_124.o` disassembles to `ldr`
at function offsets `+0xea` and `+0xf2`, after the preceding stores. This
qualifies the read/write order in source and compiler output; peripheral
side effects have not been run on hardware.

`0x4262e0` MSPI blocking transfer and `0x427160` PLL postdivider were also
inspected but deliberately retained as header-only leads. Their Ghidra return
width/ambient register and numerical child contracts need direct caller and
instruction proof before a stronger full-body claim. The other seven bound
comparisons did not justify source changes.
