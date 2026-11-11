# RTC epoch initialization implemented directly in C

`r1_native_rtc_epoch_initialize` in `r1/src/application/board/native_rtc_lifecycle.c` is now a direct C implementation. Its 18-byte handwritten frame bridge and the superseded private `rtc_epoch_body` are removed. No forwarding wrapper or additional implementation remains. The RTC open bridge is the only assembly block left in this module.

The C initializer retains stock's sequence: reject null block; read/store the UTC offset; load caller name before record name; compare; test opened; capture/store epoch; convert that captured epoch into calendar scratch; return zero. Mismatched/closed requests return 17 after the offset store; null block returns 4 without touching shared state.

The first 48 calendar bytes occupy caller SP minus 72, and both strcmp and conversion run at that same native depth. The recorded Clang build uses 56 local bytes and 16 saved bytes. GCC9 uses 48 local bytes, four alignment bytes and 20 saved bytes. Compiler-selected C padding expresses these tested layouts. The first GCC candidate used an 80-byte frame and was rejected. This is profile-bound geometry, not a portable C guarantee for arbitrary compiler options.

Clang and scoped GCC9 each pass 936 direct paired cases and 20 cases using the actual native and C calendar converter. They compare ordered shared/input loads and stores, name read order and controlled mutation, input/counter aliasing, statuses, the exact 48-byte scratch pointer/content, provider depth, counter/record state, saved-register restoration and masks. strcmp and direct conversion are modeled. The old assembly-plus-C extra provider frame, initial GCC 80-byte frame and a delayed offset-store variant are rejected.

Private frame/save-slot contents and active saved-register values during providers remain outside the comparison. Clang skips frame allocation on the null-block path while native still performs its private saves; stack-fault identity is therefore unproven. Neither physical RTC operation nor complete concurrency/fault equivalence is established.

All 576 R1 units compile and both relocatable compositions succeed without failures or duplicate strong symbols. Imports remain 164 application and 34 bootloader. All 575 unrelated objects and seven other lifecycle function bodies/relocations are unchanged, including the C tick path. `make sources-check` and `git diff --check` pass. The direct initializer is 68 bytes under the normal Clang profile.

Four Clang and four GCC9 qualification candidates compile and select no regions. GCC9 uses the same scoped `-Wno-unused-parameter` option for pinned Nordic SVC header definitions as the tick review; normal Clang manifest flags are unchanged. Other optimization variants are compilation/qualification probes, not claims of equivalent frame geometry.

REA reads the locked 108-byte entry span, independently checked against raw bytes and explicit Thumb disassembly. It contains 102 instruction bytes followed by two padding and four literal bytes. The historical 118-byte inventory envelope remains unchanged; it supplies no new global coverage or freeze credit.

The canonical hybrid still matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: 3,961 source-built bytes, 642,199 fallback bytes and 248 resource bytes. The C initializer is not byte-qualified, and full source-only firmware remains unfinished. No G2 gate advances.

[Machine-readable evidence](rtc-epoch-c-review.json) binds source/dependency hashes, compiler layouts, native/REA bytes, fixtures, rejected variants, audits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-rtc-epoch-c/`.
