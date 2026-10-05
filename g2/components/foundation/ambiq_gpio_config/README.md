# GPIO configuration, state, interrupt control and radio consumers

This component compiles unchanged pinned Ambiq SDK getter, setter and state-write bodies plus the reconstructed stock radio pin93-clear/pin138-config helper. Retained source/type/macro hashes and licenses are in SOURCE_PROVENANCE.json and STATE_PROVENANCE.json. It uses the actual shared PRIMASK helper; no executable call is stubbed.

```sh
make -C g2 ambiq-gpio-config-simulator
make -C g2 ambiq-gpio-config-simulator-test SCB_SIM_PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python GPIO_CONFIG_SIM_REPORT=build/foundation/radio-gpio-control-simulator/comparison-new.json GPIO_CONTROL_SIM_REPORT=build/foundation/radio-gpio-control-simulator/control-comparison-new.json
```

Choose a fresh report filename: output is exclusive-create. The same build target now includes state and board consumer, defaulting to build/foundation/radio-gpio-control-simulator. Prior config-only source snapshots/results remain preserved in analysis/ambiq-gpio-board-2026-10-05/prior-gpio-config-source and the old ignored build directory.

Configuration accepts logical pins0–223, validates pinned drive/pull capability tables, and writes PADKEY0x73/config/PADKEY0 under saved PRIMASK. The getter checks pin before output-nullness. The by-value configuration word is four bytes. State-write accepts a byte operation:0clear,1set,2toggle output,3disable output,4enable output,5toggle enable. Unknown operation bytes return success without MMIO. There is no pin-range check in that body: bank index wraps modulo8; bank7 aliases adjacent register families. This diagnostic behavior is not a physical-pin API. The raw-u32 adapter models stock operation truncation explicitly.

The radio helper writes WTC2 for pin93, then configures pin138 with authenticated raw3. Both statuses are ignored. Its return is void. The two calls do not form a single critical section, and no radio readiness or complete shutdown safety is established.

See [the current report](../../../analysis/radio-gpio-control-2026-10-05/REPORT.md) and [readable pseudocode](../../../analysis/radio-gpio-control-2026-10-05/pseudocode.md) for exact provenance, register offsets, comparisons and limits. Register side effects/output-active masks are synthetic fixtures; physical GPIO enable derivation, concurrent access, clocks/NVIC, board timing, full firmware reconstruction and byte equality remain unproven. The optimized tick comparison remains blocked separately.

The full upstream interrupt-control function and pin-index helper are now included, along with actual radio pin117 enable/disable, pin136 byte-truth output command and the contiguous GPIO-only shutdown slice. Reusable declarations are in gpio_interrupt_control.h; CTRL provenance is in CONTROL_PROVENANCE.json. Mask input is seven volatile32-bit words borrowed synchronously. Both-channel control rereads them per channel; it does not make a snapshot or retain the pointer. Stock validates control/null/individual pin, but does not reject invalid channel bytes. Use valid channel enum constants; arbitrary raw entry values are modeled by the explicit raw adapter. The GPIO phase excludes timer stop, caller state clearing and transport release. It does not clear pending IRQ/NVIC/callback/queued work or establish safe physical shutdown. Both test reports are exclusive-create.

Pin117 enable/disable wrappers return literal117, matching stock; it is not a HAL success/error code. The pin136 command and GPIO-only shutdown phase return void. The reviewed comparison checks these boundaries separately.
