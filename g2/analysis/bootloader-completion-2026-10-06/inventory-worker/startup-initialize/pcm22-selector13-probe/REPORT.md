# Selector13: locked float boost and LP/HP sequence

Standalone reconstructed C:pcm22_sequence13.c. Locked bootloaderf89a4c46, original0x4291ec..0x42944a (606 bytes). Probe identityeff67c82c2b90d3d82ba5f9b742c4544a41ce0debd65f4e28bba590b143adc67; actual image and original body hashes appear in current-candidate.json and selector13-probe-comparison.json.

301 original-instruction comparisons visit all606 body instruction bytes and agree in rawR0, full rawFPSCR, MMIO/cache-global write order, ROM delay inputs, stack, saved registers and PRIMASK. Additional24 fixtures vary HP enable, readiness and switch timeout and target profile. This is bounded differential coverage, not exhaustive value/scheduling proof. Negative SDK-style unit gain is rejected: selector13-sdk-gain-negative.json retains mismatched return/FPSCR and VDDF register write.

Call flow: timer wait/service → publish cached globals → TON adjust → VDDF temporary boost → VDDC temporary boost → native50us delay → restore target VDDC → load CORE temperature coefficient and trim → native5us delay → restore target VDDF → LP request/wait → set override bits6,3 and clear bit25 of4002037c → optionally enable HP supply/wait → request HP/wait → restore temporary supply-enable bit.

The VDDF temporary delta is unsigned32(targetVDDF - baselineVDDF), converted to float, multiplied by the locked binary320x3f666666 (approximately0.9), converted back to unsigned32 with VFP semantics. baselineVDDF comes from profile entry1 at20026ba8. Unsigned underflow is observable; do not simplify to signed/clamped arithmetic. Addition wraps before comparison with128, then low7 bits are written or saturated127. VDDC boost uses signed positive difference doubled and saturates127. Raw return is the computed VDDF delta, not the packed control word returned by9/10/23. Updater ignores the callback return.

This differs materially from the SDK family: unit VDDF gain, nominal10us delays and a pre-VDDC delay described there are not the locked sequence. Stock has no pre-VDDC10us delay and uses5us after CORE trim. Exact disassembly is the authority; family code is a shortcut to hypotheses.

The226-object probe contains standalone13 alongside the225-object9 candidate, but slot13 and capability bit remain unsupported. It is not an integration checkpoint. Native timer/TON/delay/status providers execute, with resident ROM40 stubbed. Synthetic MMIO/readiness and Unicorn FP are not hardware exception/scheduling proof; Selected rounding modes, FZ/DN and cumulative flags are included in36 additional fixtures; hardware FP traps and all exceptional inputs remain unproved.

Next: install the real13 table entry in a separate successor, add natural8→9 dispatch and broaden exceptional FP probes, then affected and seven integration cases, object/relink reconciliation. No commits, shared-state or hardware writes.
