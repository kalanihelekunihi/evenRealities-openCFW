# Native NADT reset and ADT shutdown in C

The [soft-ADT execution review](goodix-soft-adt-execute-c-review.md) adds the C sensor adapter and shared green/IR event reporters, reusing the existing selector, timeout counter and capacitor flag. Timeout advancement on core errors is preserved; the `goodix_nadt_calc` computation core remains unfinished.

The [NADT initializer review](goodix-nadt-initialize-c-review.md) adds the constructor/configuration tail and factors the reset fields into one shared C routine. Constructor/deinit and actual allocator lifecycles are rechecked against stock.

The [machine-readable receipt](goodix-native-nadt-reset-c-review.json) pins the exact stock REA bytes, source, normal build and executed fixtures. `native_nadt_reset.c` recovers the complete soft-ADT state/workspace reset and filter initializer. `native_adt_teardown.c` adds the basic and soft ADT shutdown callbacks. All are ordinary C and share the existing C byte-fill and allocator providers.

The reset clears five buffers, initializes a six-word filter descriptor and two histories, then resets selected state fields and workspace history words in stock order. Reserved bytes and the saved allocation pointer remain unchanged. It loads that allocation at the free call, releases it even when null, then writes status `0xbf` and returns zero. The typed canonical state/workspace totals 1,687 writable bytes; two coefficient arrays add 48 readonly bytes. Future initialization/calculation must share those owners.

The filter initializer stores pointer/count/scale words before clearing its histories. Clear length uses 32-bit wrapped `count*4+4`. Exact float bits are stored without arithmetic. Basic ADT clears byte2 then byte0, preserving byte1. Soft ADT clears its timeout after the parent returns for either status, then normalizes nonzero status to `-1`.

Verification passes 1,024 reset/soft-adapter, 4,368 filter, 1,536 basic ADT, 256 callback-mutation and 2,080 modeled-status comparisons. Every one of the 278 native entry instruction bytes executes across those fixtures. Another 784 comparisons execute the actual C fill and check byte writes. Another 256 execute the C initializer, malloc/free, filter/reset and public soft adapter with optional live guard allocations. All static state, workspace and heap writes match width/order/value. Source execution cannot enter stock code. Nineteen compiled defects are rejected.

Filter cases include overlapping history buffers, descriptor/history aliasing, four byte alignments, wrapped counts and signed-zero/NaN/infinity bits. Histories must be valid caller-owned buffers for the tested wrapped lengths; invalid null histories with positive lengths are outside the contract. Coefficient bytes are checked against stock, while the initializer admission does not establish the calculation algorithm.

The Cortex-M FP context is primed by an isolated fixture VMOV before configuring each call's FP registers/FPSCR. An initial diagnostic observed FPSCR reset on cold FP first use. This admission checks active FP context behavior and adds no FP setup instruction to firmware; cold activation and physical FP-context behavior remain unproven. Saved integer/FP registers, SP, masks, FPSCR, caller guards and preserved fields are checked. Caller scratch, APSR and private frames are excluded.

The fresh serial R1 build compiles 876 units (794 application,82 bootloader), with no duplicate strong symbols and unchanged 62/22 imports. Both tested objects equal the normal objects, and all 864 prior nongenerated objects remain identical. Two existing generated objects differ with build directory paths. The manifest adds two units; source plan and the existing cache linker layout remain unchanged.

The top-level shutdown controller, native initialization/calculation, physical sensors, concurrency, final executable linking/startup and boot remain open. Relocatable composition is not bootable firmware.
