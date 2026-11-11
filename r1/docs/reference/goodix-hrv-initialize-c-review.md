# R1 native HRV initialization in C

The [HRV frame-execution review](goodix-hrv-execute-c-review.md) now adds the C adapter and disabled report. The existing `r1_goodix_hrv_initialization_count` cell is the last-HR cache during execution; it remains the same owner initialized here. HRV calculation itself remains an explicit unfinished core.

The HRV constructor (`0x6db5c`) and full-width checked float-storage initializer (`0x56874`) now use C in `r1/src/application/goodix/native_hrv_initialize.c`. The [receipt](goodix-hrv-initialize-c-review.json) pins REA reads, sources, normal/tested objects, fixtures and results.

The constructor preserves native entry errors, the existing-owner guard and partial failure state. It shares the canonical owner already used by teardown, allocates a 308-byte context and preserves the exact finite rate groups and signed fallback. Buffer counts remain 32-bit. Supplied buffers are not cleared; failed storage allocation leaves its record untouched. No automatic cleanup or new state is added.

The constructor reloads the owner around allocator/helper calls, creates the 48/696-byte auxiliary structures and writes native metadata. Four signed integer thresholds convert to float32 and divide by 10,000, in field order `0xe8/0xec/0xf4/0xf0`. The compiled object contains four `VCVT.F32.S32` and four `VDIV.F32` instructions, without a reciprocal multiply or inline assembly.

All 1,273 comparisons pass. Every one of the 982 native instruction bytes executes. The corpus includes every rate from 0–1,100, signed and out-of-range rate words, all allocation guards, owner replacement at each allocator callback, full-width/wrapping storage counts and all four FPSCR rounding modes. Independent enumerated rate tables and exact-rational float32 rounding/status calculations supplement the stock/C comparison. Actual C storage and memory/string primitives execute; only malloc is modeled. Twenty-three compiled defects are rejected.

All 128 successful full HRV constructor/real-allocator/complete-teardown lifecycles call no modeled function ports. Raw complete heap bytes, owner state, saved registers, stack, masks and active floating-point state agree. Every allocation coalesces to the prior heap top and teardown clears the canonical HRV owner. These tests use the actual C allocator and existing C destructor without pointer normalization.

Modeled null malloc returns exercise guard branches and partial state, not physical exhaustion delivery. The public allocator's actual fatal-exhaustion path is nonreturning and separately reconstructed. Synthetic owner replacement tests establish reload ordering, not safe concurrent ownership transfer. Large wrapping capacities establish header arithmetic rather than physically valid buffers. Physical FPU delivery/cold activation, invalid pointers, concurrency, caller scratch and private frames remain unproven.

The 892-unit build passes without duplicate strong symbols. The tested object equals the normal object, 881 prior nongenerated source/object pairs are unchanged, and no writable state is added. The HRV constructor import is removed without new imports: application imports fall from 76 to 75; boot imports remain 22. Source-plan and cache layout are unchanged.

HRV calculation, remaining sensor engines, executor/inference implementation, final executable linking/startup and hardware boot remain open. This is an `ld -r` composition, not a bootable firmware image; byte identity is waived for this goal.
