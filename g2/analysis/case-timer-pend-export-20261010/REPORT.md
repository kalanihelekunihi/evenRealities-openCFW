# CASE deferred timer command source export

The independently compared `case_pend_from_isr` producer is compiled into the CASE archive under the stock `xTimerPendFunctionCallFromISR` name. `timer_pend_export.c` applies a preprocessor rename before including the unchanged source file. Its SHA-256 `398063f649894ab704b78bd5285dc6635af077368f24aeeec9cbbba9aa856059` matches the prior validation receipt. Its ARM32 arguments remain callback, pointer, value, and yield pointer in R0–R3.

The earlier deferred-event study compared this producer with original `0x0800ce0c` in 272 original/source cases, including queue acceptance and rejection with original queue/copy peers. The current Clang `-Os` export now passes a fresh **272/272** original/source producer comparison using coherent queue fixtures and original mask peers; the verifier asserts that its object hash equals the object inside the current archive. `results.json` records source, compiler, command, and ELF hashes. `event_clear_isr.c` declares its four-word integer/pointer ABI consistently with the exported producer, and its 24 original/source child-call comparisons pass after that change.

This bounded export is **COMPLETE** as source composition. The CASE archive has 23 objects, 43 provided globals, and 12 unresolved names after the typed event-set adapter. The timer daemon's execution, referenced event lifetime, and full image remain unproven.

`arm-none-eabi-ld -r --whole-archive` over all 23 archive members succeeds, ruling out duplicate strong definitions in this selection. The resulting relocatable object's `nm -u` lists the same 12 unresolved names; it is not a final image link.
