# Touch SCB foundation: linked RX/TX cycle

The source-defined Cortex-M0+ module now links RX and TX register providers and four callable entry points. TX is registered in CORE_TESTS. No production provider, campaign state or official image was changed.

## Recovered contract

RX: read status +0x308 masked to 511, clamp requested element count, read width +0x300 mask0x18, pop 32-bit values from +0x340 and store low8/16 bits in order. TX: read CTRL mask0xc000 to derive16/8-entry depth, read status +0x208 masked511, subtract unsigned usage, clamp request, read width +0x200 mask0x18 and write low8/16-bit source elements as32-bit stores at +0x240. Raw TX preserves the original underflow for impossible occupancy; the checked API rejects it.

Counts are elements, capacities are bytes. Configuration and FIFO ownership must remain serialized by the caller. Checked failures preserve actual_out and buffer contents and perform no FIFO transfers. Register reads themselves are not claimed side-effect-free on real hardware.

## Final validation

`g2/build/foundation/touch-scb-final/comparison-reviewed.json` binds final verifier, source files and linked ELF. It passes eight original/linked RX comparisons and twelve TX comparisons without original callee stubs, plus six RX and nine TX added-adapter cases. Cases cover full/empty FIFO, count clamp, zero request, high status bits, both widths, both depths, UINT32_MAX request with valid occupancy and bounded malformed-status wrap including17 halfword stores. MMIO hooks assert32-bit access widths, register read order, FIFO values/order and complete guarded-memory equality. Optimized Python is rejected; output is exclusively created; ELF address/tables/segments are bounded.

Focused foundation:9 SCB methods+7 resource methods pass. Affected core aggregate:28 modules completed,172 method invocations,166 passes,0 failures/errors,6 method skips plus1 class-setup skip. Missing optional inputs are the reviewed CFW image, authenticated Apollo Ghidra corpus, reachable npm font dependency and protoc. Existing font negative tests can pass on an earlier npm error; they do not prove the intended local negative branches.

## Incremental scan

The original RX/TX traces cover190 unique instruction bytes,160 beyond the original30-byte wrapper execution. Relative to the earlier firmware-byte-map code-observation partition these are190 new nonoverlapping observations; relative to prior source attribution they establish0 new exact compiled upstream matches. Available Infineon source is a source-level dependency/contract; it is not a new binary match. Six validated L8 resources remain28872 pixel bytes, with0 newly classified resource bytes.

The broad rescan remains197000 reviewed stored bytes and490200 instruction-export bytes. New bounded execution evidence is separate from those receipt-defined metrics. All6 production payloads still use official blobs; no source-identical bundle or complete firmware target is established.

## Next shortcut

Prioritize the adjacent source-backed RX FIFO trigger-level leaf, then source-backed hardware HAL leaves and validated resources. RTOS scheduling/port behavior is foundational but needs missing state/configuration and ownership coordination. Binary-only codec/EM dependencies remain binary dependencies, not upstream source. Product-specific attribution requires positive evidence; module names are insufficient. EvenHub remains last. See next-priorities.json and upstream/interface.json.

Remaining hardware boundary: board startup/vector table, clocks, IRQ/DMA configuration, actual SCB address/wiring and concurrent FIFO semantics are not established by synthetic execution. No flashing, deployment, commits or firmware replacement were performed.

## Completed adjacent trigger-level cycle

`touch_scb_fifo.c/.h` implements the source-backed RX trigger-level setter and is now part of the linked simulator and CORE_TESTS. Five linked/original valid cases preserve the control register high24 bits and perform config read, control read, control write. Four invalid source cases return an error and do not write. The separate nine-case original oracle covers five valid and four BKPT paths (includingUINT32_MAX), authenticates the44-byte body and checks no control write before BKPT. Threshold-to-interrupt semantics remain untested.

Final comparison: `g2/build/foundation/touch-scb-trigger-final/comparison-reviewed.json`, current verifier/ELF/all source hashes verified. It retains all RX/TX cases and adds the trigger family:232 original bytes in linked valid comparisons; the separate invalid trace adds the2-byte BKPT, making234 unique original bytes overall (204 beyond the original30-byte wrapper). This is234 new observations against the older firmware-byte-map partition, not234 newly attributed upstream compiled bytes. Compiled upstream match delta remains0, and resource delta remains0.

Final tests:11 SCB+7 resource methods pass. All29 core modules completed:174 methods invoked,168 passed,0 failures/errors;6 method skips plus1 class-setup skip as documented above. Build-provenance and knowledge-delta now reference trigger-final. The remaining next hardware boundary requires board clock/IRQ/pin initialization evidence and serialized ownership configuration; threshold firing cannot be inferred from RAM-backed tests.
