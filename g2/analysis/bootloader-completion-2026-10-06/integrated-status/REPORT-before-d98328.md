# Bootloader source integration status

Latest passing immutable image: **85d6eb5362976d4d4a296ae08b92161bb979342d21002dfa2257c0f75f5e975f**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both before/after atomic modeled ROM-operation cuts preserve matching persistent state and reboot observables; both stock/source sides reach application reset entry without exceptions and with the generated fixture payload.567 frozen source/runner inputs and137 linked objects matched after completion. [Exact-image receipt](same-image-validation-85d6eb.json). Earlier459804 and bcc057 checkpoints remain preserved.

## New source closure

Reconstructed and linked context claim42c4c6 (114 stock bytes) and transaction42c988 (684 bytes). Source: `g2/components/bootloader/initializer_callbacks/context_claim.c`, `context_transaction.c`, `context_claim.h`. The source owns an eight-slot static NOLOAD pool at0x2001455c, stride0x8a8, total17728 bytes. It is SRAM storage, not executable retained firmware. Claim validates module/output/occupancy, initializes prefix/magic/module and returns the slot pointer. Transaction implements busy checks, register save/restore, power/clock call order and status propagation. [Readable behavior, layouts and call chain](context-claim-transaction/REPORT.md).

The shared startup now claims modules2,4,5,7 and executes four native transactions in each normal case. The module4 interrupt call receives a valid0x200167fc handle rather than null. Its mask255 includes rejected bit1, so it returns6; the caller ignores this status. This is a proven valid-handle branch, not successful physical IRQ activation. Successful mask4 simulated register writes are separately covered by direct tests.

[496 direct cases](context-claim-transaction-85d6eb.json) PASS, including failure-state preservation, register retention/restoration, busy/invalid guards, low-byte argument truncation, injected child failures and claim→configure→interrupt→powerdown→reclaim sequences. [52 interrupt cases](context-interrupt-85d6eb.json) also PASS on this exact ELF. Alignment334 mappings PASS; [regression](alignment-regression-85d6eb.json) rejects the known bad ac4b placement.

Claim uses no heap allocation; failure leaves pool/output unchanged. Transaction powerdown retains claim/magic, and duplicate claim still returns7. The stock platform caller does not release the slot on later configuration errors. A target uninitialize/release implementation has not been recovered or made reachable; no SDK-inspired speculative cleanup was added. Instance configuration42cc34, enable42c538, retry43048e and CQ adapters42c420/42c44e remain explicit edges. Numeric aliases stay73 because whole claim/transaction cuts were replaced by two narrower CQ dependencies; this count does not measure progress.

## Coverage and implementation accounting

Seven-case deduplicated original-byte footprint: **34304/148599 =23.08%** of the bootloader payload. This is modeled path coverage, not overall implementation completion or whole-OTA coverage. Unioning these seven traces with the exact-image496 direct traces yields34948 bytes; direct lower power/clock/CQ/wait calls are stubbed, so that broader metric has an additional model boundary. Six FP64 effects remain emulated; second-halfword NOP log aliases overlap existing modeled4-byte slots and are not counted twice.

[Ownership inventory](iom-source-ownership-85d6eb.json) explicitly maps and hashes854 original bytes across claim, transaction and the prior interrupt function. It is a partial three-function source audit. [Linked inventory](implementation-inventory-85d6eb.json) lists448 defined function symbols and74122 deduplicated compiled function bytes, with16 selected original-entry mappings. Aliases/local/veneer symbols are included. Compiled sizes cannot be divided by original firmware bytes as an implementation percentage; whole original extent/ownership coverage remains incomplete.

## Remaining work and limits

Next initializer gaps: actual instance configuration/enable/retry and their CQ/peripheral children. Other major gaps remain startup/runtime41fa50/41ba80, ADC/service dependencies, filesystem mutex lower kernel, ISR/notifications/events/deferred/cancel/termination, logger/fatal and accepted nonnull power configuration. Full vectors/assets/data/layout, compiler reproduction, source-complete build and byte equality remain open. [Provider checklist](remaining-providers-dceae3-worklist.md).

Shared tests execute native power/clock code through the new transaction. Direct tests use explicit lower-call cuts to isolate its control/state behavior. MMIO, ADC samples/readiness, scheduler/task delivery and resident-ROM page operations remain synthetic. Stop/reboot tests do not establish partial physical writes, reset/cache/IRQ timing, hardware recovery or application instruction execution. New SRAM BSS exposed a test-loader duplicate-map defect; it was fixed before the successful profiles, with the failure record and prior input freeze retained. No firmware ELF change was required for that loader repair.

This relocated ELF linked against137 prepared objects is not a clean whole-payload source build or bootable/byte-identical firmware. No commits, hardware writes or IAR authentication occurred. Historical report retained in [prior checkpoint report](REPORT-before-85d6eb.md).
