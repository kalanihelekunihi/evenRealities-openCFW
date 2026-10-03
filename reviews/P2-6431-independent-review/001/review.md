# Independent review 6431

Disposition: **PASS_SCOPED**; `accepted:false`.

I reviewed revision 002, which supersedes 001. Its packet file hashes and ECF2..ED60 source slice match. GNU Thumb decoding confirms mode 2 and mode 3 each reject null descriptor with status 6, then compare descriptor float+12 to the PC-relative float literal at EDF8. BNE returns 7, including unordered NaN. On equality, mode 2 copies fresh global words at offsets 0/4/8 to descriptor offsets 0/4/8, then zero-extends global byte 12 into a whole-word descriptor+12 store and returns zero.

Mode 3 also gates on the float comparison, then freshly copies global words 0 and 4, stores zero to descriptor+8 and +12, and returns zero. The copy accesses are sequential and interleaved with destination writes, so alias-sensitive behavior is preserved rather than described as a snapshot or bulk copy. The dispatcher default for u8 mode >=4 returns 6. The corrected mode-2 literal/reference is EDFC as in the current packet; the source body uses the separate float comparison constant EDF8.

This is scoped static control-flow and data-movement evidence. It makes no copy/API-purpose, floating-point runtime, or admission claim. No canonical files or gates changed.
