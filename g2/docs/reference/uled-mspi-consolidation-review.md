# uLED MSPI implementation consolidation

Four stock functions had two C implementations under different names. The
consolidation retains the hardware-role names below and redirects the old
callers to them; it does not introduce an alternative implementation or
qualify any function for the source plan.

| Stock entry | Retained symbol | Superseded symbol |
| --- | --- | --- |
| 0x5926EE | `display_driver_uled_command_5926ee` | `display_driver_uled_type0_aux_reg_write_5926ee` |
| 0x59C876 | `display_driver_uled_device_reconfigure_59c876` | `display_driver_uled_device_check_59c876` |
| 0x59C980 | `display_driver_uled_serial_mode_59c980` | `display_driver_uled_packet_begin_59c980` |
| 0x59CA2C | `display_driver_uled_quad_mode_59ca2c` | `display_driver_uled_packet_end_59ca2c` |

The superseded four single-function files and their source-manifest units
are removed. The two packet-submit callers use typed configuration pointers
for serial/quad transitions, matching the retained definitions. The command
completion caller uses the retained command helper. Other panel callers
already used these retained functions.

The relocatable link had four `--defsym` aliases that redirected the retained
names to the superseded definitions. Those aliases are removed as part of the
consolidation, so calls now bind to the retained C bodies. The source build's
link-failure check caught these stale aliases during validation.

## Evidence and execution comparison

The locked Apollo main payload has SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
REA/Ghidra 12.1.4 analyzed an unchanged stock slice at runtime
`[0x592600,0x59D200)`, with analyst-supplied Thumb entry seeds. Observed body
sizes are 48, 266, 172 and 208 bytes respectively. The original artifact was
not modified. This bounded import has incomplete callee coverage and is not
independent pseudocode review or whole-image coverage admission.

An isolated Unicorn probe executed each stock function and both C versions
compiled for Cortex-M55, hard float, `-Oz`, freestanding. All **129 cases**
agreed across all three versions:

- Nine command cases vary command byte and 32-bit length and compare the
  complete 28-byte descriptor, including its context and payload pointers.
- Forty cases each for reconfiguration, serial and quad vary success or
  failure at disable/configure/enable/control and all eight log-flag values.
- Observations compare helper order and arguments, the 24-byte configuration,
  the control mode byte, log-flag queries and fixed log arguments, applicable
  return status, and preservation of the caller's original configuration.

Memory-copy, MSPI and logging helpers were controlled mocks. Control checks
cover the mode byte rather than unconstrained scratch bytes; log checks
exclude unconstrained variadic register/stack contents. Serial/quad return
registers are unspecified and excluded. These comparisons do not verify the
lower-level helpers, interrupt concurrency, hardware timing, full source
completeness or compiled byte identity.

At this consolidation step, all 2,837 Apollo-main units compiled, with no
expected failures or duplicate strong symbols, and the relocatable link
passed. That build reported 1,456 object-level imports before aliases. The three edited caller
objects have identical allocated sections and normalized relocations to the
baseline after accounting for the intended symbol renames. The G2
manifest then contained 4,998 units; the four-unit reduction removes duplicate
implementations rather than firmware behavior. Final build evidence is in
[`source-build-goal-validation.json`](../../evidence/source-build-goal-validation.json).
The later [callback review](uled-irq-handle-review.md) removed one more
duplicate unit; current counts are in that build summary.

## Linkage correction and count scope

The first consolidation mistakenly left the three retained translation
units marked `link: false`. Compilation passed while three retained entry
names became unresolved in the composed object (131 to 134). This was
detected by comparing the actual composed symbol sets, rather than the
object-level import census. The replacements now inherit the removed
copies' relocatable-link participation. Their MSPI disable/enable/pin-mode
calls use the existing source-backed NOR/MSPI names, avoiding three
unbound alternate names. The redundant 0x45A568 role getter in the command
TU was removed; its existing linker alias still resolves to the single
`audio_uart_device_role_get` body.

The 129 stock/C comparisons pass for these retained bodies, and the current
composed unresolved-symbol set is exactly the original 131-symbol baseline.
Relocatable participation does not admit the candidates to the qualified
source plan. Build reports now distinguish object-level and composed
unresolved counts; successful composed output determines the latter.

Raw pseudocode and assembly observations, analysis identity, limitations and
comparison results are retained in
[`uled-mspi-consolidation-review.json`](../../evidence/uled-mspi-consolidation-review.json).
The wrapper and probes live under `build/goal-uled-hardware/`; removed source
snapshots are kept there for probe replay. No assembly wrapper or stock
executable slice is admitted as firmware source.
