# Independent review 2857 — profile field-apply leaf

**Result: PASS_SCOPED.** The source range, body hash, and packet artifacts verify. The isolated static replay passes with 24 instructions covering `0x42AB7C..0x42ABB2`. Decoding confirms the profile magic guard, ordered fields (target low 10, low 6, then bits 15–16), fresh profile-word-104 loads, and the stated exit register behavior.

I also ran original instructions for representative guard-match and guard-mismatch cases; their return/register and NZCV behavior agree with the pseudocode. This does not cover all values, concurrent changes, aliasing, caller ownership, or physical peripheral meaning. `accepted` remains false.
