# Independent review 2903

**PASS_SCOPED**; `accepted` remains false.

Reviewed static candidate analysis/apollo-boot-trim-commit-map-2902/001. The source image SHA-256 matches inventory; body [42AE9C,42AEEC) matches its pinned digest, and candidate artifact hashes were checked. Isolated Capstone replay into a fresh directory passed and decoded 30 instructions across the exact 80-byte interval. The instruction sequence confirms an 8-byte R7/LR frame, calls 41B8EC then stores returned R0 in the saved-R7 slot, calls 42AE6C, reads flag byte 200271B2, and on nonzero flag checks state word 20000144 for 8 then freshly rereads it for 12 before conditionally setting bit3 and then bit6 at 4002037C. The flag is cleared on this nonzero path; zero flag branches around the state/register branch and clear store. Both paths call 41CCD6 and 42AE24 with R0=1, reload the saved interrupt mask, restore PRIMASK, and pop to R0/PC. Literal targets/values match the listing. This is a static map only: helper behavior is separately evidenced, but original dynamic composition is pending; no claim about physical hardware, concurrent state changes, full caller ownership, or canonical admission. accepted:false.

Candidate receipt SHA-256: `72e921110c0062636e0d2c26b963e1ad83a6f38c104d9f06e0e4377d7c6240d9`.
