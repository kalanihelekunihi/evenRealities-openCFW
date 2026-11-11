# YHM recovery-delay C increment experiment

The delay at `0x5c0fa..0x5c10d` is a timing primitive with four NOPs per loop and an unsigned bound of 209. Its production source is `r1/src/application/board/native_stacmd_delay.c`; the canonical source plan already admits its complete 20-byte body.

Moving only the increment from inline assembly to `++i` preserves the compiled body's length, NOPs, bound, branches and return. However, Clang emits `01 30` for the addition at body offset 10; locked stock uses `40 1c`. These are different Thumb encodings of addition by one. Functional similarity does not satisfy the repository's byte-identity target. All five official qualification profiles compile, and none selects this body. The production builder independently rejects the candidate with `selected source bytes changed: r1_stacmd_recovery_delay_native`.

The experiment was reverted exactly. The canonical source plan is unchanged. The restored production build is `build/hybrid-goal-r1-delay-retained/build-report.json`; its application is compared by SHA-256 with the locked artifact in the machine receipt. The temporary normal build `build/sources-goal-r1-delay-increment-c/report.json` describes the rejected experiment and must not be treated as the current source validation baseline. The current normal baseline remains the flash-write-frame report.

This result supports retaining the timing assembly under the tested profiles. It does not prove that every possible C formulation or compiler is unsuitable, and it does not measure physical hardware timing. The next assembly-removal work should prioritize control/data policy rather than replacing this already-qualified primitive with equivalent code.

Probe sources and qualification output remain under ignored `build/goal-r1-delay-increment-c/`. Durable input/output hashes: [stacmd-delay-c-increment-review.json](stacmd-delay-c-increment-review.json).
