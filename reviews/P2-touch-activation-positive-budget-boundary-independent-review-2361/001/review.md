# Independent review 2361

**Result:** PASS_SCOPED.

Receipt e0e66d6d334b588a69d2da9bf8deed32969e286a0badc6225f123199aafb8bc3 pins source, body [0x4AF4,0x4BA0), literal pool [0x4BA0,0x4BAC), and artifacts; hashes match. Independent replay passes all 24 cases.

Both PC-relative loads resolve to 0x4BA4: at 0x4B56, aligned PC 0x4B58 + 0x4C; at 0x4B60, PC 0x4B64 + 0x40. The referenced word is 1000000 (0xF4240) in each case. Therefore the original 4AF4 uses 1,000,000 for both A6C0 and 5FA4 arguments; 0x4BA8 is not the scaler literal. This corrects the erroneous formula prose in 2356.

The original A6C0/5FA4 path computes positive budget 200,000 for the selected fixture. Against controlled readiness busy for budget-1, budget, and budget+1 reads, the actual poll sees 200,000 / 200,001 / 200,001 reads respectively; the first two retain the accumulated status, the last replaces it with 4. Full execution, compacted nonpoll call order, local writes, result and R4-R7/SP assertions pass.

**Limits:** Other children remain controlled; only arithmetic helpers are original. Readiness is modeled, not physical. Only the specified positive-budget boundary is covered; arbitrary clocks, overflow and aliasing remain unresolved. Private evidence only; accepted:false and no canonical admission.
