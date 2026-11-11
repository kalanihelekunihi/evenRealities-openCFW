# Integrated STACMD hardware boundary review

The recovery routine now calls the configured void GPIO callbacks through the
same explicit raw-R0 gateway as transmit. The shared two-byte `BX R1` adapter
avoids calling a void function through an incompatible return type while
preserving the stock tail-return observation. Low calls use their void type.
REA at native `0x5cc8c` and raw execution establish high/output/high, delay,
low, four delays, then high with its raw R0 result.

The recovery-delay C loop retains the unsigned 209-iteration bound. Its timing
block contains four NOPs and an explicit tied-register increment. A plain C
increment compiled into a countdown or a different increment encoding; this
narrow assembly timing primitive reproduces the native 20-byte body at
`0x5c0fa`. It is not evidence that all assembly can be removed safely.

The official `tools/build/qualify_sources.py` compilation, native-anchor,
byte-equality and selection logic qualified this single manifest candidate.
The probe wrapper filters only the candidate input. Its generated selection
was appended to the source plan without altering existing selections. The
candidate-plan R1 hybrid build reproduces application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
It contains 3,617 source-built bytes, 248 resource bytes and 642,543 retained
bytes; this is not a complete source rebuild.

All 219 stock/C integrated comparisons pass. The actual read/write frame,
transmit, receive, parity, idle, recovery and delay implementations execute.
Only GPIO callbacks are probe-only C models writing ordinary RAM. Cases cover
zero-to-three-byte transfers, byte patterns, header truncation, invalid
commands, header/data parity mismatch, and both 1,000-read timeout phases.
Comparison includes raw R0, ordered GPIO arguments and sampled levels,
cumulative NOP count, output guards and callback RAM, callee-saved registers,
SP, interrupt masks and callback alignment. Recovery executes 4,180 NOPs.
Private stack depths may differ. This does not establish physical pulse timing,
electrical behavior, interrupt/concurrency behavior or full firmware boot.

All 562 R1 units compile with zero failures or duplicate strong symbols.
Application/bootloader imports remain 211/34. The G2 interrupted pseudocode
workflow and implementation gate remain unchanged. Exact source, probe,
qualification, plan and build bindings are in the
[machine-readable review](stacmd-c-integrated-gpio-review.json).
