# Direct C STACMD read frame

The read-frame candidate at stock entry `0x28bb0` now runs directly in C in `r1/src/application/board/native_stacmd_frames.c`. Its eighteen-byte naked bridge and private `stacmd_read_frame_body` are retired. The frame module now contains no naked functions or nonempty assembly instruction strings. Two empty register constraints remain in the read body and one in the write body. These emit no instructions; their fixed register bindings are compiler-specific rather than portable ISO C.

Stock saves incoming R2/R3 as distinct ACK/data words at caller SP minus 48/44 and restores incoming R12 on every return. The C local frame retains both initialized words, incoming R12 and the header. Recorded Clang uses sixteen local and thirty-two saved bytes. GCC9 uses sixteen local bytes, four alignment bytes and twenty-eight saved bytes. Both retain native provider depth 48 and the separate word addresses. Private save layouts differ: C header/R12 storage is not a claim of native save-slot identity.

The C path preserves command rejection, header construction after the first idle, header ACK and parity checks, signed length gating, eight-bit accumulation, partial-byte storage on read failure, the volatile output-byte reload before parity, the inter-byte drive and final idle/release. Every return reloads ACK/data into R2/R3 and restores incoming R12.

REA read the complete 188-byte envelope: 184 instruction bytes and four literal bytes. Raw Thumb decoding independently establishes the saved words, calls, signed branch, partial-byte failure store and register restoration. The executable fixture checks the locked application SHA.

Both recorded Clang and GCC9 pass **1,764 paired cases / 3,528 executions each**. Actual parity executes; idle/write/drive/ACK/bit/release providers are modeled. Checks compare R0/R2/R3, incoming R12 restoration, ACK/data addresses, every provider's 48-byte depth, controlled output state, provider sequence, final callee-saved registers and interrupt masks. Cases cover header truncation, zero-to-three-byte and signed-negative lengths, partial/no writes, full-width status values, failure positions, nonbinary sampled words, output-byte mutations and five additional full-width R12 seeds.

Each compiler configuration also passes **219 paired full-protocol cases**, executing actual frame, transmit, receive, recovery and delay units with probe C GPIO callbacks. The GCC run replaces the frame unit; other units retain their normal objects. Checks cover transfers, command rejection, parity mismatches, timeout phases, GPIO operations and samples, NOP counts, output guards and final ABI state.

Negative controls reject a zero ACK seed, lost R12, a stale byte used after an output-store mutation, merged ACK/data storage, unsigned length handling and the previous bridge's deeper provider calls. All 575 other objects and the write-frame bytes and relocations remain unchanged.

Active provider saved-register values, private stack/save slots and header/R12 storage identity, aliases into saved slots, R1, APSR, return-address bits, arbitrary faults and exceptions are excluded. Protocol results and NOP counts do not establish equal cycles, electrical timing, concurrency behavior or physical hardware operation.

All 576 R1 source units compile and compose without new failures or duplicate strong symbols. Imports remain 164 application / 34 bootloader. Four generic and four GCC9 profiles compile with normal flags, but select no exact regions. The normal manifest and source plan remain unchanged. The direct Clang read body is 208 bytes; stock instruction identity is not established.

The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: 3,961 source-built bytes (including assembly and data), 642,199 fallback bytes and 248 resource bytes. Source completeness remains false.

Evidence: [stacmd-read-c-review.json](stacmd-read-c-review.json). Probes and negative controls are under ignored `build/goal-r1-stacmd-read-c/`; normal report `build/sources-goal-r1-stacmd-read-c/report.json`, hybrid report `build/hybrid-goal-r1-stacmd-read-c/build-report.json`. This supersedes the bridge described in the [earlier separate-word review](stacmd-c-read-frame-review.md).
