# R1 latest HR, HRV and SpO2 sample readers in C

`native_health_latest_samples.c` now expresses the output clearing, provider
selection, status handling and field copies for `0x8d6ac`, `0x8d858` and `0x8e524`
in C. Three small entry bridges retain the native saved-word frame. The
[review receipt](health-latest-c-review.json) binds source/object hashes, REA bytes,
differential fixtures, negative controls, qualification and normal composition.

Null output returns zero without clearing the saved input words. Otherwise the
reader clears its output using native widths: HR clears two words, HRV clears
two halfwords and a word, and SpO2 clears only byte 0 and the word at offset 4,
leaving bytes 1–3 intact. It clears the two local packed words, calls the correct
provider and copies data only for nonzero provider status. HR/SpO2 copy byte 0
and an unaligned timestamp word from local offset 1 to output offset 4. HRV
copies a halfword and the timestamp word from local offset 2. The complete raw
provider return is retained.

The entry bridges preserve the local frame at caller SP-16 and restore its
possibly provider-written or aliased words into R2/R3. On null input those words
remain the incoming R2/R3 values. The C worker adds stack depth: provider calls
use 32 bytes versus native 16, while the exposed packed pointer is unchanged.
This remains an explicit assembly boundary rather than a claim of fully C entries.

The existing packed providers now live in `native_health_latest_packed.c`, one
implementation per function. Their machine bytes and relocation records are
identical to the previous unit. Separating them preserves stock's external
raw-return boundary: the first same-unit C probe allowed the compiler to normalize
a modeled high-bit return to 1. The split version passes that check without an
assembly constraint or changes to packed-provider behavior. It adds no RAM globals.

The fixture passes 747 paired native/C cases: 603 execute the actual packed
providers, including logical faults, and 144 model partial writes and raw return
words. Cases cover missing/nonzero samples, null and unaligned destinations,
destinations overlapping source fields or the exposed frame, preserved SpO2
padding, raw R0, restored R2/R3 and interrupt masks. Callee-saved integer/FP
registers, SP, masks and FPSCR are checked; other caller-clobbered registers,
APSR and private worker stack are excluded. Six compiled defects are rejected:
normalized return, wrong timestamp offset, wrong HRV halfword, incomplete frame
clear, excessive SpO2 clearing and ignoring provider status. Physical and concurrent
behavior remain unverified.

All 633 units compile and both relocatable compositions succeed without duplicate
strong symbols. Of the previous 632 objects, 631 remain unchanged and the reader
unit changes; the separated provider unit is new. Application/bootloader import
sets remain unchanged at 172/34. Manifest checks pass. None of the three readers
passes instruction qualification. The exact plan remains at 4,313 source-built
bytes; a fresh hybrid application matches the locked artifact with 641,847
executable pull-through bytes and 248 resource bytes. Complete source-only linking
and firmware hardware validation remain unfinished.
