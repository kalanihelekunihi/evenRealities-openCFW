# Goodix profile switch reconstructed in C

`r1_goodix_switch_profile` implements stock `0x50904` in the existing C
Goodix policy unit. REA confirms the routine first raises reset, prepares
transport, opens the bus, calls CMSIS `osDelay(100)`, switches configuration
zero, stops sampling mask `0x42`, then calls `osDelay(10)`. These are RTOS tick
delays, not Nordic busy delays. Return statuses do not short-circuit the sequence.

Only after setup does the selector matter. Selector zero tail-calls sampling
mask two; selector one tail-calls mask `0x40`; other full-width selector words
return after setup without a sampling call. The C body uses a required tail
call for the two valid selectors, restoring the original stack and return
address before entering the sampling boundary.

The execution probe passes 192 paired stock/C cases (384 executions), covering
zero/one and six unsupported selectors, varied callback result words and
interrupt masks. It compares exact external-call sequence/arguments and checks
original SP/LR at sampling entry, preserved registers, stack and masks. All
2,080 acquire and 2,080 release regression cases pass against the current object.
A deliberate early selector rejection fails at selector two: stock performs
seven setup calls while the variant makes none.

The normal report `build/sources-goal-r1-goodix-profile/report.json` compiles
all 569 R1 units without failures or duplicate strong symbols. Imports remain
197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-c-profile-review.json) binds REA, source, execution
probes, negative control and normal build by hash.

Both C and stock instruction bodies are 62 bytes; equal size does not prove
byte identity. No source-plan qualification was performed. The canonical source
plan and G2 gates are unchanged. Hardware, SDK and RTOS calls are modeled;
private frames/caller-clobbered registers/flags, actual scheduling and hardware
timing, physical power/bus/sampling behavior and complete source-only byte
identity remain unverified.
