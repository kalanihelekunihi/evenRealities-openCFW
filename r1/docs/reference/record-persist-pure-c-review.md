# Health settings persistence wrapper in ordinary C

`runtime/native_record_providers.c` replaces the naked 0x73604 persistence
wrapper with a local three-word C buffer. The existing body remains canonical:
null input does nothing; otherwise it reads twelve cached bytes, copies the
three unaligned input words in order, reloads the live KV handle and writes
all twelve bytes. Read status does not gate the write. The entire buffer is
overwritten before the write, so captured incoming R1/R2/R3 values do not
contribute to the public result. Initial/private scratch contents are excluded.

Normal source, previous compiled object and locked stock firmware match in
1728 modeled KV-boundary cases plus 144 cases executing the cached KV and
memcpy implementations (5616 executions). Inputs include null, unaligned
records, aliases of both cached node payloads, partial/nonwriting modeled
reads, read/write error statuses, mismatched payload sizes, read callbacks
that change record bytes or the handle, and both interrupt-mask states.
Tests compare read/write order, length, write bytes, fresh handle selection,
callback-visible node state, final cached payload/dirty flags and guards,
input record state, saved registers, SP and masks. Source execution cannot
enter stock instructions. In the integrated cases only the critical-section
enter/leave callbacks are modeled; the stock KV/memcpy code executes for the
stock root and compiled C KV/memcpy executes for the C roots.

The API is void; incidental R0/R1/R2/R3 results, private frame addresses and
contents, live register allocation at callbacks, faults and private-stack
aliases/concurrency are not its typed contract. Arbitrary callbacks reading
the pre-read scratch bytes are not a supported output-buffer contract.
Physical flash programming or power-loss persistence is not verified by a
cached-class operation.

Four compiled defects are detected: omitted read, short record copy, stale
write handle and wrong write length. The clean baseline is rerun afterward.
Fresh REA bytes at the stock entry match the locked image. The companion JSON
records those bytes, evidence identifiers, build/probe hashes and the audit.
Both existing apply and persistence body sections and relocations are
unchanged. All 782 unrelated nongenerated objects retain their hashes; the
two generated bootloader objects retain allocated bytes and relocations.

All 785 R1 units compile without failures or duplicate strong symbols. Imports
remain 107 application and 22 bootloader linker metadata. Strict source
bootloader linking succeeds. The global source check retains the unrelated
unlisted G2 resident_rom_thumb_set.S failure. Full application linking remains
unfinished. No new source-plan qualification or byte-identity claim is made.
