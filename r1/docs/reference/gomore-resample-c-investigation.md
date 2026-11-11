# GoMore resampling C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-resample-c-review.md) records promotion into the normal source build.

Stock ACC `0x60990` and PPG `0x60a14` were checked against REA bytes and
forced-Thumb disassembly of the locked application. The experimental C candidates
remain under `build/goal-r1-gomore-resample-c/`; neither is in the source manifest.
The [receipt](gomore-resample-c-investigation.json) binds the current artifacts.

ACC clears three 100-byte destinations with a fresh descriptor read before each
call, clears the descriptor flag, then invokes three kernels for nonzero count.
Kernel arguments load the destination before the source, preserving alias order.
Zero count publishes flag one and status 32. Kernel returns are ignored.

PPG clears 100 bytes of private scratch and the live output, clears its flag,
and returns status 64 with flag one for zero count or zero channels. Otherwise
it converts channels as signed, computes its reciprocal, invokes at most one
kernel, accumulates 25 samples, and scales 25 samples. Negative channel words
skip the kernel loop but still scale. The output pointer is reloaded per sample.
Both roots log the final status.

Initial Clang output delayed reciprocal computation until after the PPG kernel.
A native/C trace with channels 255 detected the missing inexact FPSCR flag at
kernel entry. A volatile reciprocal temporary forces earlier computation in C.
Expanded two-NaN tests exposed operand commutation by both Clang and GCC:
with two quiet NaNs, stock preserves the output operand payload, while the first
C prototype preserved the sample operand payload. A non-inlined C addition helper
compiled with strict GCC floating-point flags emits the stock operand order.
The helper has no inline assembly and introduces no persistent state.

The current GCC prototype passes **1,072 native/C cases**, including **60 fault
pairs**, 224 mixed FP patterns and 128 pairwise FP operand combinations. The
matrix includes four rounding modes, flush-to-zero and default-NaN settings.
Preserved integer and high FP registers are checked on completed calls.
Thirty cases additionally have independent expectations for status, kernel
counts/arguments and PPG finite output. Nine compiled defective controls are
rejected (addition order, statuses, contexts, flags, scaling, dispatch and log
severity). Removing volatile alone survived under this GCC profile; it is not
counted as a rejected control. Compilation failures also do not count.

An explicit 112-byte C frame plus 32 saved register bytes now puts PPG scratch at
entry SP minus 140, matching stock. The replay compares numeric scratch pointers
without normalization. The two tail words reserve stock frame space; no extra
output or persistent RAM is introduced. ACC still saves 24 bytes versus stock's
32, so provider entry SP equality is not claimed. Lower clear/kernel/logger calls
remain modeled, and actual host integration is a separate pending check.

Before promotion, expand fault/provider mutation coverage and replay through the
actual host caller. Physical alignment behavior, device execution and byte
identity remain unproven. No firmware source, source manifest or canonical source
selection changed in this investigation. The normal source build remains at
679 units. Experiments and their scripts remain under the ignored build directory;
the receipt records exact hashes for this checkpoint.
