# Battery five-sample filter C frame extraction

This historical bridge-based implementation is superseded by the [direct C root](battery-filter-root-c-review.md). The current unit removes the bridge and separate body, preserving the native provider depth and scratch-memory trace.


The filter at stock address `0x91184` now uses an explicit native frame
bridge and a C body in `native_battery_filter.c`. REA and raw instructions
confirm that the native 48-byte push supplies the temporary word and sample
array in its first sixteen bytes. The new 16-byte bridge preserves that span
and its epilogue; the current C body is 196 bytes. Stock is 182 bytes.
This does not establish byte identity.

The temporary word at entry SP-48 begins with incoming R0. Only its low half
is cleared; the upper half remains in use. Three following words are zeroed
in native order to initialize six sample halfwords. The C body opens the
current device, requests five samples into the native temporary address,
reads each low halfword, stores it into the array and clears only that low
half before delaying. The runtime byte selects `osDelay(2)` or the busy delay
on every iteration. All provider statuses are ignored. The device handle
is reloaded for each request and close.

After close, the array is read again to find its two smallest values. The
captured sum subtracts those values with unsigned wraparound, divides by
three and narrows to sixteen bits. Multiplication by 292 and 2989 wraps at
32 bits before division by `0x79d38` and final sixteen-bit narrowing. The
C implementation retains this arithmetic, including overflow and duplicate
minima. Volatile halfword views preserve callback changes to retained data.

The ignored `build/goal-r1-battery-filter/verify.py` probe passes 1,292
stock-versus-C scenarios against an independent stepwise memory and arithmetic
oracle. Coverage includes all five-read success/write masks, partial and
non-writing sample responses, constant and duplicate samples, arithmetic
boundaries, changing device handles, both delay paths, full-width ignored
statuses and changes through retained scratch pointers. Checks include exact
scratch initialization and access widths/order, callback arguments, final
scratch bytes, returned result, callee-saved registers, SP, interrupt masks
and callback alignment.

All 562 R1 units compile without failures or duplicate strong symbols; the
other 561 source units and manifest are unchanged. Imports remain 227
application and 34 bootloader. Exact source, manifest, native, REA and probe
bindings are in [the machine-readable review](battery-c-filter-review.json).

Open/read/close and delay boundaries are modeled; the registry, ADC and
scheduler providers do not execute in this probe. The C body adds private
callback stack depth. The runtime context remains an unresolved dependency.
Physical voltage accuracy, timing, complete fault-state equivalence, final
linking, provider qualification and byte identity remain unproven. No G2
gates or source-plan selections change.
