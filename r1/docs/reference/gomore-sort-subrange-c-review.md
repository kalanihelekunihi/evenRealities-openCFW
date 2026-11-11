# R1 native float subrange sort in C

`native_gomore_sort_subrange.c` implements `0x87600`, a dependency of the optical
peak matcher. REA confirms inclusive word bounds, wrapping base/count arithmetic,
four-byte elements and a tail call to native qsort with callback `0x58a40`.
The C provider uses the existing C comparator. The guarded provider-injected
utility retains its behavior under the `_checked` name.

The production object passes 1,205 stock/C replay pairs: 1,200 execute actual
stock qsort and comparator with random raw floats, NaNs, signed zeros and six
FPSCR settings; five model qsort to check wrapped or reversed bounds without
inventing safe bounds for the raw native ABI. Buffer writes, sort call arguments,
FPSCR, return completion, stack restoration and preserved registers agree.
A compiled wrong-element-size defect is rejected. This direct wrapper fixture
binds the stock comparator address on both sides; the existing statistics review
separately covers the C comparator and C qsort integration.

The C wrapper has a four-byte temporary private frame and a larger body than the
18-byte stock wrapper. Its qsort tail call restores that frame before transfer.
It is a behavioral candidate, not an instruction-identical selection.

The normal source build passes 698 units (624 application, 74 bootloader), with
no failures or duplicate strong symbols. Imports remain 179 application and 34
bootloader. Hybrid equality passes with 4,381 source-built executable bytes,
641,779 stock executable bytes and 248 resource bytes. The canonical plan is
unchanged. Peak matching, the optical root, complete source linking and physical
hardware validation remain open.
