# RTC tick frame implemented in C

`r1_native_rtc_tick` in `r1/src/application/board/native_rtc_lifecycle.c` now uses a C tail wrapper and C worker instead of its 14-byte handwritten assembly bridge. The epoch-initialization and open bridges remain unchanged. No opcode array, executable blob or additional state is introduced.

The worker owns 56 local bytes below an eight-byte compiler save area. Its first 48 bytes occupy the stock calendar scratch address, caller SP minus 64. Calendar conversion is explicitly out of line: otherwise Clang scalarizes the calendar into a smaller temporary and loses that boundary. The public C wrapper compiles to a four-byte tail branch; the worker is 88 bytes under the normal profile. Its raw R0 result is checked in the recorded binaries, without treating a void C callback as a portable return-value contract.

The native sequence remains explicit: read divider; capture/increment/store epoch; load signed offset; convert the retained epoch; test calendar minute/second; reload alarm callback; pass the low hour byte; reset divider after callback return. Source volatile views preserve the previously recovered ordering. The native loop exits after record zero.

Clang and GCC9 each pass 8,400 direct paired cases plus 720 cases using the actual native and C calendar converter. Checks cover exact 48-byte scratch contents/address, conversion and alarm calls at native SP minus 64, active R4–R11 at conversion entry, divider/epoch wrap and signed offsets, controlled epoch/offset mutation after the epoch store, alarm matching/null callback, raw R0, saved-register restoration and masks. Direct conversion and alarm providers remain modeled. Partial-write cases stress the recorded binaries; the real converter fills all fields consumed by the C policy.

The previous assembly-plus-C arrangement passes the scratch pointer down into another C frame, placing its providers below native SP; it is rejected by the strengthened depth checks. Removing the converter boundary is also rejected because it collapses scratch storage. The new C frame closes both counterexamples. Private eight bytes beyond the calendar prefix and the save-slot layout differ from native; active R5/R6 at alarm entry, full fault/concurrency equivalence and physical RTC delivery remain outside this proof.

All 576 R1 units compile and both relocatable compositions succeed without failures or duplicate strong symbols. Imports remain 164 application and 34 bootloader. All 575 other objects and seven other lifecycle function bodies/relocations are unchanged. `make sources-check` and `git diff --check` pass.

The raw GCC9 qualification profile fails on unused-parameter diagnostics in pinned Nordic SVC header definitions. A scoped qualification/test profile adds `-Wno-unused-parameter`; all four GCC9 candidates then compile, and its recorded Os object passes the fixtures above. Normal manifest flags are unchanged. Four Clang candidates compile as well. Neither compiler selects a region, so the exact source plan is unchanged.

REA reads the locked 108-byte entry envelope but reports the queried individual instructions as undecodable; that limitation is retained. Explicit Thumb disassembly and native execution establish the frame/order evidence. The envelope contains 102 instruction bytes, two padding bytes and a four-byte literal. It gives no new global inventory, pseudocode or freeze coverage.

The canonical hybrid remains equal to locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,961 source-built bytes, 642,199 fallback bytes and 248 resource bytes. This C tick candidate is not byte-qualified; full source-only firmware and hardware operation remain unproven. No G2 gate advances.

[Machine-readable evidence](rtc-tick-c-review.json) binds source/dependency hashes, compiler profiles, fixtures, rejected variants, audits, REA limits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-rtc-tick-c/`.
