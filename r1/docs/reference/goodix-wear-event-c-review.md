# R1 Goodix wear-event policy in C

`r1/src/application/goodix/native_wear_event.c` now replaces the vendor demo wear hook in the existing generated `gh_demo_hook_r1.c`; its header supplies the generated unit's declaration. Stock `0x2eb84` uses stream callback slot 3 and different event routes; the old template called the unresolved `gh3x2x_wear_evt_notify`. The pinned upstream file remains unchanged.

Wear-off takes priority when both event bits are set. Living-object wear-off calls slot 3 with zero and returns; ordinary wear-off calls slot 3 with zero and sends multi-sensor event 2. Living-object wear-on calls slot 3 with one and stops sampling with mask `0x200`; ordinary wear-on sends event 1 without the slot callback. The callback pointer is read after logging. Logging preserves repeated short-circuit mode reads, exact ring/SDK strings with CRLF bytes, and the native descriptors.

The policy and calls are C. At the original checkpoint, two empty extended-assembly register constraints retained the recorded 16-byte save frame across log providers. The first unconstrained C probe used eight bytes and was rejected. Tail callbacks and tail stop/event providers run after the caller frame is restored; ordinary callbacks run at caller SP minus 16. Active callee-saved values are excluded from this bounded contract. Callee-saved restoration and interrupt masks are checked.

## Subsequent pure C frame closure, 2026-11-11

The wear hook now uses ordinary C variables and no register-bound assembly.
It lives in its own C unit with Clang's `-fno-omit-frame-pointer` flag. The
compiled entry saves four registers, preserving the 16-byte provider frame;
the original default-flag C candidate saved only two. Applying the flag to
the full generated hook unit changed 16 other function bodies, so that probe
was not integrated. With the isolated unit, all other generated hook function
bytes match the preceding normal object. The isolated wear object SHA-256 is
`bc08b526d6e15811b8a77b5a0f5ae1a91321bfdcda89e6ac3c3a6283bf8786ab`.
The current object passes all 3,840 paired policy cases and 768 paired cases
executing the actual wear-cache callback, including callback replacement,
full 240-byte cache state, provider SP, returned SP, callee-saved registers
and interrupt masks. Results are under ignored
`build/goal-r1-goodix-wear-hook/pure-c-isolated-results.json` and
`pure-c-isolated-integrated-results.json`. The full 1,045-unit R1 build and strict
application/bootloader links pass at
`build/sources-r1-wear-isolated-c-20261111/report.json`,
`build/r1-link-wear-isolated-c-20261111/report.json` and
`build/r1-boot-link-wear-isolated-c-20261111/report.json`. The application uses
693,768 of 696,320 flash bytes, leaving 2,552. Provider implementations,
device execution, and active register residue remain separate checks.

Verification:

- Clang and GCC9 each pass 3,840 paired stock/C cases covering event priority, extra bits, live mode sequences, optional callbacks, callback replacement/removal during logs, exact messages and provider arguments/SP.
- Each compiler also passes 768 paired cases executing the actual native and C wear-cache callbacks and comparing the full seeded 240-byte cache. Logging, stop-sampling and multi-sensor providers remain modeled; callback mutation is covered by the separate unit fixture.
- Wrong callback slot, stop mask and log-mode bit variants are rejected. The first eight-byte-frame candidate also fails the fixture.
- All 576 R1 units compile and both relocatable compositions succeed without failures or duplicate strong symbols. Application imports fall from 167 to 166; bootloader imports remain 34. All 575 other objects and the other 16 hook functions are unchanged. `make sources-check` and `git diff --check` pass.

REA/Ghidra confirms the entry assembly and reports a grouped tail-target body and terminal-flow limitation. Raw instruction execution supplies the bounded comparison. The historical 444-byte inventory envelope is retained; it is not the contiguous entry code span `0x2eb84..0x2ec91` and supplies no new inventory or pseudocode coverage.

Four Clang and four GCC9 qualification candidates compile, selecting no regions. The candidate stays outside the exact source plan. The canonical hybrid remains equal to locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: 3,945 source-built bytes, 642,215 fallback bytes and 248 resource bytes. Full source-only linking, physical hardware operation and source completeness remain unproven. No G2 gate advanced.

[Machine-readable evidence](goodix-wear-event-c-review.json) records REA provenance, source/dependency hashes, normal builds, compiler fixtures, rejected variants, audits and qualification. Probes remain under ignored `build/goal-r1-goodix-wear-hook/`.
