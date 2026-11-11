# FreeRTOS unordered event wait in C

`vTaskPlaceOnUnorderedEventList` now uses the pinned FreeRTOS kernel body in the existing `rtos/task-wait/task-wait.c` owner. It marks the event value with the reserved high bit, inserts at the event-list cursor, and shares the existing delayed-list helper. No new manifest unit or duplicate helper is introduced. The caller must have suspended the scheduler.

The normal build report is `build/sources-goal-r1-rtos-unordered-wait-c/report.json`. All 729 R1 units compile and both payloads compose with zero failures or duplicate strong symbols. The event-group import resolves, reducing application imports from 168 to 167; bootloader imports remain 34. This is relocatable composition, not a complete firmware link.

ARM emulation executes the compiled API and actual pinned C list routines without executable bindings. All 7,200 cases pass, including 4,608 current delayed-list cases, 1,152 overflow-list cases and 1,440 indefinite suspended-list cases. Checks cover the event cursor and reserved bit, ready-list removal, sorted wake insertion, tick wrap, next-unblock updates, preserved task ownership, scheduler/tick state, interrupt masks, stack and callee-saved registers. Data symbols use isolated harness coordinates. Invalid pointers and an unsuspended scheduler are outside the tested preconditions.

Four compiled defects are rejected by runtime assertions: omitting the reserved bit, sorting the event list, disabling indefinite suspension, and shifting the wake time. The original source prefix, all pre-existing instruction sections and their named relocations are unchanged; the other 728 object hashes are unchanged. `make sources-check` passes for both devices.

The machine-readable [review receipt](rtos-unordered-wait-c-review.json) records upstream provenance, build hashes, the test digest and defect diagnostics. Probe sources and subset ELF are under ignored `build/goal-r1-rtos-unordered-wait-c/`. These checks establish pinned C semantics against the existing native layout contracts; they do not claim stock byte identity, complete scheduler/event-group execution, physical hardware timing, or a complete firmware image.
