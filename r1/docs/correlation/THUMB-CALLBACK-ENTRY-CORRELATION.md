# Thumb callback-entry correlation

## Outcome

Ghidra represented twenty-nine executable callback/helper/task entries as odd Thumb pointers, plain
labels, or reachable code omitted from its function CSV
instead of independent functions. They are now explicit manual provenance supplements in the
source-ownership ledger. Every body is byte-pinned to the rebuilt application at load base
`0x00027000`; none of these ranges is copied into the source-built firmware.

## Exact entries

| Extent | Bytes | SHA-256 | Transparent source role |
| --- | ---: | --- | --- |
| `0x00042D28..<0x00042D2E` | 6 | `46ce7a3526ac961a61ffc8aa365a532374d31a64e5dc370ffbd0076019594aaf` | PMIC post timer sets worker flag `0x08` |
| `0x00042D2E..<0x00042D3E` | 16 | `afcc5ed6008cfba661948e736b4f83763b8ebb33bdd1d0ef365c3c0aa3f7b16d` | invoke generic-device slot `0x0C`, then set worker flag `0x01` |
| `0x00042EE8..<0x0004301A` | 306 | `7fa0d4b5da336d725c3fda8749821b3248350985ff0eb34c335d570bd42030af` | delayed target-glasses validation and disconnect policy |
| `0x00046F88..<0x00046F8E` | 6 | `972ff6f355a5b431c393c6dfaf0f12173dcf4a44a787a81bb9684b5157d3f18d` | release shared-power client 2 (touch) |
| `0x0004B6C0..<0x0004B6FE` | 62 | `01529383d9556740deb853204cb9d84bd4d04c68b2cbf462f02bd9a35a509195` | start/stop the product one-shot `"temp"` listener |
| `0x0004B920..<0x0004B9F0` | 208 | `9a796f9f908343c06334fa122a9f41771468e57d28d37ccff2573fef5cc8b8bb` | bounded one-shot temperature callback |
| `0x0004BBF0..<0x0004BC26` | 54 | `f515e0da5298838c50d396626160eea844f8f9cc30a9d6f9ab4e306603f90f61` | gated `"timing"` temperature-listener start |
| `0x0004BC40..<0x0004BCD6` | 150 | `8ffdb4962894501a85292a14defa42932f2a3fdea2d2e349168b99d7798c7296` | bounded timing-temperature callback |
| `0x0004E008..<0x0004E05A` | 82 | `09faf2697afaaa3ccdc2ce5c7b882246693646820df7c8e05d78f108c0ef5921` | log phone/glasses handles, then set role-sync flag `0x100` |
| `0x00058D4A..<0x00058D52` | 8 | `2467e717b3f3559c4a73231c3d00bf66d382a6d43845761a699c20f26973c1d9` | compare tensor-arena live entries by first-word offset |
| `0x0006A600..<0x0006A612` | 18 | `533f977264f4879dd87b28676cd5d535bbc148abad73bc70311f3e90b5bb2828` | accelerometer stream read/copy callback |
| `0x0006A61C..<0x0006A638` | 28 | `f509ddc6020e95e31b38ba95ee419b575ea33367ab4477fcd13db0db30d0e2a9` | register the singleton `"acc"` listener once |
| `0x0006A648..<0x0006A65E` | 22 | `b73a06d0cafe595c39bf96d8f8ccdd65b9060c59481bf3410da11ee789d1bddc` | unregister and clear the singleton `"acc"` listener |
| `0x0006A230..<0x0006A234` | 4 | `737ab2b8b75c34dcd62999cfda6d5ef469cd4f3f49960ca53158d6b8e306134c` | FlashDB health timestamp tail veneer |
| `0x0006ACC8..<0x0006ACD2` | 10 | `3badaeb80fceb23c967ef58d3c3da3c18870fba79034fd608da8659c586a927f` | clear staged GoMore acc/raw counts after success |
| `0x0006B0D4..<0x0006B10E` | 58 | `8f159dceef23f9d294812d1b330e4b31335d6965de6393f3e06d908dfd9f1db2` | enforce the required acc/raw readiness barrier |
| `0x0006B1B8..<0x0006B1F4` | 60 | `74acdce104fa24422fcb4b7101bb6a70c143d3442bb4fe23f8fe94ad21687eed` | stage direct heart rate and readiness bit `0x04` |
| `0x0006B1F4..<0x0006B228` | 52 | `bf19893965dc98b713fe3c861943ce8505cfe4434b2cacfa44a6c69133770e8f` | clear/copy the four-value HRV auxiliary lane |
| `0x00075CCC..<0x00075CDE` | 18 | `527b41112c9686559b46008cea21a67ecaa8ef7ab7bea1f74fea9a953a42e7e1` | FlashDB health-TSDB lock callback, wait forever |
| `0x0007F17C..<0x0007F188` | 12 | `ae5ea793492667852747e0c14d33a68a2296f625f20922a731083639b4846b9f` | LIS2DW12 bus-read veneer at address `0x18` |
| `0x0007F188..<0x0007F194` | 12 | `b3885f000d7970d0322dce0e7ede723a6a005499ff5db40cb71f0a7bf1157c12` | LIS2DW12 bus-write veneer at address `0x18` |
| `0x000882AC..<0x000882EC` | 64 | `28d8568d7f96013e7c9255881ce0b659f1ed3071d7bd35492f99de6ad18027ab` | route packed connection/context selectors to empty BLE-thread events |
| `0x000920EC..<0x0009216C` | 128 | `a5c8694c233c107da3df11c43b95747523afd8c1d9fbfb41531dd964096fcecb` | channel-1 transmit task startup and dispatch/suspend flag loop |
| `0x00092178..<0x0009223E` | 198 | `75497f7603d5c266081039ff61cb0821fccef22bc7c4aaeb80aedda9809d934b` | BAE8 input task startup and drain/suspend flag loop |
| `0x0009227C..<0x000922FC` | 128 | `c7aa95dfd7e4c12af796c706385ec6f28cb3de700daae8146fa3548f59d2f025` | shared EUS/explicit transmit task startup and dispatch/suspend loop |
| `0x0009230C..<0x0009238C` | 128 | `65da7625dd83c8f74a802a46676632679fc978ef5268b4981207facb30d45a45` | factory-marker input/sensor-scheduler task orchestration |
| `0x000926DC..<0x000927BA` | 222 | `b13c5bc01f09f51f5b4dc9a79566d9b5dcaff74cdf6e8447b12e3d8affa8a179` | storage task startup order and event/suspend flag loop |
| `0x00093EE4..<0x00093EF2` | 14 | `856dec2d21da309fc9de8a9d2bb79f9fb73ce6fd300d7b3cceb5bf5f6b8d392e` | FlashDB health-TSDB unlock callback |
| `0x00096A60..<0x00096A7A` | 26 | `4c74110b82ab232183d7aa09415da2327258ecaa7e51efb1a3eaf54f307e2553` | re-arm self with `0x199`, then set worker flag `0x04` |

## Source composition

The three PMIC action-only callbacks are represented by
`r1_pmic_retry_callback_plan`, `r1_pmic_post_timer_callback_plan`, and
`r1_pmic_post_device_callback_plan`. The target-peer callback reuses the tested two-target planner,
the role-sync callback is `r1_connection_control_role_sync_thread_flags`, and the newly closed
connection-event callback maps to `r1_connection_control_delayed_event_plan`.

The remaining callbacks were already compiled transparently at their actual provider boundaries:
the Zephyr accelerometer provider, LIS2DW12 bus adapters, delayed touch-power release, and FlashDB
health mutex lock/unlock functions. The ledger now names those source bodies instead of allowing
their callback entries to disappear between neighboring Ghidra functions.

The widened census also reconciles the already reconstructed temperature and GoMore topic paths.
The paired temperature start/callback entries map to
`gomore_primitives_temperature_measurement_begin` and
`gomore_primitives_temperature_measurement_step`; the timing activation policy stays dormant.
The GoMore entries map to `gomore_primitives_topic_update_complete`,
`gomore_primitives_topic_update_take_ready`, `gomore_primitives_topic_heart_rate_ingest`, and
`gomore_primitives_topic_hrv_ingest`. Their acc/raw peers were already supplements, so all four
topic callbacks plus readiness and successful-update cleanup now have explicit ledger rows.
The tensor comparator is the local static used by `quantized_runtime_arena_allocate`; the
four-byte health timestamp veneer maps to the source-built `health_get_time` binding and retains
the reconstructed clock backend as a separate typed provider.
The storage task entry maps to `r1_storage_task_plan_startup` and
`r1_storage_task_plan_flags`; CMSIS queue/thread operations and all ten separately owned startup
callees keep their existing source boundaries.
The channel-1 task entry maps to `r1_channel1_task_plan_startup` and
`r1_channel1_task_plan_flags`; the source-built scheduler owns its CMSIS queue and worker and uses
typed owned events instead of stock heap-envelope pointers.
The BAE8 input task similarly maps to `r1_bae8_input_task_plan_startup` and
`r1_bae8_input_task_plan_flags`; live receive dispatch remains in the transparent Nordic/Zephyr
BAE8 bindings.
The shared transmit sibling maps to `r1_shared_tx_task_plan_startup` and
`r1_shared_tx_task_plan_flags`, composed by the source scheduler's typed shared queue.
The factory-input task maps to `r1_factory_input_task_plan_startup` and
`r1_factory_input_task_plan_flags`; its five startup callees remain separately source-routed.

No callback enables a new public command, bypasses authorization, embeds stock bytes, or performs
deployment. Hardware operations remain behind their existing typed Nordic, ST, FlashDB, motion,
and shared-power providers.
