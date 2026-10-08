# Bootloader source integration status

Latest verified immutable image: **52ca309db34cba5cf1c70f60d194b527277bdd5056e2331ad622a7b91d123915**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both stop/reboot persistence and observables match, and both stock/source reboot sides reach the fixture application reset entry without exception.574 frozen input files and143 linked objects remain unchanged. [Exact-image receipt](same-image-validation-52ca30.json). Earlier d98328 and19ff0c receipts/reports are preserved.

Observed original instruction-byte numerator: **35,468 /148,599 =23.86826%**. This is bounded modeled execution coverage, not implemented completion. Six FP64 effects are modeled; overlapping halfword logs are not counted twice. Source completeness/byte identity remain unproved. [Linked inventory](implementation-inventory-52ca30.json) has467 defined function symbols and76008 deduplicated compiled function bytes; these are not original-byte coverage.

## Semaphore closure

[Readable source behavior and ownership table](semaphore-REPORT.md). Native416762 rejects invalid counts/context/attributes, chooses static or dynamic binary/counting queues and reproduces stock initial-token failure cleanup. It calls existing native guard, queue factories and RTOS allocator. Boot startup creates a dynamic binary semaphore with maximum1,initial0 and stores matching handle0x20000568 at0x20027104. Counting419e62/419e94 and destroy41a470 C bodies inline into the selected wrapper; their independent fatal entries are not tested or separately retained in this ELF. [Partial308-byte source ownership](semaphore-source-ownership-52ca30.json).

1344 controlled-factory comparisons PASS across count/storage/allocation/put branches. Twelve additional comparisons run native queue construction and heap allocation/free/coalescing with controlled scheduler and put outcome: failed dynamic binary initialization restores81904 free bytes and counters1/1, leaving low-water81808. Static failure never frees caller storage. The tests do not establish real waiter cancellation or scheduling. No release policy beyond stock flag+0x46/free is invented.

740 IOM child comparisons and two conditional subtype-preserving CQ cleanup comparisons PASS on this exact ELF. Alignment348 mappings PASS; known bad odd-address image rejected. Numerical linker aliases are66. Manifest shows36 segments and zero source hash mismatches. Older196608 NVIC and496/52 claim/IRQ receipts remain tied to their original exact images, not relabeled here.

## Closed versus open initializer paths

Native IOM claim42c4c6, transaction42c988, configuration42cc34, enable42c538, retry43048e, interrupt42c63a, interface/clock helpers and CQ initialize/enable/disable42c3e2/42c420/42c44e remain integrated; NVIC430470 and semaphore416762 are now closed. Failed IOM enable can retain a claimed CQ; the synthetic subtype-dependent retry outcomes do not prove a hardware fault or safe release.

Descriptor registrar430280, ADC/service children and lower lifecycle/scheduler alternatives remain unresolved. Asynchronous IOM publisher42c45a and service42c6f8 are still unimplemented boundaries; [new publisher pseudocode](iom-publisher-next.md) identifies32-byte records and ordered register writes, without head advancement or release in the publisher body. Release/uninitialize remains unproved. [Provider checklist](remaining-providers-dceae3-worklist.md).

Synthetic MMIO, ADC, scheduler/task delivery and atomic resident-ROM operations limit conclusions. Physical partial writes, hardware IRQ/recovery and application instruction execution are not demonstrated. This relocated ELF links prepared objects; it is not a clean whole-payload source build or byte-identical firmware. No commits, flashes or IAR authentication occurred.
