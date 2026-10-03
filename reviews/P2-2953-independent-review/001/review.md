# Independent review 2953/001

**PASS_SCOPED**; `accepted` remains false.

The candidate source/body pin matches the previously reviewed original decoder body. The 9,216 fixtures form the stated 6×3×4×4×2×4×2×2 product and execute original instructions without child interception. I independently checked replay output hashes and fixture count. The flag-byte values 0, 1, 128, and 129 distinguish bit 0 from bit 7: values with bit 0 set take the set path, including 129, while 128 follows the clear path. That agrees with zero-extended `LDRB`, `LSLS #31`, and `BPL`. Output writes/status and R1/R2/R4/R5/SP/PRIMASK/stop assertions pass.

This is bounded emulator evidence, not physical MMIO behavior, aliasing or volatile-change coverage, a complete flags/high-register contract, or global ownership.

Candidate receipt SHA-256: `82850d8a7189e6f47d7f9370f62c066f5531fef39c8be04c86b0820a46a2b332`.
