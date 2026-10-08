# Bootloader source integration status

Latest verified immutable image: **92619ea6a92780848703d61cb91385c950b717089718aa6a82a13baf6fc1cda4**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both stop/reboot persistence and observables match; both sides reach the fixture application reset entry without exception.581 frozen files and144 linked objects remain unchanged. [Exact-image receipt](same-image-validation-92619e.json). Prior52ca30 and earlier immutable checkpoints remain preserved.

Seven-case observed instruction-byte numerator remains **35,468 /148,599 =23.86826%**. Shared startup does not deliver an asynchronous IOM IRQ, so adding its native source does not increase that path footprint. This is not implemented completion. Seven-case plus515 asynchronous direct traces union to37026 original bytes, with additional callback/delay/FIFO model limits. Six original FP64 effects remain modeled. Synthetic callback instructions are excluded from stock traces.

## Asynchronous source closure

[Readable behavior/layouts/ownership](context-events/REPORT.md). New source/header `initializer_callbacks/context_events.c`/`.h` reconstruct publisher42c45a, service42c6f8, classifier42c076, recovery42c0b2, CQ status427a56/resume427b38 and index refresh427754. The seven bodies are retained in the source-linked test ELF. [Partial ownership](context-events-ownership-92619e.json) maps1490 original bytes, all observed across bounded515 direct comparisons; that is instruction visitation, not all possible interleavings or hardware semantics.

505 principal and10 independent guard/index/flag cases PASS. Counter wrap, descriptor callback clearing, CQ callback mode2 retention, callback stop metadata, error recovery, finite command chains/FIFO drains and synthetic callback reentry compare stock/source. A nested descriptor callback can drive pending count from0 to0xffffffff in the stated synthetic state; no clamp or release is invented. No hardware manifestation is claimed. Callbacks clear after return, with ordinary CQ retention in mode2; userdata/record storage is never freed by these bodies. External callback bodies can have additional ownership effects and are not recovered here.

740 existing IOM child,12 native semaphore heap cleanup and2 conditional CQ subtype cases also PASS on this image. Alignment355 mappings PASS and known bad placement rejected. Manifest:66 numeric aliases,36 segments,zero source hash mismatches. [Linked inventory](implementation-inventory-92619e.json):474 defined function symbols and77524 deduplicated compiled function bytes; compiled sizes are not original-byte implementation percentages.

## Closed versus open

Native claim/transaction/configuration/enable/retry/IRQ-enable, clock/interface and CQ adapters remain integrated. NVIC430470 and semaphore416762 stay native, with prior reports preserved. Asynchronous publisher/service and their directly required recovery/status/index helpers are now reconstructed and directly validated.

The actual stock caller is IRQ wrapper430610: read enabled status42c672, clear42c6b6, service42c6f8 using module4 handle0x200003b8. IRQ wrapper/status/clear and actual vector delivery remain unclosed. Descriptor registrar430280, ADC/service and remaining lifecycle/scheduling boundaries remain open. Queue submission/full rejection/allocation failure and independent release/uninitialize are not established by this service: it allocates/frees no storage and performs no pending-capacity guard. [Provider checklist](remaining-providers-dceae3-worklist.md).

MMIO, ADC, scheduler, ROM operations and callback behavior remain synthetic. No real partial write, IRQ timing, callback workload, recovery or application instructions are proven. Relocated test ELF uses prepared objects; it is not a clean whole-payload source build, source-complete firmware or byte-identical artifact. No commits, flashes or IAR authentication occurred.
