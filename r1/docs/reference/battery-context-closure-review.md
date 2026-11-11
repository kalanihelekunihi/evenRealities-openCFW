# Battery shared-context dependency closure

Normal R1 composition now uses canonical C owners for the 68-byte battery
device context, 92-byte runtime context, two thread handles and shared-power
client word: 172 bytes total. `native_battery_context.h` provides byte and
typed union views with checked offsets. Status bytes 44/45 share the device
owner, and the ADC-cache pointer shares runtime offset 16. Independent status
and ADC-cache definitions and the old split context slices were removed.
The existing context unit now participates in composition.

The source constants retain the runtime sentinels and four six-halfword
cadence rows. No cold pointer or default payload is invented. The ignored
`initialization.py` probe checks the authenticated native scatter descriptors,
executes both stock startup handlers and independently expands compressed
initialized data. All 172 compiled owner bytes match the resulting RAM;
guards remain unchanged. The device context is inside the native zero region.
Each owner is four-byte aligned and occupies non-executable writable data.
This establishes these cells, not ownership of the whole startup image.

Fresh REA analyses bind the zero handler, ADC cache and charging-cadence
selector. The ignored `verify.py` probe passes 1,080 stock-versus-C cases:
256 shared-status/reset cases, 32 cache-to-filter workflows, 36 thread-flag
cases and 756 cadence cases. The graph executes actual source cache, status
getters, progress reset, filter, thread-flag adapter and cadence functions.
It checks shared field addresses, cache-hit/miss behavior, filter handle
handoff, all cadence selectors, boundary levels, returned values, final
context bytes, callee-saved registers, SP, interrupt masks and callback
alignment. The dedicated probe places the owners at their native addresses;
final firmware placement remains a separate gate.

All 562 R1 units compile without failures or duplicate strong symbols.
Application composition now includes 452 objects. Seven imports close with
no additions: device/runtime context roots, battery and low-battery thread
handles, shared-power clients, and the two device-status bytes. Application
imports fall from 227 to 220; bootloader imports remain 34. Macro views
replace those former standalone data names, so their consumers now reference
the canonical storage owners directly.

Exact source/header, manifest, startup bytes, native analyses and probe
bindings are in [the machine-readable review](battery-context-closure-review.json).
Registry lookup, ADC dispatch, delay, configuration, clock, KV-kind and
thread-flag APIs are modeled. The full battery/event/RTOS graph, hardware
accuracy/timing, final boot/link placement, provider qualification and whole
image byte identity remain unproven. No G2 gates or source-plan selections
change.
