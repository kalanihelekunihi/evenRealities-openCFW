# Independent review 5065/001

**PASS_SCOPED**; `accepted` remains false.

Fresh isolated replay passed all 150 cases across ten helper entry points, five initial block words, and three arguments. The masks and offset were independently confirmed from the pinned literal words. The full 16-byte block window and R0/R4/SP/PC assertions match.

The cases use stable modeled memory and do not validate condition flags, volatile mutation, aliases, or hardware effects.

Candidate receipt SHA-256: `1b4de69a991b4ef48563a067c59aec876bb65a5632724b673b9a03879956bca6`.
