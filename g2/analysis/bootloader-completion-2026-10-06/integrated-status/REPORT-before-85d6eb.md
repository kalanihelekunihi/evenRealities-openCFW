# Bootloader source integration status

Latest complete seven-case checkpoint: **bcc057db988238f1209f2e9aead5e699156b7050402ad6c08b9f667d1c964da7**. Its own normal2, malformed3 and interruption/reboot2 cases PASS. Both before/after atomic modeled ROM-operation interruptions retain matching persistent pages and produce matching reboot observables; both sides reach the application reset entry without an exception and with the generated fixture payload. Frozen563 files and135 linked objects matched after completion. [Receipt](same-image-validation-bcc057.json). Previous459804 also completed its own seven cases and remains preserved.

This checkpoint replaces the initializer context interrupt provider with compiled source. Alignment332 mappings and52 direct leaf cases PASS. All seven cases PASS on that exact ELF. The alignment regression also rejects the known bad ac4b image. No older seven-case result was transferred.

## Concrete recovered source

The linked paths include initializer table/qsort/callback bodies and source-defined callback/configuration data; HAL control requests30/34; NOR timing/address/serial handlers; kernel-state wrapper/runtime flags; startup/reset, DFU update/error handling, littlefs and bounded storage/peripheral chains. Context interrupt42c63a is now linked natively at source33a1c. Null/bad magic returns2, forbidden mask bit1 returns6, otherwise the source ORs the module enable register and returns0. Full behavior and limitations: [native helper evidence](native-context-interrupt-bcc057.md).

The initializer previously passed row4 instance instead of transfer; corrected source matches the original4305ca load. Explicit linker/assembly alignment fixes the prior ac4b odd Thumb placement; old failing and passing snapshots remain preserved. NOR valid-wire comparisons prove descriptor length, FIFO count/module and command fields; raw unused final-word padding differences remain diagnostic rather than raw MMIO equality.

## Coverage and implementation accounting

bcc057's seven-case deduplicated observed original footprint is **34108/148599 bootloader bytes (22.95%)**. The union uses actual byte addresses across profiles. Six FP64 second-halfword NOP log aliases overlap modeled4-byte slots and add no unique bytes; the intermediate459804 summary was corrected from34110 to34098 by removing12 duplicate bytes, with no receipt changes. This describes tested modeled paths, not overall implementation completion. Direct suites cover additional overlapping branches; their counts are not summed into this metric. No whole-OTA percentage is claimed.

[Implementation inventory](implementation-inventory-bcc057.json) lists444 defined linked function symbols,73366 deduplicated compiled function bytes and a partial explicit original-entry map. It includes aliases/local/veneer symbols. Compiled sizes cannot be divided by original firmware bytes; a complete original function extent/ownership map is still needed for an implementation percentage.

## Remaining work and model boundary

The bcc057 linker retains73 numeric bindings. Startup/runtime orchestration41fa50/41ba80; initializer context claim/config/retry, NVIC, ADC/service children; filesystem mutex lower kernel and ISR/notification/event/deferred/cancellation/termination paths; logger/fatal and accepted nonnull power configuration remain open. [Provider checklist](remaining-providers-dceae3-worklist.md).

The normal initializer fixture passes `(handle=0, mask=255)` to the newly native helper and executes the null-handle return2 path; valid handle register writes are covered by the separate52-case simulated-MMIO test. This is not proof that the real context handle is populated or interrupts activate. Six stock FP64 instruction effects are emulated. ADC readiness/samples, scheduler/task delivery, peripheral completion and resident-ROM storage calls remain synthetic. Stop/reboot tests cut around atomic modeled page operations; physical partial writes, reset/cache/IRQ timing, hardware recovery and application execution remain unverified.

Relocated test ELF and134/135 captured prepared objects are not a clean whole-payload source build, standalone bootable firmware or byte-identical bundle. Vectors, remaining data/assets/layout, full source closure and compiler reproduction still require work. No firmware flashing, commits or credential access occurred. Previous report retained in [historical report](REPORT-before-bcc057.md).
