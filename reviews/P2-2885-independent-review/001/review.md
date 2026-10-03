# Independent review 2885

Status: **PASS_SCOPED** (`accepted: false`).

Inventory, bootloader source, and decoded ITCM hashes match the candidate receipt. The candidate artifact hashes verify, and its isolated replay passed all 12 fixtures.

I checked the index-29 path against the original instructions. It calls the pre-wrapper, then the index-below-30 helper with `(3, 1, stackmask)`, performs one PRIMASK-protected read/modify/write of `0x40021004` with mask `0x08000000`, calls the post-wrapper, and polls `0x40021008` for equality using the same group mask. The poll routine receives budget 5 and its fifth stack argument is mode 1. It returns timeout 4 after six failed reads and five unit delays; on success, the index-29 path performs the original delay of 100 before the final status test. The fixture's final status is stable, so success returns 0. Control-write values, callback-wrapper order, read/delay counts, return state, high registers, SP, and PRIMASK match the replay assertions.

The callback targets are null and the status-register readiness is modeled. The final-read mutation path, nonnull callback behavior, other indices, and physical hardware effects remain unverified. No canonical admission is claimed.
