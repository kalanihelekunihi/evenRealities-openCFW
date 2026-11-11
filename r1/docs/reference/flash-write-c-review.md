# FlashDB write adapter in ordinary C

The FlashDB write adapter at stock `0x3f05a` no longer uses fixed-register
bindings or empty assembly constraints. It reads the file-mode byte before the
partition pointer, returns error 2 for file mode, forwards four full FAL words,
maps a signed negative result to error 3, and returns zero otherwise. The public
sync argument remains unused. The read path now owns defined scratch buffers;
it no longer needs this adapter to reproduce old private stack words.

All 3,282 direct stock/C comparisons pass, covering all mode bytes, signed
results, unaligned inputs, provider mutations, ignored sync, shared memory,
null-database fault address, return SP, integer callee-saved registers and masks.
Every native instruction byte executes. Private stack aliases, provider-entry
scratch registers and saved-frame contents are outside the C contract.

Another 1,728 comparisons execute the actual C write adapter, FAL partition
write and cache lookup with the final flash driver and diagnostics modeled.
Two compiled defects changing the mode error and treating positive results as
failure are rejected.

All 852 units compile and both relocatable payloads compose. All 842 nongenerated
objects, the other ten utility function bodies, data bytes and import sets are
unchanged. R1 manifest validation passes. Imports remain 66 application and 22
bootloader symbols. This does not establish physical flash writes, fstorage
completion, full linking, startup or boot.

[Machine evidence](flash-write-c-review.json) binds REA, sources, normal build,
probes and negative controls. It supersedes the fixed-frame requirement in the
historical [write frame review](flash-write-frame-review.md) for this implementation.
