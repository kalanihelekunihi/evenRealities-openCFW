# R1 optical history range in C and active-FP verification

`native_wear_history_range.c` supplies stock `0x3d06c` as ordinary integer C.
The [review receipt](wear-range-c-review.json) binds REA bytes, production hashes,
native comparisons, FP-context diagnostics and followup replays.

Maximum starts at the existing previous-history word. Minimum starts at that word
when nonzero, otherwise at one billion. Stock's nonzero uint32-to-binary64-to-uint32
round trip is exact; the C implementation removes it. The active count is captured
as a byte, then an unchecked unsigned scan starts at the history prefix and returns
maximum-minus-minimum with uint32 wrapping. Zero count and zero previous value thus
return wrapped negative one billion. Counts through 255 can read beyond the nominal
20-byte prefix. No new RAM is owned.

The fixture passes 1,920 paired comparisons executing the actual stock binary64
conversion helpers, with previous-value and count boundaries, unsigned extrema,
six history patterns, interrupt masks and preserved FPSCR. Six compiled defects
are rejected: wrong sentinel, missing maximum seed, signed minimum, signed maximum,
count capping and reversed subtraction. Public memory remains unchanged; R0,
preserved registers, SP and interrupt masks are checked. Caller-clobbered registers,
APSR and private stack residue are excluded.

The first FP-state check failed because the emulator initializes FP context on its
first FP load/move and clears a debug-preloaded FPSCR. A four-instruction probe
isolates that behavior; a load followed by architectural VMSR and another load
preserves the programmed state. The final fixture initializes context with a single
load before setting FPSCR, matching the statistics-before-decision calling path.
The integer replacement does not reproduce first-use FP-context activation; that
side effect is outside this candidate's proven contract. Physical startup remains
unverified.

This exposed a limitation in the earlier statistics fixture: labeling cases FZ/DN
or rounding modes did not prove those settings survived first FP access. A fresh
replay with initialized context passes all 1,910 direct statistics cases and 1,624
integrated motion cases using unchanged production objects. Direct replay has
404 bounded prefixes, versus 408 in the earlier setup; they remain prefixes, not
completed calls. No production change was needed. Other historical FP receipts
are not silently reclassified as having this stronger setup.

All 647 units compile and both relocatable compositions pass without duplicate
strong symbols. All 646 earlier sources and objects remain unchanged; import sets
remain 173/34. This helper fills a deeper on-decision source route and does not
resolve an existing composition import yet. Manifest validation passes. It does
not qualify as exact. The source plan remains at 4,345 source-built bytes; a fresh
hybrid matches the locked application with 641,815 executable pull-through and
248 resource bytes. Complete source-only linking, full byte identity from C and
physical/concurrent hardware validation remain unfinished.
