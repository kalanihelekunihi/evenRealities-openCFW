# Boot device-info failure state and store order

The selected `0x41d792 -> 0x41d69c` path had two source mismatches.
At native `0x41d876..0x41d878`, the dispatch caller sets R0 to the record
pointer while R2 still holds that same pointer. Native `0x41d69c` begins
with `push {r2,r3,r4,lr}`, making R2 the initial INFO output word. If the
INFO1 read of word `0x244` fails before writing that output, native uses the
pointer's low byte in record word 3. The previous C candidate initialized
the output word to zero. `device_info_dispatch.c` now passes the caller's
authenticated ambient word explicitly, and `device_info_mode0.c` seeds the
lower output with it. This qualifies the selected caller path; arbitrary
external calls to the native child would need their own R2 contract.

Native then clears record word 3 and issues four distinct RMW stores on
each path. The selected C had collapsed them into one or two stores. The
corrected C keeps every volatile read/write boundary, including the
INFO-failure path and two success subpaths. Target `unit_005.o` keeps the
record pointer in R1 at the call to `opencfw_boot_device_mode_configure`;
`unit_006.o` stores R1 to its INFO output stack slot before the lower call
and emits separate record stores.

The new coherent target receipt is
`boot-coplacement-device-mode-ambient-round/receipt.json`:
`PASS_BOUNDED_LINK`, 373 selected units, 1,010 providers, three genuine
ROM imports, 34 callback relocations, and 158,692 candidate bytes versus
148,599 stock bytes. `git diff --check` passes in Boot scope. No hardware
execution or byte-identical image claim follows from this receipt.

Explicit reviewed bindings for `0x41d792` and `0x41d69c` now record the
caller and complete child path. Rooted header-only attribution queue is
**166/654**, down from 168; whole catalogue header-only queue is **264/903**.
These are proof leads rather than missing C body counts. Remaining ROM,
indirect-root, source-data/layout and runtime gates are separate.
