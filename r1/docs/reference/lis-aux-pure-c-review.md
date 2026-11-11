# C LIS interrupt routing and tap policies

`r1/src/application/runtime/native_lis_aux.c` replaces three private-frame bridges with ordinary C: interrupt-route setter `0x756da`, tap disable `0x751b8` and tap enable `0x75290`. The route worker is consolidated into its canonical entry. The shared LIS context declaration now uses its actual 16-byte prefix owner. Motion-table auxiliary slots and declarations consistently return a 32-bit completion word with no arguments; table layout and targets remain unchanged.

Route setup retains reads of registers `0x24`/`0x3f`, field computation and writes to `0x23`/`0x3f`, with the same early error returns. Tap policies retain their complete register order, routing-bit changes, modes/rates, live logging gates and completion value one. They still continue after helper errors. Locals start at zero when providers write nothing; this replaces caller scratch history with a deliberate C fallback.

REA bytes match the official artifact. The full fixture passes **136,808 stock/C comparisons** across route bytes, all register-24 values, register-63 values, both tap graphs, logging modes, errors at transfer positions and live context changes. Actual C field, register and read/write helpers execute. Tests compare transport calls/statuses, every register-bank byte, return words, explicit route output and context. Caller stack, callee-saved integer/FP registers, SP, interrupt masks and route guards remain intact while modeled callbacks overwrite caller-saved registers.

Another **108 C-only unwritten-read cases** compare initialized fallbacks with a zero-byte-delivery oracle across caller seeds and transfer errors. They do not claim equivalence to arbitrary old stack data. Five compiled defects are rejected using a reduced matrix: wrong route register, ignored read errors, wrong disable mask, wrong tap mode and wrong route fallback.

The shared context is placed at a controlled fixture address. An initial linker-placement mistake in the fixture was corrected before the full passing run; final image placement is not proved. Bus callbacks model byte delivery, including filled buffers carrying error status, and logging remains modeled. Provider overruns, private-frame aliases, incidental R2/R3/APSR, faults/concurrency, physical routing/tap behavior and final linking/startup remain unverified.

The open-toolchain report `build/sources-goal-r1-lis-aux-reviewed-c/report.json` compiles all **855 units** and completes both relocatable compositions. All **844 other nongenerated objects**, including motion selection and its tables, remain unchanged. The normal auxiliary object equals the executed probe object; log sections remain identical. Imports remain **61 application / 22 bootloader**. R1 manifest validation passes, and manifest/source-plan selections remain unchanged.

A source audit now finds no inline assembly or naked functions in all seven `native_lis*.c` runtime units. Architecture-specific delay/driver code elsewhere and full firmware completeness remain separate. Byte identity is not claimed.

[Machine receipt](lis-aux-pure-c-review.json) binds sources, REA and ignored probe evidence under `build/goal-r1-lis-aux-pure-c/`.
