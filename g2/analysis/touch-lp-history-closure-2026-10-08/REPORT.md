# Low-power history: producer composition, reset, safe offline interpretation

**766 cases pass**, comprising48 independent stock-reset comparisons,352 locked-project IRQ/source comparisons with decoder checks,108 sparse original-producer/decoder/reset compositions,192 new-decoder metadata guards,64 new-decoder read guards and2 original-only LP type7 bypass observations. No function-entry stubs. This is not766 stock-equivalence tests: decoder.c is a new offline/app interface with no claimed stock counterpart.

## What the firmware does

The actual project IRQ0x3948 reaches wrapper0x5c98, dispatcher0x5fba and registered ISR0x6780. Its LP branch calls history writer0x6530 only when common u16+22 (`lpDataSt`) bit0 is set. Reset-copied common context0x20000528 has that gate clear. Tuner initialization0x7e04 clears commandu16+2, tuner statebyte6, gateu16+22 and scan-statebyte28. It **retains samples, first/count/frame bytes24..26 and scan counter27**. Stale counts alone do not indicate a fresh enabled history.

The writer stores first/count at24/25 and floor(FIFO-used-low11/count) truncated to byte26. FIFO STATUS2 bit31 selects scan state1(reset) versus3(reset|valid); these are status flags, not evidence that software cleared all baseline/sample data. Data is little-endian uint16, frame-major, with two bytes per slot position. Disabled widgets still consume FIFO and advance the output pointer, leaving their history positions unwritten. Enabled CSD stores raw; CSX/ISX stores max(maxRaw-raw,0). Metadata does not encode the enabled mask. A decoder needs the enable state at capture, not a later widget state.

Actual LP descriptors0x20000808 contain(0,0),(0,1),(0,2),(0,3): four electrodes of widget0, method1/type7. Actual history pointer is0x2000065e. Sparse tests use separate synthetic mixed-widget descriptors, explicitly distinguish them from that four-electrode locked layout, check each frame/slot and retained holes, then run original reset and confirm interpretation is disabled without erasing history/counts.

## Buffer boundary and failure limits

The next known live object, LP descriptors0x20000808, is426 bytes after history. **426 is an upper window before another object, not the declared history allocation.** For four slots it holds at most53 complete frames (424 bytes). Only generated cycfg allocation/link-map evidence, or equivalent authoritative object bounds, can establish actual capacity.

| Synthetic FIFO used, four slots | Stored frames | Logical bytes | Observed behavior |
| --- | --- | --- | --- |
|212..215|53|424|212 FIFO reads/stores; remainder is not transferred|
|216|54|432|216 reads/stores; three stores touch LP descriptors; decoder rejects426-byte capacity|
|1024|0|0|quotient256 truncates to0; no FIFO reads/stores|
|2047|255|2040|1020 reads,418 stores; self-corrupted descriptors alter subsequent enabled checks|

These fault-injection states are supplied offline with the history gate enabled. They do **not** establish a reachable default backlog, physical FIFO chronology or hardware fault. In the largest case output also partly overwrites the deliberately bound ISR pointer. Comparison normalizes only untouched bytes of that pointer; overwritten bytes are compared exactly. No later IRQ using the corrupted pointer is modeled.

The new decoder requires caller-supplied capacity, checks locked-project first+count<=4 and complete span before reading, rejects null/out-of-range reads without modifying output, and returns UNWRITTEN without reading stale holes. It never corrects the producer or mutates firmware state. Use copied, stable metadata/history and an enabled-at-capture snapshot. It does not provide an atomic capture protocol, lost-frame detection or validity beyond the recorded flags.

## Is there a CPU history consumer?

No stock CPU history-processing loop was identified in this bounded investigation. Original filter initializer0x4e6c and preprocessing wrapper0x5c02 return for actual widget0/type7, without RAM changes or history reads in the two direct tests. The inner clamp0x5bc0 is not that guarded wrapper. Pinned public LP sensing source explains hardware filtering; common processing source does not consume ptrLpHistoricContext/lpNumFrame.

The narrow static scan finds the direct context+56 read at0x6546 in the writer, the initialized history pointer literal at0xb5f0, and gate clear0x7e0e. Other candidate +56 reads belong to PDL/SCB contexts;0x89d8 stores an unrelated EEPROM context field. Raw data at0xb4fc and later also decodes as candidate instructions and is not interpreted as a consumer. This scan is not exhaustive control-flow/alias proof. Generic tuner transport, indirect application aliases, external callbacks and hardware processing cannot be excluded by missing direct references.

Public tuner source at CapSense pin247a9a0f79eb976f144f5fbeb29488c1c2606517 documents COMM_EN/COMM_DIS for optional history export; it does not prove stock RunTuner is linked or reachable. Its verbatim TuInitialize body, compiled with explicit minimal ARM32 offsets/macros, reproduces the16 stock bytes at0x7e04 exactly at-Og/-O1, no relocations, one whole-body match. This raises prior demonstrated distinct selected public-source attribution286 bytes to302; it is not a full SDK build or uniquely identified producer/toolchain.

## Reproduction and next dependency

`build_offline.py` builds additive native source with the existing pinned public PDL object into an explicit scratch directory. `verify.py history.elf` runs original instructions/native source in Unicorn. `screen_public_reset.py` records exact-body attribution; `inspect_static.py` emits instruction excerpts and candidate/literal evidence. Firmware address/hash/config/reset provenance and reproduction receipts are retained beside this report. INDEX.md links preceding evidence. No production firmware, Git index or device was changed.

The buffer-size question stops at missing producer-generated cycfg allocation/link-map evidence. The physical backlog/enable/IRQ question needs an actual timing trace; unknown callbacks need their implementations. A useful independent dependency lead is selected public MSCLP ISR/interrupt wrapper attribution against0x5c98/0x5fba, followed by hardware filter configuration already reached through preparation—not invention of a CPU history consumer.
