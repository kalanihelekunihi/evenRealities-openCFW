# Battery recovery C kernel and native frame

This historical bridge/kernel implementation is superseded by the [direct C recovery root](battery-recovery-root-c-review.md), which preserves the native provider frame and logging/saved-word overlap without executed inline assembly.


`board/native_battery_recovery.c` no longer captures incoming R2/R3 or restores
R1/R2/R3 with inline register moves inside compiler-managed C. Recovery logic
is a C kernel receiving the stock saved-word frame. A 14-byte entry bridge
saves R1-R9/LR and exposes saved R1/R2/R3 at entry SP minus 40/36/32. The C
kernel updates those words for log arguments, and the bridge restores them.
This is an ABI correction, not a claim that total assembly bytes decreased.

Fresh REA and raw instructions at `0x3db70` establish the frame and recovery
sequence. The 64-bit frequency-times-120 threshold, voltage comparisons,
percentage clamping, timestamp handling, state updates and logging branches
remain in C; no opcode array or firmware blob is introduced.

All 2,300 stock/C comparisons pass. Coverage includes timer wrap, zero/large
frequencies, elapsed-time boundaries, level/history/recovered states, voltage
thresholds, estimates, live log-mode sequences, timestamp values and a pointer
aliasing the native saved frame. Tests compare restored R1/R2/R3, provider
arguments/log contents and visible state, complete battery/runtime storage,
timestamp storage, R4-R11, SP, interrupt masks and callback alignment.

The ordinary old-source baseline agrees; it is not labeled a regression.
The controlled saved-frame alias case differs: stock and corrected C observe
the saved words as timestamp storage, while old C's private array is elsewhere
and reads unrelated stack bytes. Old R2/R3 become `0x5a5a5a5a` in that fixture;
stock returns the updated reference and captured timestamp word. This tests a
machine-boundary alias contract, not an observed physical charging failure.

Tick/frequency/curve/log providers are modeled. Provider-private stack placement
differs, and arbitrary mutation of a logger's private vararg slots is not
covered. Raw R0 is not asserted for this void-returning interface. All 562 R1
units compile without failures or duplicate strong symbols; imports remain
211 application / 34 bootloader, the other 561 units are unchanged and source
checks pass. Physical charging, complete fault/concurrency equivalence, byte
qualification and complete source-only firmware remain open. Source-plan
selections and G2 gates are unchanged. Exact bindings are in the
[machine-readable review](battery-c-recovery-frame-review.json).
