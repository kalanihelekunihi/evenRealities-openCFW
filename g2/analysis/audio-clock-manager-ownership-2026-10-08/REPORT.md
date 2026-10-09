# XTAL user ownership and release

Six complete native offline functions pass **514 original-instruction comparisons** on exact ELF `7875dedc218c22c9a83f92838fc37967c26d22c070d8e9891a42007025342c78`. **24 additional original-only sequences** validate request/repeat/release ownership, including invalid-drive paths, with real stock clock manager/oscillator/delay execution. [Source](../../components/audio/clock_manager_ownership_offline/ownership.c), [interfaces](../../components/audio/clock_manager_ownership_offline/ownership.h), [pseudocode](pseudocode.md), [exact build](exact-build-validation.json), [body/data provenance](function-bindings.json).

## Recovered ownership

The clock manager stores seven rows of two32-bit user words at0x20073324. XTAL is clock2. CLKOUT_XTAL user52 is bit20 of0x20073338. Requests are idempotent bits, not counters. Set validates byte-narrowed clock<7 and user<57; query/count helpers omit validation. No lock is embedded in bitmap helpers; callers supply critical sections.

Oscillator action5 acquires user52 before drive validation. In constructed original-instruction sequences, drives1/2/8 return6 but leave bit20 set and crystal control enabled. A repeat returns6 again without an additional reference. Action6 removes that bit; with no other user it executes oscillator disable, clears stabilization and pointer; with user0 still present it leaves XTAL enabled. These are proven offline paths, not an observed hardware incident or a patch recommendation.

Repeated XTAL requests also publish a stack-local counter pointer even when stabilization is already false. The wait helper skips cleanup when that flag is false. Consequently the inactive pointer can remain after request returns; last-user release clears it, another-user release leaves it. Shown consumers dereference only while the flag is true. No active dangling-pointer hazard or concurrent race is established without real caller/IRQ ordering.

## Readiness and retained state

XTAL status0x480C56 reads controller bit8 first (external mode2), then bit0 (crystal mode1), otherwise off0; it does not measure crystal readiness. Request waits up to150 iterations of actual delay API(10), can exit on cleared flag, and returns success even when the counter reaches zero. Pinned source names microsecond units; physical elapsed time is unverified. The wait clears stabilization after software waiting, not a hardware-ready poll.

All24 lifetime fixtures preserve retained0x40008858 as0x5AF00000 while user bits change. This illustrates separate state domains: the manager user bitmap is distinct from retained request flags and six-byte request cache reconstructed previously. It is not a complete audit of all retained writes or indirect calls.

## Boundaries and next source leads

The native release still invokes actual original oscillator; request/wait remain source-guided pseudocode and original-code dependencies. Queries intentionally preserve missing stock bounds checks; do not expose them to arbitrary app inputs. Synthetic board24MHz/mode0, user tables and MMIO do not prove physical crystal behavior. Authentication binds to main raw SHA19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701.

Remaining available leads are native XTAL request/wait closure, manager board-info initialization0x4C38A0, and other HFRC/SYSPLL user branches. No source-exhaustion claim is made. Actual scheduling/IRQ traces are needed for concurrency conclusions. Prior seals,110 inputs,four checkpoints are preserved. Concurrent additive staging changed the index during this batch; it was inspected read-only and left intact. No staging/undo, commits/device writes/production changes were performed by this agent.
