# R1 packed sleep signaling comparison in C

`r1/src/application/runtime/native_gomore_consume.c` now implements the
stock signaling compare-with-zero and FPSCR read in C. The helper classifies
the float's raw bits, preserves existing FPSCR control/sticky fields, sets
the stock IOC and input-denormal bits, and writes the resulting flags with
Arm compiler builtins. A private noinline C multiply keeps the subsequent
half-gain calculation after the FPSCR update. At this review's checkpoint,
the raw stack-frame bridge remained assembly to preserve an incoming
uninitialized byte and a native provider-visible frame address. It was
subsequently replaced with the checked C frame in
[the consumer review](gomore-consume-c-review.md#subsequent-c-frame-closure-2026-11-11).

The ignored probe in `build/r1-consume-vcmpe-pure-c-20261110/` uses the same
manifest compiler profile as production. The first inline candidate failed
the paired replay because Clang scheduled the half-gain multiply before the
FPSCR write. A noinline compare candidate changed an early path's FP state.
The final candidate passed **1,537 paired stock/C packed-consumer cases**,
including provider mutations, quiet/signaling NaNs, subnormals, FZ/DN and
rounding modes. The test compares output and provider-call state, raw frame
padding, return, saved integer/high-FP registers, SP, interrupt masks and
FPSCR. The current production source is identical to the tested candidate;
the production and probe objects have identical allocated sections and
relocations. The lower providers remain modeled by this replay.

The R1-only source build still compiles **975/975 units**, with no failures or
duplicate strong symbols, and its strict bootloader link remains vector-valid.
The application still has **24 unresolved functions**. Full flash load now
overflows by **29,464 bytes**, 80 more than the preceding checkpoint. The
manifest source scan finds **147 `__asm__` occurrences in 38 C files**, one
fewer assembly site. Hardware execution, full source-only application linking,
and byte identity remain unverified.
