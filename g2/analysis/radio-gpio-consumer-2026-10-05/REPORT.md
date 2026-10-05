# Radio pin117: registration → IRQ dispatch → scheduler event

Implemented a bounded vertical consumer in `g2/components/foundation/radio_gpio/radio_gpio.c`, with reusable declarations, a callable linked target and fresh original-instruction comparisons. This is reconstructed C linked with the existing unchanged Ambiq SDK GPIO bodies and real PRIMASK provider. It does not replace full radio boot or the scheduler.

## Recovered behavior and implementation

| Stock location | Implemented contract |
| --- | --- |
| `0x4b49a8..0x4b49b6` | Register channel0 pin117, handler `0x4b4a99`, argument NULL. New source registers its reconstructed callback instead of embedding the stock executable address. |
| `0x4b80be..0x4b80ea` | Snapshot seven channel0 raw status words; read IRQ59 raw status again; clear that mask before servicing it. Ignore helper statuses. |
| `0x52dd58..0x52dd6a`, `0x52dd6a..0x52dd7c` | Enable/disable channel0 pin117 through stock GPIO interrupt control; masked read-modify-write preserves other bits. |
| `0x4b49b6..0x4b49c8` | Enable GPIO117, write IRQ59 priority4 (IPR byte0x40), set NVIC ISER1 bit27. Integrated with registration as IRQ setup tail. |
| `0x4b4a98..0x4b4ab2` | Increment RAM counter at `0x20074640` modulo2^32; read handler ID byte at `0x20074fcb`; submit event1 through `WsfSetEvent` at `0x52b91e`. |

The implementation preserves the unused seven-bank snapshot's observable MMIO reads, with saved PRIMASK restored before the bank3 read/clear/service sequence. This specializes the stock `0x4812f6` snapshot helper to this consumer's channel0/raw branch; other modes are not reimplemented. The existing real GPIO leaves perform bank3 reads at `0x40010564`, W1C at `0x40010568` and callback table lookup at row3 bit21. Pin117 callback/argument slots are `0x200683fc` / `0x20068afc`.

Readable C is the pseudocode companion. Its callback deliberately ignores its argument; it retains fixed stock state locations and expects caller initialization. The source does not implement HCI transfer inside the ISR: it counts the interrupt and requests deferred work through the scheduler. A replacement scheduler adapter must reproduce actual WSF behavior; the simulator's provider is an explicit external-call fixture, not a production implementation or proven C typedef contract.

## Fresh validation

`make -C g2 radio-gpio-simulator` builds a callable ARM32 ELF. `radio-gpio-simulator-test` invokes the new verifier with a fresh output path. Compilation uses the established Cortex-M4 compatible Thumb2 subset for M55 execution because installed Unicorn does not implement some compiler-emitted M55 instructions; it is not a hardware architecture change or byte-equal compiler claim.

`g2/build/foundation/radio-gpio-simulator/comparison-reviewed.json`: **180 original/source comparisons pass**. The original instructions run without GPIO/callback/helper stubs. Only `WsfSetEvent` submission is intercepted on both sides; W1C is synthetic. Inputs cover prior PRIMASK0/1, handler ID0/7/255, counters0/0x7fffffff/0xffffffff, zero/unregistered/pin117/mixed/all pending masks. EN is zero for ISR/setup cases, mixed0x80400001 for enable cases and0xffffffff for disable cases: this deliberately proves the ISR uses raw pending status rather than filtering by enabled bits. Checks compare MMIO order/value/PRIMASK, callback publication order, full normalized callback tables, final registers/counter, scheduler arguments and counter-before-submission. The standalone registration comparison ends at `0x4b49b6`; integrated setup executes the stock tail through `0x4b49c8`. Individual pin enable/disable wrappers and their original GPIO control dependency execute. Earlier boot initialization does not execute.

Fresh focused tests: **36 passed**. Fresh aggregate: **186 passed, zero failures/errors**, six method skips plus one class setup skip, 34 modules. Three new repository tests authenticate locked consumer bytes, enforce build/symbol integration, and reject optimized-Python verification.

The new comparison observes820 original instruction bytes, **502 new after deduplicating prior GPIO/critical bodies**. This includes44 ISR,26 callback,14 registration-slice and152 snapshot-branch bytes, plus266 bytes across pin enable/disable, setup tail, GPIO control branch and NVIC wrappers. Cumulative original trace evidence is1894 unique bytes across payload identities; this does not measure complete firmware coverage. There are25 foundation C/header files and six callable target profiles; profiles share source and are not production firmware. Fully blob-free production payloads remain0/6. No source-built byte-identical bundle is proven.

The firmware image, original manifest, workflow state and open_cfw.py hashes remain unchanged. Existing source and earlier evidence packets were preserved; new evidence is a separate overlay and cumulative inventory. No commits, staging, flash or deployment were performed.

## Ownership and remaining boundary

Registration publishes handler before argument without its own critical section. Callback service reads live table slots, so publication or replacement during dispatch is not atomic by this API. This callback uses NULL argument and fixed firmware globals, but that does not prove concurrent unregister/IRQ delivery safe. No allocation, release or lifetime handoff occurs in this consumer. Disabling GPIO117 does not clear its pending STAT bit, unregister its callback, disable NVIC or drain queued scheduler work. Because this ISR consumes raw status, a pending bit still dispatches when EN is zero in the serialized tests; actual post-disable interrupt arrival requires hardware/scheduler evidence. The bounded tests are serialized; they cannot establish teardown quiescence, interrupt arrival timing, scheduler queue ownership, counter race safety, or reentrancy.

Stock boot registers the callback, enables GPIO117 through `0x52dd58`, then sets IRQ59 priority4 and enables IRQ59. These operations are now implemented as a bounded IRQ setup tail. Stock disable wrapper `0x52dd6a` clears only GPIO117 EN bit21. Full boot/teardown state remains outside this source increment. Physical pad configuration, physical NVIC delivery, scheduler initialization and the deferred HCI handler's transfer behavior are not yet implemented or verified. Static consumer findings and exact teardown-search limits are in `original/`.

The next useful increment is the actual WSF event producer/consumer contract and the deferred HCI transfer loop. Do not infer physical delivery or callback publication safety from the synthetic comparator.

## Navigation

- `original/`: authenticated original consumer analysis and bounded call-site search.
- `review/`: independent review.
- `dependency-provenance.json`: locked image/ranges and exact upstream dependency attribution.
- `cumulative-inventory.json`: deduplicated source, ELF and trace evidence.
- `validation-summary.json`: fresh tests and explicit external-call limits.
- Prior GPIO, critical, CMDQ, MSPI and touch reports remain in sibling `ambiq-gpio-irq-2026-10-05`, `ambiq-critical-2026-10-05`, `ambiq-cmdq-disable-2026-10-05`, `ambiq-mspi-lifecycle-2026-10-05`, `ambiq-mspi-cycle-2026-10-05` and `touch-mmio-cycle-2026-10-05` directories.
