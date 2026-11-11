# Motion interrupt dispatch C extraction

The machine-result/frame contract below is superseded by the [compatible C notification ABI](motion-irq-pure-c-review.md). Incidental dispatcher and callback R0 values are no longer C results.

The stock dispatcher at `0x50294` now performs its selection and null checks
in C in `native_motion_stream.c`. REA analysis agrees with the native load
order: read the selected-provider word once, then its interrupt slot at
offset 12 once. Missing selection or callback returns zero. The selected
callback is invoked even if those cells change after being read.

The operation table admits both void notifications and status callbacks.
An ordinary C void call cannot capture the native machine return value.
The C dispatcher therefore passes the captured pointer to a two-byte
`bx r0` adapter, which preserves callback-entry R0 and the callback's result
without an incompatible C call. The native dispatcher is 18 bytes; the
current C body is 24 bytes plus the two-byte adapter. No extra callback-entry
frame is observed in this compiler output.

The ignored `build/goal-r1-motion-irq/verify.py` probe passes 734
stock-versus-C scenarios. Cases cover null selection/callback, two provider
records, full-width results, selection/slot changes immediately after their
loads, register/flag clobbers, interrupt masks and callback changes to the
selected state. Checks include ordered word reads, callback identity,
callback-entry R0/SP/LR, returned R0, restored SP and callee-saved registers.

Of those cases, 112 traverse actual native/C LIS or BMA no-op callbacks or
the QMA interrupt wrapper. Probe-only callback trampolines redirect execution
while keeping the same incoming callback pointer on both sides, so the
void no-ops' preserved R0 is compared directly. The QMA wrapper retains
acquire, IRQ and release order and returns the release result regardless of
the first two results. Its bus and IRQ boundaries are modeled; the IRQ's
internal sensor reads do not execute in this probe.

Nine other motion-stream function bodies are unchanged, and the provider
selection source is unchanged. All 562 R1 units compile without failures or
duplicate strong symbols; imports remain 227 application and 34 bootloader.
Exact source, manifest, stock spans, REA and probe bindings are in
[the machine-readable review](motion-c-irq-review.json).

This remains a partial C extraction. Physical interrupt delivery, bus timing,
complete flag/register/fault-state identity, final linking, provider
qualification and byte identity remain unproven. No G2 workflow gates or
source-plan selections change.
