# Battery cached-class dependency closure

Normal composition now includes the existing C `power` and `dev_info` class
records and their symbolic handles from `native_battery_kv_config.c`. The
28-byte power class and 76-byte device-info class retain their native keys,
tags, flags, payload sizes and initial values. The handles at `0x20007df8`
and `0x20007de8` bind to the classes at `0x20006abc` and `0x200069a8`,
respectively. Additional layout assertions check the cached-class headers.

The ignored `initialization.py` probe executes the actual stock decompressor,
checks its guards and validates the initialized-data hash. All 104 class
bytes match the compiled C objects. Each four-byte handle has exactly one
`R_ARM_ABS32` relocation to its class; the linked probe's handle bytes also
match stock. All four objects are aligned to four bytes in writable,
non-executable data. These 112 bytes do not establish whole-arena ownership.

Fresh REA analyses bind the native cached-class reader and writer. The ignored
`verify.py` probe passes 1,341 native/source workflows: 264 for each battery
configuration getter and 549 for the device-info field setter. Actual
cached-class read/write code and the pinned musl copy routine execute.
Only critical-section callbacks are modeled. Cases cover size rejection,
payload changes during callbacks, post-copy scratch changes, live port and
handle replacement, dirty flags, null input, input alignment and aliasing.
Checks include API/copy arguments, class bytes and guards, handle reload,
getter results/R3, callee-saved registers, SP and interrupt masks. This
extends the recent getter-frame repair through successful cached reads.

All 562 R1 units compile without failures or duplicate strong symbols.
Application composition now includes 453 objects. The two record-handle
imports close with no additions, reducing application imports from 220 to
218; bootloader imports remain 34. The other 561 source units are unchanged.
Exact source, manifest, startup data, relocations, native analyses and probe
bindings are in [the machine-readable review](battery-kv-closure-review.json).

Probe placement is fixed to native addresses; final firmware placement and
boot integration remain unproven. Flash commit/recovery, concurrent access,
physical battery behavior, complete private-frame/fault identity, provider
qualification and whole-image byte identity remain open. The distinct
`r1_device_info_kv_handle` used by the 124-byte read retains its existing
C owner in `native_protocol_serial.c`; it is not aliased to this 52-byte
record handle. No G2 gates or source-plan
selections change.
