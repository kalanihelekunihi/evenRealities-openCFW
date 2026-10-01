# Independent review 1985

**Result:** PASS_SCOPED.

- All listed artifact hashes and the immutable touch.flash.bin source hash match the receipt.
- An isolated replay regenerated the candidate evidence exactly; the inherited startup trace still reaches 0x3D50 under the documented fixture.
- The original 3A80 both-flags path, 3A38/3568 storage write path, 404C reset, 3EE8 default halfword handling and 3EE0 stubs execute without helper interception in this composition. Recorded logs, cleared flags, PRIMASK 0 and SP 0x2000EFD8 agree with event.json.

**Limits:** The clock read hook, flash/status MMIO, and interrupt-context delivery are modeled. This composition does not establish physical timing, storage effects, hardware interrupt delivery, or complete startup behavior. No canonical admission is made.
