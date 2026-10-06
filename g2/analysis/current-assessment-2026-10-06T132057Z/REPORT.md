# Current OpenCFW assessment

Fresh snapshot: 2026-10-06T13:20:11.700722+00:00. Official G2 bundle: **4,301,227 stored bytes**, SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`. All six payload hashes reauthenticated. Assessment only: no firmware/source changes, builds, emulation, commits or flashing.

| Evidence footprint | Current bytes / stored bundle | Percent | Change since Oct 5 15:33 |
|---|---:|---:|---:|
| assembly_export_bytes | 599,718 / 4,301,227 | 13.9430% | +109,518 |
| raw_pseudocode_bytes | 1,902,397 / 4,301,227 | 44.2292% | +0 |
| authenticated_scoped_review_bytes | 204,660 / 4,301,227 | 4.7582% | +7,660 |
| partial_C_compared_trace_bytes | 8,418 / 4,301,227 | 0.1957% | unmeasured then |

These are evidence footprints, **not completion percentages**. Generated pseudocode is unchanged; authenticated scoped reviews gained 7,660 bytes. Reviewed ranges do not certify all branches or semantic completeness. The raw catalogue addresses 1,902,397 of 1,912,325 candidate bytes (99.4808%); the catalogue is not an exhaustive executable map.

| Payload | Stored bytes | Assembly footprint | Generated pseudocode | Scoped review | Partial compared C trace |
|---|---:|---:|---:|---:|---:|
| codec | 326,092 | unknown | 28.38% | 0.67% | 0 (0.0000%) |
| ble_em9305 | 211,948 | 98.53% | 0.00% | 0.72% | 0 (0.0000%) |
| touch | 34,464 | unknown | 80.89% | 46.21% | 234 (0.6790%) |
| case | 55,784 | 73.64% | 77.21% | 40.90% | 0 (0.0000%) |
| apollo_bootloader | 148,599 | 83.42% | 75.71% | 68.60% | 0 (0.0000%) |
| apollo_main | 3,523,396 | 6.41% | 46.16% | 1.71% | 8,184 (0.2323%) |

Partial C is a conservative **tested instruction footprint of compiled source slices**, not an exhaustive source map. Uncounted C may exist. Cuts, stubbed historical providers, O0/O2 profile differences and synthetic MMIO remain bounded per result. Complete blob-free payloads: **0/6 (0%)**; byte-identical source-built bundles: **0/1 (0%)**.

Checkout has **89 foundation C/header files**, unchanged since Oct 6 01:59; trace union likewise remains 8,418 bytes. Four C/header files added since the 01:19 scan cover event consumption and registration. HEAD remains `4ab13514dfcfd96f835784118cf580c48715c2d3`. Source is visible to Git; build outputs are ignored. Latest registration hash bindings match; the older notification Makefile binding remains stale after the registration target addition.

| Core focus | Completion | Concrete evidence / remaining boundary |
|---|---|---|
| Boot/reset | Unknown | Startup/maps exist; no complete reset-to-task proof; resident ROM timing missing. |
| RTOS | Unknown | Queue/event/ready/resume/tick slices compile and have bounded comparisons; optimized tick emulator divergence and full scheduler/context switching remain unresolved. |
| GPIO | Unknown | Pin configuration/state/IRQ/radio callback slices; synthetic registers do not establish electrical/board behavior. |
| DMA/cache/audio | Unknown | Cache operations, 3200-byte borrowed PCM selection, next-buffer rearm, age 0–40 filtering and owner/callback registration. No hardware DMA lifetime or coherency proof. |
| Communications/IPC | Unknown | Touch queue/trigger slices and radio/WSF glue; normal audio BLE copy/IPC source integration remains outstanding. Diagnostic file callbacks are not BLE. |
| Hardware buses/power | Unknown | MSPI/CMDQ and radio IOM/power preparation slices; whole-device initialization/shutdown incomplete. |

Machine-readable focus entries provide deduplicated first-credit trace contributions; these are navigation aids, not subsystem percentages. No exhaustive core-area executable denominator exists, so assigning completion scores would be unsupported.

Non-code context: the earlier bounded map identifies 151,707 confirmed non-code bytes and 1,280 metadata/padding bytes. The classification was not expanded here; unresolved bytes include code, compressed initializers and resources. CPU runtime expansion must not be added to stored-byte coverage.

Upstream attribution remains separate: EM9305 has a recorded 74.50% archive match of its 210,888-byte app record, not a 74.50% source-built payload. FreeRTOS/CMSIS/Ambiq lineage and pinned upstream source help reconstruction but do not prove a matching compiled replacement. EvenHub SDK/application source does not count toward hardware firmware coverage. This authenticated six-payload assessment does not establish an updated R1 percentage.

Latest saved registration aggregate: 44 modules, 228 tests, 222 passes, six method skips and one setup skip, zero failures/errors; affected checks eight passes. These results were hash-checked, not rerun. Hardware concurrency, full transport lifetimes, ROM timing, and source-identical builds remain unproven.

Deliverables: `coverage-comparison.json`, `partial-c-trace-ledger.jsonl`, `partial-c-evidence.json`, `checkout.json`, fresh assembly/review/bundle metrics, and inherited upstream/non-code context. Fresh counting-method logs and ledgers are under `g2/build/audits/2026-10-06-current-assessment-refresh/`.

Final index preservation check: True. Registration saved-result bindings checked: 5; mismatches: 0.
