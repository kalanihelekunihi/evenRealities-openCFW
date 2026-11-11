# Ordinary C reset-reason decoder

`r1_reset_reason_decode_and_report` now takes its single reset-reason input directly in C. The assembly entry and its scratch-register forwarding worker are replaced by one canonical body. The former scratch input only seeded unused upper bytes of a caller word; logged tags and callers remain masked to one byte. Local words are initialized. The architectural precise-PC capture primitive remains unchanged.

REA bytes authenticate the stock decoder against the official application image. **23,426 stock/C comparisons** pass across every supported reset-flag combination, additional random/unknown flags, retained-reader failures, all byte tags, caller values, scratch seeds, logging modes and live changes through explicit output pointers. Full log arguments, returned mask, stack restoration, saved registers and interrupt masks are checked. Logging and reader providers are modeled in this direct fixture.

**2,160 further stock/C comparisons** run the actual reset startup adapter, decoder, retained-record readers and CRC implementation. Valid records, invalid marker bytes and bad CRCs produce the same full logging sequence and cached reason. The retained record remains untouched, and the acknowledgment store contains the raw reset reason. The reset register is plain emulated memory: electrical reset behavior and hardware write-one-to-clear effects are not established by this check.

Five compiled defects are rejected: incorrect result mask, pin flag, caller admission, caller index and PC reader. The normal open-toolchain build compiles **855 units** and completes both relocatable compositions, with **61 application / 22 bootloader imports** unchanged. All **844 other nongenerated objects** are identical. Constant data and normalized relocation targets are unchanged, and the normal decoder object matches the direct probe. R1 source validation passes; manifest and source-plan selections are unchanged.

Physical reset retention, final linking/startup and boot remain unverified. Private frame aliases, incidental caller scratch values, APSR and faults/concurrency are outside the tested public contract. Byte identity is not the target of this change.

[Machine receipt](reset-decode-pure-c-review.json) binds the source, REA evidence, normal reports and ignored fixtures under `build/goal-r1-reset-decode-pure-c/`.
