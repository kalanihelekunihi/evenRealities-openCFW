# Independent review: wave 065 callback call types

## Conclusion

The two callable-type corrections from wave 063 are present in the three declared source files and resolve those mismatches within the reviewed source paths. The change preserves callback arguments, the high cancellation target's `uint32_t` return type, and the generic void-returning RxISR call path. I independently reran the supported type and native/source DMA checks in a disposable `/tmp` copy; both passed. This is an available-evidence/source review, not physical acceptance.

## Source changes and call contracts

- `g2/components/case/source_candidate_20261010/dma_abort_provider.c:53-54` now loads/calls the DMA `+0x38` callback as `void (*)(uint8_t *)`. The current producer at `g2/components/case/source_candidate_20261010/uart_irq_continuations.c:30` stores `case_uart_dma_abort_callback`, whose definition at line 15 takes `uint8_t *`; the direct fallback at line 32 already uses that type. The loaded-call argument is still `dma`.
- `g2/components/case/startup_candidate_20261011/application_boot_sensor_irq_restart_candidate.c:9,42` now uses a cancellation-specific helper with type `uint32_t (*)(uint32_t)` for `p+56`.
- `g2/components/case/startup_candidate_20261011/application_boot_sensor_irq_5f50_candidate.c:22-24,55-56` adds the same cancellation-only typed call for the fallback path. It leaves the existing `void(uint32_t)` `invoke` helper in place for other callback slots such as descriptor `+116`. Both cancellation call sites explicitly discard the target result, matching the surrounding native callers, while leaving `case_boot_sensor_cancel_callback`'s `uint32_t(uint32_t)` definition and R0 behavior intact.

The source changes exactly match `source-changes.json`: all three saved-original hashes and all three current hashes match their declared pins. The saved originals show the mismatching call types. The 401-entry input manifest has zero source-hash mismatches; the build receipt has 401 objects and zero object-hash mismatches. The production ELF is 121,152 bytes, SHA-256 `51e51425823ff690c5707bd881d7a67047ec51c079473a443a1741b496f342ac`, matching the receipt. The locked native firmware payload remains SHA-256 `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.

## Independent checks

I copied the three current and three saved-original source units, checker inputs, locked native image, and pinned production ELF to `/tmp/case-wave065-independent.XEqJMI`; I did not let the checkers write into the producer's sealed wave directory.

- `/tmp/iar-c-runtime-venv/bin/python <temp>/g2/analysis/component-goal-20261013/case-wave065-dma-cancel-call-types/verify_types.py` passed as `PASS_ACTUAL_SOURCE_AST_CALLBACK_TYPES_AND_3_ORIGINAL_NEGATIVE_CONTROLS`. The AST assertions observed the corrected DMA and both cancellation call types; they also observed the retained void RxISR call type. Four compiler `_Static_assert` controls passed, including assertions that the saved-original DMA parameter and cancellation return types are incompatible with their targets.
- `/tmp/iar-c-runtime-venv/bin/python <temp>/g2/analysis/component-goal-20261013/case-wave065-dma-cancel-call-types/verify_dma.py` passed as `PASS_160_REAL_DMA_CANCELLATION_PATH_PAIRS`. It executes locked native code and the real linked CASE source helpers/callback bodies on bounded RAM-backed inputs for low abort, high restart-ready, and high IRQ cancellation paths. The run produced a fixture ELF SHA-256 `08d1a35e309b44c71f84502bf5c997b147fe54e16f2d5fa30b19e771220ed9ad`, matching the producer fixture hash; its recorded production ELF hash also matches the pinned `51e514…342ac` ELF.
- Native branch control is rechecked: locked halfword `0xe00d` at `0x08006050` targets `0x0800606e`, skipping `0x0800606c (mov r0,r4)`. The high fallback therefore keeps p in R0; source continues to pass `rd(state)` (p). No argument substitution is warranted.

The emulator evidence uses synthetic ordinary RAM for peripheral/register fixtures and proves only these bounded instructions and source/native paths. It does not emulate physical peripheral timing, actual interrupt delivery/reentrancy, asynchronous callback lifetime, or hardware behavior. The fixture's object inputs are the pinned wave 065 build products; I independently verified their hashes but did not perform a second 401-unit production rebuild. No timer/router/memory/reset regressions beyond the focused type and DMA checks were rerun in this review. Nothing here constitutes global source completeness, firmware admission, or physical acceptance.
