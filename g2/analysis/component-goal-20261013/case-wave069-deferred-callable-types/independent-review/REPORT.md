# Independent review: wave 069 deferred callable types

## Verdict

The wave 069 edits fix the two confirmed callback-call type mismatches and align the low consumer's scheduler-state declaration with its actual provider. The edits preserve the 16-byte packet and native argument order. I independently validated the source/object inventory, production ELF identity, actual declarations, and reran the type and two native/source graph checks in a disposable `/tmp` copy. No new defect was found within this bounded callback/consumer scope.

## Source changes checked

`source-changes.json` lists exactly two firmware source files. The high consumer now calls through `void (*)(void *, uint32_t)` and converts the first payload word with `(void *)(uintptr_t)message[2]` at `application_boot_timer_expired_candidate.c:23`. The low consumer does the same with `m.arg1` at `deferred_consumer_offline/consumer.c:20`. These agree with the actual clear and set callback prototypes/bodies at `source_candidate_20261010/event_clear_callback.c:3-8` and `startup_candidate_20261011/event_set_callback_candidate.c:7-12`. The pointer word remains first (R0) and the bit mask second (R1), matching the native B0FC `BLX R2` evidence recorded in my wave 068 review.

The low consumer also now declares `case_scheduler_state` as returning `uint32_t` at `consumer.c:4`, matching its provider definition at `source_candidate_20261010/scheduler_state.c:4`. The return is ignored in the consumer, but matching the declared C function type remains required. The remaining `case_enter_critical`, `case_exit_critical`, `case_yield_request`, and `case_remove_waiter` declarations match their actual provider signatures on inspection.

The packet definition remains `struct { int32_t command; uint32_t callback, arg1, arg2; }` with `_Static_assert(sizeof(...) == 16)`. The producer still initializes `{-2, callback, arg1, arg2}`. Both high and low graph checkers assert this exact serialized tuple per execution before normalizing only callback address differences for cross-image comparison; no payload slot or argument ordering was changed.

## Independent reproduction

I copied the wave 069 scripts, frozen `before/` copies, source inventory, ELF, and receipt into `/tmp/case-wave069-independent.YghzBa`; read-only source/blob inputs remained pinned to the workspace. All generated fixture and result files were written in the temporary copy.

- `verify_types.py`: `PASS_DEFERRED_CONSUMER_C_TYPE_CONTRACTS`; both saved originals are negative controls; four compile-time type/word-width assertions pass.
- `verify_deferred_high.py`: `PASS_STOCK_DEFERRED_EVENT_CALLBACK_CONSUMER_GRAPH 108`; actual native and source scheduler/queue/consumer/clear-or-set callback/provider bodies run without stubs or cuts.
- `verify_deferred_low.py`: `PASS_REAL_NEGATIVE_ONLY_DEFERRED_CONSUMER_GRAPH 108`; the forced low consumer is linked from the real source objects and compared against the native B0FC path, with no provider stubs or callback-entry cut.
- Each generated type, high-graph, and low-graph JSON result matched the producer's corresponding result exactly.

I separately recomputed all pinned hashes: 401/401 source inputs match `input-manifest.json`, and 401/401 object inputs match the final receipt. The receipt ELF hash matches the file. Wave 069's production `case.elf` is byte-identical to wave 065's production ELF, both SHA-256 `51e51425823ff690c5707bd881d7a67047ec51c079473a443a1741b496f342ac` (121,152 bytes). This confirms the signature repairs did not change production machine bytes; the changes correct the source-level callable contract.

## Remaining limits

This review covers the known queued clear/set callback targets, these two consumer call sites, and the low consumer provider declaration. It does not establish types or lifetimes for arbitrary external callback writers, prove queue object lifetime, exercise waiting event tasks or scheduler races, or close physical IRQ/reentrancy behavior. The 108-case emulator graph checks are bounded software evidence, not physical hardware acceptance.
