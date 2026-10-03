# Independent review 2291

**Result:** PASS_SCOPED.

Isolated replay regenerated all 2,592 fixtures. Source/body/literal and listed artifact hashes match. 6928/9178, 7288/A6C0 and 6980/5FA4/A6C0 execute original instructions without interception; only 6AC0 is controlled. Captured mode call arguments and R1 clobber, sequence scratch arguments, budget/poll arguments, parent-only writes, final output/status and R4-R11/SP assertions pass. With the chosen clock and config, budget is multiplier×5 or ×10 for mode2; multiplier zero yields poll return zero even with modeled ready status, hence parent status OR 4.

**Limits:** The candidate asserts parent-level writes while child MMIO writes execute but are not fully asserted in this composition. Only selected mode/status/field patterns are used; 6AC0 transition behavior and hardware status remain modeled. No canonical admission or physical claim.
