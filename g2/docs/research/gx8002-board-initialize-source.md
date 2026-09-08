# Board startup source

The board entry at package0x17CD0/runtime10025CBC and register helper at
package0xD200/runtime10203C74 compile byte-exact from source,20 bytes each.
The first calls reset_reason, conditionally calls the reconstructed flash
resume initializer when the unsigned result is at least2, then always calls
the register helper. It preserves the original four-byte saved-link frame.
The helper writes0x59 in order to A0005040, A0005044, A0005048 and A000504C.
No meaning beyond these observed writes is assigned to those registers.

Normal-Os, priority allocation and disabled sibling-call optimization emitted
22 bytes for the board entry. The source uses GNU asm-goto to express the
unsigned threshold as CMPhSI and BF directly. These are source-authored named
instructions implementing that condition; no machine byte sequence is embedded.
The call uses the actual void-pointer-returning flash initializer declaration;
its return value is ignored, as in the original. Both dependencies already have
separately qualified source implementations.

The verifier rebuilds the two functions and first requires complete byte
identity with authenticated stock. It then decodes the candidate and compares
1572 cases with an independently specified event trace: reset query, optional
resume, register helper and four writes. Cases include0,1,2,3, signed-boundary
values,256 deterministic values, two register seeds and three resume results.
The register helper executes within the board model. Every call requires the
saved frame and every return preserves all callee-saved registers. Five tests
reject absent frames, unknown helpers, wrong return frames and uninitialized
conditions, and check threshold boundaries.

The two functions are registered for integration. These checks establish the
recovered control flow and writes, not whole-board runnability, peripheral
semantics or interrupt timing. The remaining firmware goal stays active.

Board entry and register helper integrated successfully:266 tests pass. The
codec now has121 C functions /137 code occurrences,24 source-data regions and
161 total replacement regions. Ownership is8428 C bytes,2216 source data,
80 metadata,326 fill and315042 retained bytes. Codec SHA remains
d226af97d7bb35b46852bf1d4bd839eb5bb6228e16eb3e91747e4efc0b35ad54.
Both new functions are byte-exact; only ownership and published metadata change.
The source-only and hardware qualification goal remains active.
