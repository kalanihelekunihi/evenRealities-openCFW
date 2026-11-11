# R1 temperature and SpO2 service entries in C

Five functions in `native_health_service_wrappers.c` now use ordinary C: the
sleep-status logger `0x8e154`, sync-status null/length gate `0x8e1e0`, constant
SpO2 and temperature forwarders `0x8e274`/`0x8e552`, and no-op `0x8e55c`.
The [review receipt](health-service-c-review.json) binds production source/object
hashes, REA bytes, replay artifacts, negative controls, qualification and the
promoted exact source plan.

The logger preserves the full incoming status word, fresh mode reads, short-circuit
log gating, structured messages and SDK tag. The sync gate forwards the original
buffer and full length only when both are nonzero; otherwise it uses the stock
null-buffer messages and tag. The SpO2 forwarder supplies 1 and the temperature
forwarder supplies 0. The no-op has no effects. These functions add no state or
policy. Explicit per-function sections preserve independently linkable entries.

The two publication bridges are unchanged and now live in
`native_health_state_publish.c`, with one implementation per stock function.
They publish event 4099 or 4103 only when the low input byte is below 2, while
retaining the entire incoming word in their eight-byte frame. After publication
they restore the potentially callback-mutated word into R3. Ordinary C cannot
promise that register/frame behavior; the bridge instructions remain assembly.
The old seven assembly blocks are reduced to these two. Both retained allocated
instruction sections match their former source object's sections exactly.

There are 1,072 paired stock/C replays. Logger and sync-gate cases cover full
argument words, null/zero combinations, changing mode sequences and interrupt
masks. A further 640 of those pairs compare all integer registers and APSR through
forwarders, no-op and actual publication bridges, including saved-word mutations,
upper input bytes and invalid low-byte states. All pairs check callee-saved integer
and FP registers, SP, masks and FPSCR. Logging and sync backend operations remain
modeled boundaries; logger/gate caller-clobbered register residue and APSR are
excluded. Provider stack depths match stock: ordinary calls 8, tail calls 0 and
publication 8 bytes. Six compiled defects are rejected: wrong constant values,
missing length gate, wrong status, non-short-circuit logging and wrong SDK tag.
Physical and concurrent behavior remain unverified.

The production two forwarders and no-op pass exact qualification at their named
entries with native publication bindings: 6+6+2 bytes. Their production and
qualification instruction sections agree. Only those three roots enter the exact
source plan, adding 14 source-built bytes. The logger and sync gate do not qualify.
The two retained assembly publication roots are not promoted. Earlier plan units
and regions remain intact. The preview hybrid matches the locked artifact before
the canonical plan is updated. Current exclusive provenance is 4,313 source-built,
641,847 executable pull-through and 248 resource bytes.

All 632 units compile and both relocatable compositions pass without duplicate
strong symbols. Of the previous 631 objects, 630 remain identical and only the
converted service unit changes; the publication unit is new. Application/bootloader
import sets remain unchanged at 172/34. Manifest checks pass. These results do not
establish a complete source-only link, complete C firmware or hardware validation.
