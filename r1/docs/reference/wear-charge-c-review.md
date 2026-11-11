# R1 wear/charge transition service in C

`native_wear_charge.c` implements the 170-byte stock service at `0x4c4b8` and its existing event-service alias. It reuses the existing health-mode byte and nonzero-state helper. The actual byte-truncating, length-gated event adapter at `0x4210c` executes in the probe.

The native comparison sign-extends the previous status byte before comparing it with the full request. A changed request is stored before logging or provider calls. Request 1 tears down the wear probe, starts raw HR probing, publishes a zero state on topic 4 and creates a missing 60,000-period timer. Other requests release and then clear an existing timer, convert the current health-mode byte to nonzero state and publish it. Logging preserves its short-circuit mode reads and exact strings/IDs. The timer callback at `0x4c3d0` remains an explicit dependency; this change does not invent its implementation.

Executing the stock RW decompressor and ZI initializer confirms the new status byte at `0x2001e47a` and timer word at `0x20006ea8` both start at zero. An independent RW decoder agrees, and the compiled C object matches both owners. These are separate narrow owners; adjacent health and timer fields are not claimed. See [startup receipt](wear-charge-initialization.json).

The C service and actual event adapter pass 4,048 stock/C comparisons. Cases cover signed old values, full-word requests, byte truncation at the adapter, rejected lengths, health values, timer presence and creation failure, individual logging bits, changing logging reads, provider mutations and repeated/mixed transitions. Checks compare provider order/arguments, copied event bytes, guarded memory, preserved registers, stack pointer and interrupt masks. Private scratch, caller-clobbered registers and void returns are excluded.

Eight compiled defects are rejected: unsigned old-status comparison, wrong stored status, broadening the request-1 gate, wrong timer period, early timer clearing, lost timer-presence gate, wrong health-derived event and wrong charge event. The normal implementation is rerun after defect testing.

REA returned the complete function span and it matches the raw official application. See [REA receipt](wear-charge-c-rea.json) and [structured verification](wear-charge-c-review.json).

The license-free build compiles all 761 R1 units and composes both payloads without duplicate strong symbols. All 760 prior object hashes are identical. The application import count remains 128: `r1_event_service_0004c4b8` closes and `r1_wear_charge_timer_callback` becomes explicit. Bootloader imports remain 34. R1 source coverage passes. The global check still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Wear-probe operations, timer allocation/release, event transport and logs are modeled boundaries. Timer callback identity is checked, but callback execution, physical charge sensing and asynchronous scheduling remain unverified. Relocatable composition is not proof of complete firmware linking or device operation. Byte identity is not required for this implementation route.
