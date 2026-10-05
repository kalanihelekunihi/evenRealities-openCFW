# GPIO configuration, state and radio consumer foundation

This component compiles unchanged pinned Ambiq SDK getter, setter and state-write bodies plus the reconstructed stock radio pin93-clear/pin138-config helper. Retained source/type/macro hashes and licenses are in SOURCE_PROVENANCE.json and STATE_PROVENANCE.json. It uses the actual shared PRIMASK helper; no executable call is stubbed.

```sh
make -C g2 ambiq-gpio-config-simulator
make -C g2 ambiq-gpio-config-simulator-test SCB_SIM_PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python GPIO_CONFIG_SIM_REPORT=build/foundation/ambiq-gpio-board-simulator/comparison-new.json
```

Choose a fresh report filename: output is exclusive-create. The same build target now includes state and board consumer, defaulting to build/foundation/ambiq-gpio-board-simulator. Prior config-only source snapshots/results remain preserved in analysis/ambiq-gpio-board-2026-10-05/prior-gpio-config-source and the old ignored build directory.

Configuration accepts logical pins0–223, validates pinned drive/pull capability tables, and writes PADKEY0x73/config/PADKEY0 under saved PRIMASK. The getter checks pin before output-nullness. The by-value configuration word is four bytes. State-write accepts a byte operation:0clear,1set,2toggle output,3disable output,4enable output,5toggle enable. Unknown operation bytes return success without MMIO. There is no pin-range check in that body: bank index wraps modulo8; bank7 aliases adjacent register families. This diagnostic behavior is not a physical-pin API. The raw-u32 adapter models stock operation truncation explicitly.

The radio helper writes WTC2 for pin93, then configures pin138 with authenticated raw3. Both statuses are ignored. Its return is void. The two calls do not form a single critical section, and no radio readiness or complete shutdown safety is established.

See [the current report](../../../analysis/ambiq-gpio-board-2026-10-05/REPORT.md) and [readable pseudocode](../../../analysis/ambiq-gpio-board-2026-10-05/pseudocode.md) for exact provenance, register offsets, comparisons and limits. Register side effects/output-active masks are synthetic fixtures; physical GPIO enable derivation, concurrent access, clocks/NVIC, board timing, full firmware reconstruction and byte equality remain unproven. The optimized tick comparison remains blocked separately.
