# Boot TON profile read order

The stock `0x42a1bc` TON adjust routine handles selector 0 by reading the
profile byte at native `0x42a1e2`, then separately reading the same profile
word at `0x42a1ea`. Selected C previously read the word first, then the
byte. `power_ton_adjust.c` now preserves the native byte-then-word sequence.
This matters if the source-owned profile is changed by another context
between reads; both accesses remain volatile.

The corrected target `unit_289.o` disassembles to `ldrb` at function offset
`+0x24` followed by `ldr` at `+0x26`. The native selector cases, major-8
override, field extraction, and two final MMIO RMW stores are recorded as a
reviewed full-body binding. The stock literal `0x42ac50` is the profile
base `0x20026ba0`, and the C addresses are that base plus the retained
offsets.

The cache maintenance body `0x41e348` also gained a reviewed full-body
binding after checking cache-disabled barriers, whole-cache set/way loops,
range line loops, operation-select MMIO addresses and barrier placement.
No cache source edit was needed.

The coherent `boot-coplacement-ton-readorder-round/receipt.json` is
`PASS_BOUNDED_LINK`: 373 selected units, 1,010 providers, three ROM imports,
34 callback relocations, 158,676 candidate bytes versus 148,599 stock.
Rooted header-only proof leads are **164/654**, down from 166; whole-catalogue
header-only leads are **262/903**. These counts are attribution work rather
than missing body counts. ROM, indirect-root, complete data/layout and
runtime/hardware equality remain open.
