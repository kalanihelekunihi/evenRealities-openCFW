# Independent review 6569/002

Disposition: **PASS_SCOPED**; `accepted:false`. The corrected packet revision 002 matches the pinned bytes and GNU decoding. The two routines at 0x4157F8..0x41581A and 0x41581A..0x41583C each preserve R4-R6 and return source-pointer distance. Both perform separate fresh loads of the set byte and source byte, so the result is conditional on those reads remaining stable. The first routine advances on a set byte and terminates at the first set/source NUL boundary; the second advances while the set byte does not match and terminates at first match/source NUL. The following 8-byte routine loads the word at 0x415FDC through its literal reference, stores the input R0 there, and returns R0. It is distinct from the two span routines.

No bounds, synchronization, or higher-level string purpose is assumed. The incorrect prior revision is superseded; no canonical files or gates changed.
