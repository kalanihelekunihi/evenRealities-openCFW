# Independent review 2879

Status: **REVISE_PROSE** (`accepted: false`).

The source and ITCM hashes match inventory, the initializer body `[0x42AC54, 0x42ACA4)` matches its digest, and candidate artifact hashes verify. The isolated replay passed all 48 fixtures.

The replay runs the original initializer, output wrapper, dispatcher, operation, classifier, poll/delay, and ITCM delay loop. It controls the power helper and derivation helper, and manually installs the slot-4 pointer to operation `0x42A878`. The `-40.0f` input classifies as category 0, and the tested bound words and aliased return registers match the assertions. Gate, helper status, poll result, calls, delays, output words, high registers, SP, and PRIMASK are checked. The apply target is asserted not to run.

One rationale in the prose is too broad: when the controlled derive helper returns zero and writes zero derived words, those words match the initially zero stored values, so the apply call is skipped. When the derive helper returns 4, the original operation exits on that nonzero status before the comparison/apply decision. The prose should distinguish these paths instead of saying both skip apply because the values match. The provider/derive implementations and installed table path remain unproven; no hardware or canonical admission claim is made.
