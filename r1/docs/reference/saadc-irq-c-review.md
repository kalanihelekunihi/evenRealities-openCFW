# Nordic SAADC interrupt C source route

The stock SAADC IRQ entry at `0x317cc` now routes to `SAADC_IRQHandler` from the
already compiled, unchanged pinned SDK `nrfx_saadc.c`. The SDK macro renames its
`nrfx_saadc_irq_handler` definition to the vector symbol. This closes an unresolved
source route; it introduces no second implementation or new driver-state owner.
Firmware C, configuration, manifest, and source plan are unchanged.

REA reads cover the 320-byte native IRQ body and its buffer/event helpers.
The native control block is at `0x2002c250`. Compilation of assertions against
the actual SDK types confirms its 48-byte layout, all thirteen field offsets,
and the 12-byte event structure with payload at offset four. The fixture links
the actual existing C object and its static `m_cb` at that native address.
This controlled placement does not establish the final firmware link address.

13,056 stock/C pairs pass: 9,600 base cases, 3,200 callback-mutation cases and
256 independently enabled/pending-limit cases. They cover all combinations of
END, STARTED, CALIBRATEDONE and STOPPED, low-power/conversion-end states,
primary/secondary buffers, remaining-count boundaries, active channel counts,
and multiple enabled-limit masks. Independent pending cases also include zero
active channels. Callbacks can change low-power state, raise STARTED, change
remaining counts, change buffers, enable a pending limit after calibration or
clear enabled flags during a limit callback.

The checks compare ordered MMIO reads and writes, meaningful callback fields,
control-block snapshots at callbacks, final control block and mapped peripheral
memory. Return callee registers, SP, interrupt masks and adjacent state guards
also match. Five negative controls reject clearing the wrong event, retaining
conversion-end state, retaining the secondary buffer, inverting low-power
handling, and reporting the wrong limit type.

The SDK C callback frame is 48 bytes versus native 40 bytes. Event pointers are
checked within their respective frames; raw event padding and live callback
registers are not treated as equal. Ordered control-block stores between callbacks
are not compared. MMIO is emulated memory: autonomous ADC/DMA behavior, electrical
results, real exception return, concurrency, corrupt states and arbitrary private
frame aliases remain unproven. The callback is a modeled boundary.

Qualification compiles this SDK unit but selects no exact regions. All 589
normal-build source hashes, object hashes and the manifest hash were revalidated
against `build/sources-goal-r1-twi-open-c-final/report.json`; no firmware rebuild
was needed for this source-route change. That report has 164 application / 34
bootloader unresolved imports and no compile failures or duplicate strong symbols.
The existing canonical hybrid artifact and current source-plan hash were
revalidated: 4,245 source-built, 641,915 executable fallback and 248 resource bytes.
It retains the locked application SHA. Complete source-only rebuilding and native
byte identity remain unproven.

Machine-readable observations, hashes and report pointers: `saadc-irq-c-review.json`.
Reproducible probes: ignored `build/goal-r1-saadc-irq-c/`.

A subsequent [bounded observer replay](irq-observer-review.md) passes the full
original matrix with MMIO hooks restricted to their register ranges.
