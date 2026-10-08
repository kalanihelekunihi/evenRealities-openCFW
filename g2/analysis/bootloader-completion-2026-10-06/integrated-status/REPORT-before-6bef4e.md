# Bootloader source integration status

Latest verified immutable image: **4f111ccb9ed4131499a99a47af126d83f4b56f8abb54a5e6073cbc6566e93e8a**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both stop/reboot persistence and observables match; both sides reach the fixture application reset entry without exception.584 frozen files and145 linked objects remain unchanged. [Exact-image receipt](same-image-validation-4f111c.json). Prior52ca30 and earlier immutable checkpoints remain preserved.

Seven-case observed instruction-byte numerator remains **35,468 /148,599 =23.86826%**. Shared startup does not deliver an asynchronous IOM IRQ, so adding its native source does not increase that path footprint. This is not implemented completion. Seven-case plus515 asynchronous direct traces union to37026 original bytes, with additional callback/delay/FIFO model limits. Six original FP64 effects remain modeled. Synthetic callback instructions are excluded from stock traces.

## Asynchronous source closure

[Readable behavior/layouts/ownership](context-events/REPORT.md). New source/header `initializer_callbacks/context_events.c`/`.h` reconstruct publisher42c45a, service42c6f8, classifier42c076, recovery42c0b2, CQ status427a56/resume427b38 and index refresh427754. The seven bodies are retained in the source-linked test ELF. [Partial ownership](context-events-ownership-92619e.json) maps1490 original bytes, all observed across bounded515 direct comparisons; that is instruction visitation, not all possible interleavings or hardware semantics.

505 principal and10 independent guard/index/flag cases PASS. Counter wrap, descriptor callback clearing, CQ callback mode2 retention, callback stop metadata, error recovery, finite command chains/FIFO drains and synthetic callback reentry compare stock/source. A nested descriptor callback can drive pending count from0 to0xffffffff in the stated synthetic state; no clamp or release is invented. No hardware manifestation is claimed. Callbacks clear after return, with ordinary CQ retention in mode2; userdata/record storage is never freed by these bodies. External callback bodies can have additional ownership effects and are not recovered here.

740 existing IOM child,12 native semaphore heap cleanup and2 conditional CQ subtype cases also PASS on this image. Alignment358 mappings PASS and known bad placement rejected. Manifest:66 numeric aliases,36 segments,zero source hash mismatches. [Linked inventory](implementation-inventory-4f111c.json):477 defined function symbols and77686 deduplicated compiled function bytes; compiled sizes are not original-byte implementation percentages.

## Closed versus open

Native claim/transaction/configuration/enable/retry/IRQ-enable, clock/interface and CQ adapters remain integrated. NVIC430470 and semaphore416762 stay native, with prior reports preserved. Asynchronous publisher/service and their directly required recovery/status/index helpers are now reconstructed and directly validated.

The actual stock caller is IRQ wrapper430610: read enabled status42c672, clear42c6b6, service42c6f8 using module4 handle0x200003b8. IRQ wrapper/status/clear are reconstructed and pass292 direct comparisons on this image. Actual exception entry/return and vector delivery remain outside the model. Descriptor registrar430280, ADC/service and remaining lifecycle/scheduling boundaries remain open. Queue submission/full rejection/allocation failure and independent release/uninitialize are not retained as standalone bodies in the fully partitioned IOM island42c034..42cdb0; global inline/dynamic reachability remains unproved. They are not established by this service: it allocates/frees no storage and performs no pending-capacity guard. [Provider checklist](remaining-providers-dceae3-worklist.md).

MMIO, ADC, scheduler, ROM operations and callback behavior remain synthetic. No real partial write, IRQ timing, callback workload, recovery or application instructions are proven. Relocated test ELF uses prepared objects; it is not a clean whole-payload source build, source-complete firmware or byte-identical artifact. No commits, flashes or IAR authentication occurred.

## IRQ checkpoint4f111c

Status42c672..42c6b6 (68 bytes), clear42c6b6..42c6e4 (46 bytes), wrapper430610..43063c (44 bytes) are native. Enabled selector is its low8 bits; clear writes INTCLR then reads INTSTAT back. Wrapper reloads handle200003b8 at each call, ignores clear/service return codes and skips zero status. Locked vector410068 contains430611, external IRQ10.292 tests include raw-RAM and explicitly synthetic W1C models; no hardware assertion. All seven immutable integration cases and515/740/12/2 regressions PASS.358 alignment mappings PASS, malformed odd mapping rejected,66 numeric aliases/36 segments/zero hash mismatches. [IRQ ownership](context-irq-ownership-4f111c.json); [IOM partition](iom-retained-island.json).

The retained IOM island contains18 bodies/3424 instruction bytes and28 literal bytes, with no unknown code gaps. Vendor SDK submission/full/uninitialize semantics are corroboration only and cannot be inserted as missing locked-firmware routines. Descriptor registrar430280 is the next genuine reachable initializer boundary; its disassembly shows12-byte pin/GPIO descriptors, not IOM TX submission.

## Reachable CMDQ ownership follow-up

[Callers, lifetime table and validation](cmdq-ownership/REPORT.md). Reserve42790a/post4279f0/cancel4279be have40 shared-image comparisons PASS. Generic term427ad6 has13 original/source comparisons PASS using an explicitly separate retained module because its source body is linker-GC discarded from the shared image. Allocation reserves supplied queue storage; cancellation only rewinds unpublished pointers/sequence; forced term stops issued queue register bits and clears claim, without drain/free/callback notification. MSPI wrapper423f64 force-terminates then clears slot. These are MSPI control-request edges, not standalone IOM submission/uninitialize. No hardware-safe reclamation is inferred.
