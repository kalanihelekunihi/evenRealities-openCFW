# Independent review 2199

**Result:** PASS_SCOPED.

All source, body/pool and receipt-file hashes match. The code and literal extents are [0x6BD4, 0x6D6A) and [0x6D6C, 0x6D74), and the stored listing matches the Thumb/M-class decode.

An isolated replay regenerated all 144 fixtures exactly. Original 6BD4, 6140, 6AC0 and its jump table execute. Across guard/busy inputs, previous modes 0/2, and controlled 8FD0 results 0/2, the replay verifies outer/child call order, setup arguments, descriptor bits 0/7, propagation of mode-2 failure status 64, successful selected writes/configuration, fast reuse, and high-register/SP preservation.

For the observed transition, previous mode 0 requests mode 2 and reaches original 6078, 60EA, 6044 and 8FD0. A nonzero 8FD0 result returns 64 through both 6AC0 and 6BD4; zero follows the setup writes and then 664C. Previous-mode-2 fast reuse bypasses 6AC0. This matches the decoded branches and assertions.

**Limits:** 5C8E, 664C, 6078, 60EA, 6044 and 8FD0 remain controlled. Callback/mutation effects, child behavior, hardware behavior and physical MMIO are not established. This covers only the enumerated RAM-backed cases and makes no canonical-admission or whole-firmware-completeness claim.
