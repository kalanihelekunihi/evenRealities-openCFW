# Bounded stock-firmware knowledge batches

These folders contain readable manual reconstructions, original-instruction
checks and evidence receipts for stock G2 `2.2.6.10`. They are knowledge artifacts,
not completed firmware source, patches, or byte-equality claims. Cases overlap
across batches; counts are not distinct whole-image coverage. Follow each README
for exact addresses, authenticated image hashes, stubs and remaining limits.

| Batch | Main recovered interface / functions | Passing instruction cases | Main limit |
| --- | --- | ---: | --- |
| [Ring client](ring-client-2026-09-30/README.md) | R1 connection/service client call paths |25| External BLE providers |
| [Ring protocol](ring-protocol-2026-09-30/README.md) | Command payloads, `ring_service` TX lifetime |42| Synthetic scheduling, delay units not assumed ms |
| [Ring actions / ATT](ring-actions-att-2026-09-30/README.md) | Touch/action mapping and ATT copy boundary |46| No hardware lifetime-failure claim |
| [Ring TX ownership](ring-tx-ownership-2026-10-01/README.md) | Queue send/drop/cancel ownership |25| Scheduler and shutdown interleavings |
| [Ring allocator/lifecycle](ring-allocator-lifecycle-2026-10-01/README.md) | Size classes, budget, reachable lifecycle boundaries |49| Quiesce/drain proof requires missing trace/state |
| [Audio stream](audio-stream-2026-10-01/README.md) | `SVC_PcmAppProcessData`, LC3 framing and205-byte body |26| Codec provider stub, failure not flagged on wire |
| [Audio BLE metadata](audio-ble-metadata-2026-10-01/README.md) | `Thread_MsgTxByBle`, ESS/ATT copy, energy/angle units |30| Scheduler synthetic; correlation was stubbed here |
| [ESS GATT](ess-gatt-2026-10-01/README.md) | Service registration, UUIDs, `attSetMtu`, MTU request |13| Negotiated peer behavior lacks radio trace |
| [Audio angle](audio-angle-2026-10-01/README.md) | `service_algo_cross_correlation` and source-angle wrapper |13| Synthetic PCM, asin math stub, physical orientation unknown |

App-facing starting points: ESS GATT for discovery UUIDs; audio BLE metadata for
the notification parser; audio angle for why silence can produce -90 degrees;
ring actions for gesture semantics. No angle/encoder validity flag is established.

Historical display port/manager recovery is already extensive: see consolidated
`../docs/reference/capabilities.md` and its commit-pinned evidence. The angle batch
explains why it used the authorized audio fallback instead of duplicating that
work. Historical overlay/source-closure results do not satisfy current workflow
gates. Shared campaign state is deliberately not maintained by these folders.
