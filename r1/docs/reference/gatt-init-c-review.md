# R1 GATT context initialization in C

The linked `native_gatt_observer.c` unit now supplies `nrf_ble_gatt_init`,
corresponding to stock `0x78186`. Previously that public API existed only in
the excluded SDK unit. The implementation uses the already qualified C link
helper and adds no compilation unit or shared configuration override.

Stock rejects a null context with status 14. Otherwise it stores the callback
at offset 32, sets peripheral/central desired MTUs to 247 and data length to
251, then resets all three links in order. It returns zero without invoking
the callback. The C code preserves this policy, including the native 251 value
independently of the historical SDK configuration seed's 27. Compile-time
assertions pin the 36-byte context and all relevant offsets. Padding at offsets
5, 30 and 31 remains untouched.

REA/Ghidra read the complete 44-byte stock initializer. The actual production
object passed 6,144 direct stock/C initializations, eight paired null cases and
1,280 paired init/disconnect/reinit sequences. Direct tests cover all repeated
seed byte values, aligned context locations, callback pointer words and both
PRIMASK settings. An independent oracle checks context bytes, guards and all
22 writes' order, width and value. Integration checks all three links and
invalid connection handles, callback replacement, unchanged event buffers and
the absence of callback/provider/SVC execution. Returns, callee restoration,
SP and interrupt masks are checked. Both initializers call the real C link
helper at a 16-byte frame depth.

Five negative controls reject data length 27, an omitted third link, incorrect
null status, a padding overwrite and callback-store reordering. Caller-clobbered
values other than R0, APSR, live helper registers and private stack bytes are
excluded. Null and aligned mapped contexts are tested; arbitrary faults, aliases,
concurrency and real radio/SoftDevice operation remain unproven.

All 590 R1 units compile and compose without known failures or duplicate strong
symbols. The other 589 objects, and the changed unit's prior allocated sections
and relocations, are unchanged. Imports remain 159 application and 34 bootloader.

The new initializer compiles to 40 bytes and is not an exact replacement for
the 44-byte stock body. Qualification reselects only the existing exact 24-byte
link helper. The canonical source plan remains unchanged. The hybrid application
retains locked SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,269 source-built, 641,891 binary-pull-through and 248 resource bytes.
Complete source linking, physical hardware support and a byte-identical source
rebuild remain unfinished.

The [receipt](gatt-init-c-review.json) records sources, compiler arguments,
hashes and evidence. Ignored reproduction inputs are under
`build/goal-r1-gatt-init-c/`; current reports are
`build/sources-goal-r1-gatt-init-c/report.json` and
`build/hybrid-goal-r1-gatt-init-c/build-report.json`.

The newer [typed SDK call review](radio-sdk-c-review.md) reruns these regressions
while replacing handwritten radio supervisor-call wrappers.
