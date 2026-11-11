# Retained snapshot restore and shared hourly/stress state

Snapshot restore `0x59ee4`, accessor `0x589b0`, clear `0x5893c` and shared hourly restore `0x5acc4` now have C providers. The root validates the retained record, restores packed activity counters and HR/SpO2/HRV cache metadata, then clears the 52-byte snapshot and refreshes CRC over the same 964-byte record. It reuses the existing retained context, cache accessors and checksum implementation. The [REA accessor bytes](crash-snapshot-restore-c-rea.json) match the locked application.

The accessor requires a nonnull output, valid marker/CRC, nonzero snapshot flags and hour below 24. Its overlap-aware copy preserves the stock backward-byte, aligned-forward-word and unaligned-forward-byte cases. The root retains independent wrapping of activity's 12/10/10-bit fields, conditional HR average/latest updates, maximum/minimum selection, and seeding of empty SpO2/HRV slots. Latest-value metadata is restored even when those slots already contain values. Logging uses the stock strings, levels, arguments and live mode reads.

Integration uncovered duplicated storage: five average rows (40 bytes), six query/restore rows (48 bytes) and the stress prefix (80 bytes) represented overlapping stock memory as independent C objects. The new `native_hourly_state.c/.h` owns a single 120-byte aggregate: five rows at native `0x20016648`, followed by the stress prefix at `0x20016670`. Kind 5 aliases the prefix's first eight bytes. Average, query/restore, daily stress metadata and replay use this owner; the existing stress event assembly's literal now refers to this owner plus 40. No linker overlay or separate duplicate allocation is required. This removes 48 allocated bytes.

The [machine-readable receipt](crash-snapshot-restore-c-review.json) records:

- 1,904 stock/C restore, accessor, clear, accumulator and restore-to-query comparisons, including rejected records, all flag combinations, midnight/end-of-day, nonempty caches, counter wrap, null/aliased outputs and overlapping snapshot copies.
- 417 startup comparisons executing actual C retained helpers/CRC, replay, six cache writers, snapshot restore and shared hourly restore. These include 123 C snapshot calls and 738 cache writes.
- 2,012 average/hour, 1,156 daily-initialization and 1,620 daily-replay regression comparisons against the shared owner.
- Eight separately compiled defects rejected by runtime assertions: activity carry leakage, wrong HR minimum, overwriting nonempty SpO2, missing final clear, wrong hour boundary, lost copy overlap handling, rejected sixth accumulator and short snapshot clear.

The audit finds 727 prior objects identical. Changes in seven prior objects are confined to added helpers, shared-state references/allocations and one compiler-generated lifecycle constant-section label. Unrelated allocated contents and named relocations remain unchanged. `make sources-check` passes; 662 application and 74 bootloader units compile/compose with no failures or duplicate strong symbols. Application imports decrease from 158 to 157; bootloader imports remain 34.

The existing license-free R1 hybrid build still passes with 4,311 source-built bytes, 641,849 executable pull-through bytes and 248 resource bytes. It is not a complete source build. No source-plan selection is added or manually rewritten.

Direct restore tests execute actual C caches, retained helpers/CRC and hourly state; logging is modeled. Integration additionally models FlashDB, RTOS, time/calendar, allocation and iterator boundaries. Canonical cache accessors are nonnull; arbitrary pointer faults, asynchronous interrupts, physical persistence and complete firmware linkage remain outside this proof. The two storage subscription orchestrators remain unresolved below database startup, and other hardware/source dependencies remain unfinished.
