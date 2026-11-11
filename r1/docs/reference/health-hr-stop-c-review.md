# R1 HR/HRV wear-change shutdown in C

`native_health_hr_stop.c` implements the group-4 callback `0x49d28` and HR
timer release `0x49d10` in ordinary C. The [receipt](health-hr-stop-c-review.json)
binds REA bytes, production hashes, replay, startup initialization, rejected
defects, qualification and normal builds. The callback's former frontier extent
was unknown (zero); decoded code ends at `0x49da5`, establishing **126 bytes**.
The timer-release routine is 20 bytes. Neither is instruction-qualified.

The callback captures its event byte once before fresh log-mode queries and
stock status logging. Captured status **exactly 1** skips cleanup, even when
providers later change the event byte. Other statuses inspect four HR stream
slots in order, reading each fresh, unregistering `"hr"` for a nonzero handle,
then clearing that slot **after** the provider returns. It next executes C HRV
session teardown, fresh HRV timer release, fresh HR timer release, then
authorization `(5,0)`. The authorization tail entry retains stock SP. Its
return value is ignored by the multicast callback contract.

The HR timer is the existing shared timing-state word at offset 12, now named
`hr_timer`; its ownership and cold-zero image are reused rather than duplicated.
The helper reads it fresh, releases a nonzero value, then clears it late. The
new unit owns only the four-word HR handle array at `0x2001a2ec`. Executing
stock RW/ZI scatter handlers on poisoned SRAM, with guards and an independent
compressed RW decoder, verifies all **16 bytes cold-zero**. Shared timing-state
and other previous object hashes remain unchanged.

Validation passed **10,816 paired cases: 9,792 completed calls and 1,024
expected invalid-event faults**. Tests cover statuses 0/1/2/255, all handle-slot
masks, independent zero/nonzero HR/HRV timers, changed log modes, event aliases,
provider errors, and provider mutations of current/future handles and shared
timers. Captured versus fresh state and late clears are compared through
provider arguments/order, public SRAM and write widths. Null and `0xffffffff`
events fault before providers or state writes. Saved integer/FP registers,
SP, masks and FPSCR agree on completed returns. Void R0, caller-clobbered
registers/APSR and private stack bytes are excluded.

Actual C HRV session teardown, HRV timer-release coordination, EABI memory
clear and musl memset execute. Lower unregister/timer-release, authorization
and logging providers are modeled. Provider mutations can repopulate earlier
slots or timer fields; the callback preserves stock ordering rather than
adding a final blanket clear. Nine compiled defects were rejected: broad
status guard, early stream clear, cached handles, wrong timer field, early
timer clear, swapped timer order, omitted session cleanup, wrong authorization
argument and wrong ring tag.

All **659 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **658 prior objects** are unchanged; only the
registration source's callback prototype changes, alongside the shared header's
field name. The group-4 callback import resolves without new imports, leaving
**167 application / 34 bootloader imports**. No new bytes qualify as exact;
the canonical source plan remains at 4,369 source-built bytes. The fresh hybrid
still matches the locked artifact through executable pull-through. Full
authorization, final source-only linking, concurrency and physical HR/HRV
shutdown remain unproven.

The later [HR mode transition review](hr-mode-transition-c-review.md) extends the canonical handle owner to five words because stock initial mode 4 indexes the adjacent slot. It authenticates all 20 cold-zero bytes, preserves existing stop instructions/relocations and reruns the controller/result regressions.
