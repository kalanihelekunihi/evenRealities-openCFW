# R1 stock two-pass AES policy

This component converts the three R1-owned routines at `0x48B02` (162 bytes),
`0x891A4` (20 bytes), and `0x98E22` (22 bytes) to C. AES key expansion and block
decryption come directly from pinned tiny-AES-c, not a local substitute.
`r1/docs/correlation/TINY-AES-CORRELATION.md` records source lineage and provider
boundaries. The argument order and loops were checked against the tracked
pseudocode and complete disassembly, then against the authenticated application.

The first pass decrypts complete blocks in reverse order with the second key
half. Its chain starts at the first key half, then points to the next block of
original input. The second pass decrypts forward with the first key half,
starting its chain at the second key half and retaining each pre-decrypt
intermediate block for the next iteration. Stock copies the full input first
and transforms only complete blocks. Partial trailing bytes remain unchanged;
this differs from the historical clean-room adapter's validation policy.

Supported calls require nonnegative lengths, disjoint input/output/key/result
storage and valid extents. No new padding or argument rejection is introduced.
Negative transform lengths and invalid/overlapping pointers are not verified.
The XOR helper separately preserves signed-length and overlapping bytewise
behavior for the tested cases.

```
make -C r1 crypto-candidate
# Python environment with unicorn==2.1.4:
make -C r1 crypto-oracle PYTHON=/tmp/r1-source-venv/bin/python
```

The component has two compilation units and links without runtime libraries or
unresolved symbols. `pre-consolidation:r1/research/source-build/crypto/verification.json` records
116 transform comparisons and 28 XOR comparisons against original stock Thumb,
covering 103 payloads including all lengths 0...65, random keys/messages,
partial blocks and 4,096 bytes. Output-length words, output guards, original
inputs and keys were checked. Only component behavior for those inputs is
established; neither an application link nor all-input equivalence is proven.

REA and Ghidra-MCP separately examined the candidate ELF and its upstream AES
calls. Their dossiers are saved in the same directory. Both use Ghidra, so their
agreement is not independent semantic verification. The candidate orchestration
body is 242 bytes versus stock's 162: exact instruction matching and original
compiler/placement remain unresolved.
