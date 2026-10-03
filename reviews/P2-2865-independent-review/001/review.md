# Independent review 2865

Status: **PASS_SCOPED** (`accepted: false`).

I verified the candidate receipt and its three listed artifact hashes. The pinned Apollo bootloader source is byte-identical to the inventory image (`f89a4c…67b5`); the claimed body `[0x42ABBC, 0x42AC4E)` hashes to `1f0bf…ca2d`. The candidate’s isolated replay passed all 48 fixtures.

The replay’s controlled provider behavior matches the stated boundary: gate rejection returns 7 without a provider call; provider failures at stages 1–3 return their injected status. The assertions cover ordered provider arguments/call counts, persistence of writes already made to the profile, absence of copying failed stage-2 stack data into the profile, and five words copied before a stage-3 failure. The checked return, stack pointer, preserved high registers, and PRIMASK agree with the pseudocode for these fixtures.

The provider at `0x421548` is controlled; no provider implementation or hardware behavior is established. This is bounded failure-path evidence, not a complete-success or startup/caller-ownership claim. No canonical admission is made.
