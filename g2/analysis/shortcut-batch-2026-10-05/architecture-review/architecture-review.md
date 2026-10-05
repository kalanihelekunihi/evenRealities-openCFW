# Apollo architecture boundary and attribution review

This is a bounded architecture/source-attribution review of the locked G2 documentation and saved resource proof. It does not alter firmware, source, or shared coverage state.

## Execution and responsibility boundaries

The Apollo510B is an embedded Cortex-M55 target. The documented chain starts in Ambiq secure boot ROM/SBL, continues through an Even bootloader image, then into a statically linked Apollo application. The ROM/SBL is a protected 64 KiB MRAM region and is absent from EVENOTA. The application startup uses a scatter/decompression table and copies at least a delay loop into ITCM; therefore address-space and initialization assumptions include RAM/TCM execution. This is neither a desktop OS nor a process-separated userland model. (`g2/docs/reference/memory-map.md`, §§1–3; `g2/docs/reference/toolchains.md`, §§1–2.)

Within Apollo main, FreeRTOS 10.5.1 is the scheduler/kernel with a G2 TCB patch; CMSIS-RTOS2 is a wrapper/API surface, not a separate OS. IAR DLIB/compiler runtime and the IAR Cortex-M55 port supply ABI, startup, exception and C-runtime behavior. Above that, AmbiqSuite HAL and device drivers own peripheral configuration and low-level transfers; product modules bind those transports to sensors, display, storage, peer processors, and board policy. Cordio is BLE host middleware, while EM9305 is a distinct radio-controller firmware processor. LVGL/FreeType/Nema are display/UI middleware and backends. Littlefs/FlashDB/NOR form storage middleware. Product protocols, service threads, settings, OTA, sensor hub, EvenHub/device features, callbacks, and UI modules are application glue or policy layered on these facilities. See `g2/docs/reference/libraries.md` §§1–2, `g2/docs/reference/capabilities.md` subsystem tables, and `g2/docs/reference/memory-map.md` §§2–3.

A concise dependency direction is:

`Apollo ROM/SBL → bootloader/startup → IAR runtime + FreeRTOS/CMSIS wrapper → Ambiq HAL/peripheral transport (GPIO, DMA, IOM/MSPI/I2S, timers, display) → vendor middleware/drivers → product services/protocols/policy → EvenHub and user-facing product/UI modules`.

This is a conceptual layering, not a proven universal call chain. Product glue may call HAL or middleware directly, and some modules are cross-cutting. The product also spans independently executing EM9305, GX8002 codec, PSoC touch, and STM32 case payloads; they are not processes under Apollo's RTOS. (`memory-map.md` §1.)

## Attribution and authorship

The docs support positive provenance for selected dependency bytes and changes: examples include a byte-identical Ambiq LVGL backend subtree, a recovered FreeRTOS TCB patch, and identified G2 EasyLogger/printf adaptations (`g2/docs/reference/libraries.md` §§1.1–1.2). These establish code lineage or a downstream delta, not the identity of the individual author or the authorship of all functions in a module.

The library reference explicitly warns that the selected upstream commit is a reproducible baseline, not a claim about the private producing checkout; exact private checkouts are generally unobservable. Retained `__FILE__` paths anchor source paths/modules, not author identity. Capability labels such as “first-party” and closed-module-manifest attribution are useful functional ownership hypotheses, but without retained path, source/object match, or other direct provenance they do not independently prove Even authorship. The 1,911-function / 299,736-body-byte “unanchored first-party remainder” is especially explicit about lacking retained-path anchors (`g2/docs/reference/capabilities.md`, Sensors/overview-area remainder row). Treat this as a census classification, not an author-proven set.

Held-out spot check: `0x004E1406–0x004E1442` is labeled “EvenHub IMU enable policy” in capabilities and “first-party / Strong” in `g2/symbols/apollo_main.tsv`, but its evidence field points to a closed-module census and `g2-evenhub-main` function-map manifest rather than a retained source path or source/object hash comparison. The symbol inventory supplies a body SHA-256 (`64a0a79c…`), which authenticates the catalogued bytes but does not establish who authored them. I did not find the referenced generated manifests in this checkout. This corroborates product-function attribution at the module/behavior level, while individual authorship remains unproven on the available evidence. No broader decompilation was performed.

## Resource shortcut review

`resources/extract.py` authenticates the official payload by SHA-256, checks the prior validation record against that same payload, validates the 28-byte descriptor fields and exact payload/runtime pointer conversion (`runtime = payload offset + 0x437FE0`), checks pixel extent `stride × height`, verifies pixel hashes, and roundtrips generated grayscale PNGs back to identical L8 pixels. It also rejects a wrong color-format byte. `resources/README.md` and `extraction.json` correctly limit the result to six already-admitted stored assets: 28,872 unique pixel bytes, zero newly classified bytes. It does not establish live panel rendering, UI reachability/global usage, artwork semantics/authorship, font coverage, other 422 candidates, or compressed resources. The saved consumer trace is appropriately presented as bounded constructor/decoder admission evidence with explicit allocator/cache/alignment stubs, not as renderer execution. The script writes ignored PNG/L8 outputs and rewrites its own extraction report when run, so this review inspected its logic and saved report rather than rerunning it.

Address-coordinate caution: the Apollo resource script's `0x437FE0` adjustment is specifically for its official OTA image, which includes a 32-byte preamble before the `0x438000` main-image link base. Do not generalize that to another payload/wrapper. In particular, the touch image's FWPK32B wrapper prefix must be included when converting payload-relative code/data offsets to official-file offsets; the current corrected mapping cited by the parent is decoded touch offset `0x5F18` → official-file offset `0x5F38` (hash `07627776…`) and wrapper offset `0x9250` → official-file offset `0x5F70` (hash `c7729e5d…`). This review did not independently recalculate those touch slices. The distinction matters because hashes and source attribution are only meaningful when the exact authenticated image and coordinate origin agree.

## Evidence references

- `g2/docs/reference/memory-map.md`: Apollo boot/main boundaries, vector/startup/scatter table, runtime RAM/TCM, companion processors, peripheral base examples.
- `g2/docs/reference/libraries.md`: dependency identity/configuration, confidence conventions, explicit selected-commit versus private-producing-checkout caveat.
- `g2/docs/reference/toolchains.md`: IAR/DLIB, FreeRTOS port, startup evidence, compiler-release limits.
- `g2/docs/reference/capabilities.md`: functional/module capability rows and explicitly unanchored remainder.
- `g2/symbols/apollo_main.tsv`: held-out `0x004E1406` interval, module/confidence/evidence, body digest.
- `g2/analysis/shortcut-batch-2026-10-05/resources/{README.md,extract.py,extraction.json}` and `g2/analysis/firmware-byte-map-2026-10-05/display-proof/{pseudocode.md,validation.json}`: typed asset storage and limits.
