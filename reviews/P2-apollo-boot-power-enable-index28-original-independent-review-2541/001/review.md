# Independent review 2541

**Result: PASS_SCOPED.**

The bound candidate is `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-enable-index28-original-2540/001`. Its receipt, pseudocode, replay and fixture hashes match, as do the locked inventory and both source images (flash image and decoded ITCM leaf). I replayed the script from an isolated copy; all 12 original-instruction cases pass.

The trace confirms the active index-28 path: pre-wrapper `41CD34`, `41CD1A(3,1,stackmask)`, one PRIMASK-protected OR-write of `0x04000000` to `0x40021004`, restore, then post-wrapper `41CD4A` before polling `0x40021008`. Poll arguments encode budget 5, mask/expected `0x04000000`, mode 1. Readiness on poll read 1 or 2 returns through the success final-read and yields 0 with the stable modeled status; never-ready performs six reads and five delay(1) calls, returns 4. The fixtures check callback-wrapper order, critical write, reads/delays, SP, high registers and PRIMASK restoration.

The final success read is stable by fixture construction, so the alternative final-read value is not covered. Callback table slots are null; nonnull callback behavior is covered separately, but this composition does not establish installation or physical readiness. This is one bounded entry path, not complete power-enable behavior or hardware validation. Private evidence only; accepted:false, no canonical admission.
