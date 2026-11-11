# Low-battery escalation C frame extraction

The stock low-battery path at `0x3d88c` now uses a C body and an explicit
frame/tail bridge in `native_battery_low.c`. REA and raw instructions confirm
that its saved R2/R3 words form the two-word record at entry SP-16. Normal
returns restore the possibly modified record; the count-nine path instead
discards it, restores the caller's frame and tail-calls the event provider.
The current bridge is 32 bytes and C body 188 bytes; stock is 176 bytes.
This conversion does not establish byte identity.

Voltage at least 3350 clears the counter. Otherwise the byte counter
increments with wraparound, logging queries retain their short-circuit order,
and the counter is reloaded after callbacks. Count nine hands off event
`0x100c` with null payload and zero length. Counts at least ten update the
record's voltage bits, obtain a timestamp, send the record to the KV helper
and set the live low-battery thread's flag. Callback changes to the record,
voltage, counter and thread handle remain observable at the native reloads.

The C helper's internal 64-bit result carries normal machine R0 in its low
word and a tail-handoff decision in its high word. The bridge restores R2/R3
on normal paths. The event path discards those words, sets the event arguments
and enters the provider with the original caller SP/LR. It does not introduce
a nested event call or restore the discarded record after the event returns.

The ignored `build/goal-r1-battery-low/verify.py` probe passes 1,850
stock-versus-C scenarios against an independent control-flow and memory
oracle. Coverage includes every initial counter value, threshold boundaries,
counter wrap, logging-mode query combinations, full-width API returns,
callback record/context changes and both return paths. Checks include ordered
context and saved-word accesses, log argument values, KV record address,
thread/event arguments, observed R0, normal R2/R3 restoration, event-tail
SP/LR, callee-saved registers, interrupt masks and callback alignment.

All 562 R1 units compile without failures or duplicate strong symbols; the
other 561 source units and manifest are unchanged. Imports remain 227
application and 34 bootloader. Exact source, manifest, native, REA and probe
bindings are in [the machine-readable review](battery-c-low-review.json).

The API boundaries are modeled. The ring log's fifth argument is compared by
value; its physical argument-stack alias with the native saved word is not
established under the additional C helper frame. Complete flag/fault identity
and physical low-battery response remain unproven. Device-context/thread-handle
ownership, final linking, provider qualification and byte identity remain
open. No G2 gates or source-plan selections change.
