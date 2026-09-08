# GX8002 GPIO direction and level candidates

Authenticated NationalChip GPIO interface at commit
8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 supplies enum declarations. The
reference gpio_mini.o is comparison-only; no object bytes are linked.

Stock direction entry package0xf4b0/runtime0x10205f24,100-byte envelope.
The reconstructed C masks port to five bits. OUTPUT(1) clears the selected
bit in register0xa0001008 then sets it in0xa0001000. INPUT(0) clears the bit
in0xa0001000 then sets it in0xa0001008. HIZ(2) clears in0xa0001008 then
0xa0001000. Other direction encodings return0 without register accesses.
Each read/modify/write remains a separate volatile transaction.

Stock level entry package0xf514/runtime0x10205f88,44-byte envelope. It masks
port to five bits, reads0xa0001004 and clears the selected bit for zero level
or sets it for any nonzero level, then writes and returns0.

Native macOS compilation produces direction96bytes and level36bytes;
both fit their original addresses. Candidate hashes are recorded in
 gx8002-gpio-output-candidate.json. Qualification is pending: compare ordered
MMIO across all pins, wraparound port values, valid and invalid enum bit
patterns, register patterns and preserved ABI. Source is not registered.

Decoded qualification completed:8,040 stock/source comparisons pass across
pins0..63 plus signed/unsigned boundary bit patterns, six enum encodings,
five distinct register patterns and two ABI seeds. The independent expected
trace preserves each read/write and field mask; target interpreters reject
unknown instructions, out-of-scope MMIO and callee-saved register corruption.
Six tests pass for output ordering, invalid-direction no-op, nonzero-level
semantics, wrapped pins, corrupted pin mask and damaged ABI. The report is
saved; these two functions remain unregistered while GPIOISR integration runs.

Integration complete:613 tests pass and full macOS apple-clang package build
and verify-artifacts succeed. Codec SHA
7f70713935390fd79df945f1e00388015f617cd8516e6873d23ce9676504d092;
package SHA2b831d15dc3bb0c60082bc456728a331881d9cf04df20d977b6d3f8baf5e8713.
These functions supply132 C bytes and12 unreachable padding bytes. The
firmware remains a hybrid, without hardware qualification.
