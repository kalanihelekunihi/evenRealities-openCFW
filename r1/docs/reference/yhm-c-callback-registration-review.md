# YHM2710 callback-management routines reconstructed in C

REA confirms two remaining native product adapters use the existing twenty-byte
YHM transport context at `0x2000687c`. No new context owner is introduced.
`r1_yhm_block_word_set` (`0x5083c`) stores its input word verbatim at context
offset zero and returns one. Zero clears the word; nonzero values are not
validated or transformed. This is the word already consumed by the C transport
completion routine; concrete callback targets remain separately unproven.

`r1_yhm_irq_register` (`0x507ac`) reads the device at context offset twelve,
opens it through registry slot eight, then freshly reloads that device and
tail-dispatches slot `0x20` with selector one and the original callback word.
The IRQ name labels the inferred role; the native argument/slot contract is
the verified fact. The original callback argument survives open's register
clobbers and context mutations. The registry's null-device result one,
missing-method result nine and raw method result words are preserved.

The probe passes 1,176 paired stock/C cases (2,352 executions) using the actual
native and C registry dispatchers and the actual shared C context. Only device
methods are modeled. Cases cover eight callback words, null/two concrete device
records, open-induced device replacement/clearing, absent methods, and four
method result words. It compares exact ordered context reads/writes, method
calls/arguments, raw returns, unchanged context fields and preserved registers,
stack and masks. At the registration method it checks original caller SP/LR,
confirming the tail path after the open call.

A deliberate pre-open device snapshot fails when opening device A installs B:
stock registers on B, while the variant registers on A. An executable-section
audit confirms all six pre-existing YHM transport sections are unchanged;
only the two new sections are added. Both normal import sets are unchanged.

The normal report `build/sources-goal-r1-yhm-callbacks/report.json` compiles
571 R1 units without failures or duplicate strong symbols. Imports remain
197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](yhm-c-callback-registration-review.json) binds REA, source,
shared state/registry providers, execution probe, negative control, section
audit and normal build by hash.

C sizes are 34 bytes for registration and sixteen for the word setter, versus
native instruction sizes 26 and eight. Neither is byte-qualified. The canonical
source plan and G2 gates are unchanged. Concrete callback signatures/targets,
private frames/caller-clobbered registers/flags, concurrency, electrical IRQ
behavior and complete source-only byte identity remain unverified.
