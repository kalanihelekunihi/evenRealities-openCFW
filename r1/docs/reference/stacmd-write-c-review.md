# Direct C STACMD write frame

The write-frame candidate at stock entry `0x28c6c` now runs directly in C in `r1/src/application/board/native_stacmd_frames.c`. Its fourteen-byte naked bridge and private `stacmd_write_frame_body` are retired. One empty compiler constraint restores raw R3; it emits no instructions. The read-frame bridge and worker remain unchanged. This uses compiler-specific register binding, not portable ISO C.

Stock saves incoming R3 at caller SP minus 24 and reuses that word for every ACK. The initial word contains the input byte pointer; partial or absent ACK writes must retain the unwritten bytes. The C frame contains this initialized volatile word and a private volatile header word. Recorded Clang and GCC9 each use eight local bytes plus sixteen saved bytes, passing the ACK address and calling providers at native depth 24. Private save slots differ. A straightforward C version produced a 32-byte frame and was rejected.

The C path retains command rejection, pre-idle header truncation, header/data bit writes, ACK status handling, unsigned parity comparison, signed length gating, the byte reload after ACK callbacks, final idle and fresh release configuration reads. Every return reloads the ACK word into R3. The private header is C storage rather than a claim that native saved-register memory has that meaning.

REA read the complete 136-byte envelope: 130 instruction bytes, two padding bytes and one four-byte literal. Raw Thumb decoding independently establishes the saved R3 word, provider calls, signed branch and return. The stock application SHA is checked by the executable fixture.

Both recorded Clang and GCC9 pass **3,824 paired cases / 7,648 executions each**. The fixture executes actual parity and models idle/write/drive/ACK/release providers. It checks native ACK address and every provider's 24-byte depth, raw R0/R3, controlled buffer/configuration state, provider sequence, final callee-saved registers and interrupt masks. Cases cover command/register truncation, zero-to-three-byte and signed-negative lengths, callback mutations, nonzero status words, partial ACK writes, failures and parity mismatches. All 256 byte values are covered with byte and release-configuration mutations.

Each compiler configuration also passes **219 paired full-protocol cases** using actual frame, transmit, receive, recovery and delay units with probe C GPIO callbacks. The GCC run replaces the frame unit; the other units retain their normal objects. Checks cover transfers, command rejection, parity mismatches, timeout phases, GPIO operations, samples, NOP counts, output guards and final ABI state. This establishes bounded protocol behavior, not physical timing.

Negative controls reject a zero ACK seed, a stale byte retained across an ACK callback, the wrong ACK address, unsigned length handling, the previous bridge's deeper provider calls and the straightforward 32-byte C frame. All 575 other objects and the read-frame bridge/worker bytes and relocations are unchanged.

Active provider saved-register contents, private save slots/header storage, saved-slot aliases, R1/R2/R12, APSR, return-address bits, arbitrary faults and exceptions are excluded. Actual wire timing, electrical behavior, concurrency and physical-device operation remain unverified.

All 576 R1 source units compile and compose without new failures or duplicate strong symbols. Imports remain 164 application / 34 bootloader. Four generic and four GCC9 profiles compile with normal flags, but select no exact regions. The manifest and source plan remain unchanged. The direct Clang write candidate is 146 bytes; stock instruction identity is not established.

The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: 3,961 source-built bytes (including assembly and data), 642,199 fallback bytes and 248 resource bytes. Source completeness remains false.

Evidence: [stacmd-write-c-review.json](stacmd-write-c-review.json). Local probes and negative controls are under ignored `build/goal-r1-stacmd-write-c/`; the normal report is `build/sources-goal-r1-stacmd-write-c/report.json` and hybrid report `build/hybrid-goal-r1-stacmd-write-c/build-report.json`. This supersedes the write bridge described in the [earlier ACK-frame review](stacmd-c-write-frame-review.md).
