# Nordic Peer Manager GATT-cache closure

Ten exact functions / 784 executable bytes now route to Nordic SDK 17.1.0:

| Extent | Bytes | Symbol | Source |
|---|---:|---|---|
| `0x0006EDCC..<0x0006EDE2` | 22 | `gscm_db_change_notification_done` | `gatts_cache_manager.c` |
| `0x0006EDE8..<0x0006EDF8` | 16 | `internal_state_reset` | `gatts_cache_manager.c` |
| `0x0006EDFC..<0x0006EEA4` | 168 | `gscm_local_db_cache_apply` | `gatts_cache_manager.c` |
| `0x0006F0F8..<0x0006F116` | 30 | `gscm_service_changed_ind_needed` | `gatts_cache_manager.c` |
| `0x0006F118..<0x0006F194` | 124 | `gscm_service_changed_ind_send` | `gatts_cache_manager.c` |
| `0x00075A08..<0x00075AF2` | 234 | `local_db_apply_in_evt` | `gatt_cache_manager.c` |
| `0x00075B10..<0x00075B1A` | 10 | `local_db_update` | `gatt_cache_manager.c` |
| `0x0008A928..<0x0008A934` | 12 | `service_changed_pending_flags_check` | `gatt_cache_manager.c` |
| `0x00091084..<0x0009110A` | 134 | `store_car_value` | `gatt_cache_manager.c` |
| `0x00094AB0..<0x00094AD2` | 34 | `update_pending_flags_check` | `gatt_cache_manager.c` |

The closure additionally covers module reset, Service Changed state lookup/clear and pending-flag
iteration, local-update flag setting, and pending-update iteration. The cache apply uses Nordic's retry/flag fallback and
the indication sender retries
Service Changed on `BLE_ERROR_INVALID_ATTR_HANDLE`. The event wrapper maps success, busy, storage
full, invalid connection/data, and unexpected errors into the exact Peer Manager events/flags.
The CAR helper persists the one-word Central Address Resolution value through Peer Data Storage.
All complete bodies, hashes, and direct caller sets are checked by:

```sh
python3 tools/evidence/summarize_r1_nordic_gatt_cache_closure.py
```

Provider family is `nordic_nrf5_sdk_17_1_0`; disposition is `use_nordic_sdk`. openR1 already
compiles both pinned SDK files. No Peer Manager or GATT-cache body is recreated locally.
