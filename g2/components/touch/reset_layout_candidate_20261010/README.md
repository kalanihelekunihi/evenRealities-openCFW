# Touch reset table source/layout candidate

`reset_prefix.c` source-defines the bounded boot register write and interrupt
mask at `0x4674..0x467e`; `reset_suffix.c` source-defines vector relocation
and VTOR at `0x467e..0x4692`; `reset_tables.c` source-defines the word copy
and zero loops at `0x4692..0x46d6`. `layout_fixture.ld` demonstrates table,
data load, RAM data and BSS addresses with synthetic input arrays. It is an
isolated linker fixture. The three sources also link relocatably with the
existing 45-unit archive. `reset_owned_data.c` and `owned_islands.ld` place
25 independently source-owned reset bytes in five disjoint original-address
segments. The other 939 initialized bytes are not provided, so no full
executable image is produced. Evidence and comparisons are in
`g2/analysis/touch-reset-layout-candidate-20261010`.

## Current attributed reset-data scope (2026-10-11)

The 25-byte result above is the original fixture scope. Subsequent source
islands now total **480/964 reset-copy bytes**, leaving **484 bytes**.
They include slot descriptors/pointers, PM descriptor, common context,
three widget contexts, slider position, nine sensor contexts, the LP channel,
application PM descriptor/threshold, source-built GCC init/fini entries, and
three natural alignment bytes between the typed MHz/kHz objects, and the
slider position-filter history header.
The channel additionally owns 32 ROM bytes of electrode/pin descriptors and a
four-byte MSCLP driver lock outside the reset-copy range. All referenced fields
and pointers are verified in bounded compiled-source fixtures, with receipts in
`g2/analysis/c-source-completion-20261011/touch/`. The selected Touch candidate
has 54 C units, all compiled, and zero unresolved strong providers; the GCC
CRT additionally carries four optional weak references.

These fixtures do not provide final firmware placement or close the historic
buffer allocation. Complete image reconstruction and hardware operation remain
open.
