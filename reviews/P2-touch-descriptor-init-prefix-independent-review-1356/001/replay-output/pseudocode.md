# Touch descriptor initialization prefix 4C7C

This packet covers the nonnull prefix4C7C..4CB2 only. Save a six-word frame and retain descriptor. Load context pointer from descriptor+8. Clear context bytes74/75 and words0,4,C,8 in that exact order. Load descriptor+12 pointer, then its first word as row base. Iterate exactly three rows with stride3C: freshly read row byte23, OR6, store it, advance. Stop at4CB2 before subsequent initialization. No deeper helper is reached by this prefix.

Eighty-one original-instruction fixtures vary each of three row bytes across0/A5/FF and initial contextfill across0/A5/FF. Exact ordered writes are independently modeled. Null descriptor, invalid pointers, remaining initialization, return/frame restoration and physical row meaning remain unresolved. This is prefix evidence, not full helper pseudocode or ownership closure. No canonical admission or C implementation.
