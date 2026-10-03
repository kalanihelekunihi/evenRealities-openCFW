# Independent review 2781

**Result: PASS_SCOPED.** The isolated replay passed all 16 original-handler fixtures with no function interception. Source, ITCM, body, and artifact hashes match. The six profile publication and control-field writes, original delay-5 call with 145 ITCM iterations, packed R0, preserved high registers, PRIMASK, and stack frame matched the assertions on the stated normal path.

- Wait/service and other indices are outside this fixture set.
- Emulated delay does not establish physical timing or peripheral behavior.
- Private evidence only; no canonical admission.
