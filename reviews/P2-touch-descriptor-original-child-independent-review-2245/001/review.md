# Independent review 2245

**Result:** PASS_SCOPED.

The source, constructor body `[0x5548,0x569E)`, literal `[0x56A0,0x56A4)`, and all candidate file hashes match the receipt. An isolated replay regenerated all 72 fixtures with original `0x5548`, `0x51BC`, and `0x5528` instructions and no function interception. It asserts the complete ordered destination-write ledger and 48-byte output, `0x51BC` map-entry/destination arguments, return status, and R4–R11/SP preservation.

The composition’s stated test setup is consistent with the replay: the field child sees zero configuration flags and zero pointed fields, adds its destination-word-12 update and the `0x00400000` prefix in word 16, and returns zero. The constructor then returns 1 for validity values other than 1, or writes word 20 and returns zero for validity 1. Parameter bytes 32 and 33 differ in the fixture inputs.

**Limits:** This composition exercises only the supplied kind/index/validity/flag/pattern combinations. Its zeroed child configuration does not exercise the field helper’s alternate configuration-prefix and secondary-field branches. Arbitrary field configurations, aliasing, physical behavior, and whole-firmware completeness are not established. No canonical admission is made.
