# Nordic BLE static-helper closure

Five exact Nordic SDK functions / 158 Ghidra-counted executable bytes are source-routed. Their
complete recovered extents occupy 164 bytes because `set_security_req` ends with a six-byte inline
Thumb jump table that Ghidra excludes from the function size.

| Extent | Ledger bytes | Symbol | Source |
|---|---:|---|---|
| `0x00074F20..<0x00074F38` | 24 | `link_init` | `components/ble/nrf_ble_gatt/nrf_ble_gatt.c` |
| `0x00087A94..<0x00087AA8` | 20 | `ram_end_address_get` | `components/softdevice/common/nrf_sdh_ble.c` |
| `0x00087AAC..<0x00087AC8` | 28 | `rank_highest` | `components/ble/peer_manager/peer_manager_handler.c` |
| `0x00087AC8..<0x00087AF4` | 44 | `rank_vars_update` | `components/ble/peer_manager/peer_manager.c` |
| `0x0008EE0A..<0x0008EE3A` | 42 | `set_security_req` | `components/ble/common/ble_srv_common.c` |

`link_init` writes the recovered 247-byte desired MTU, 23-byte effective MTU, cleared exchange
flags, 251-byte desired data length, and 27-byte effective data length for each GATT link. The RAM
helper computes `0x20000000 + NRF_FICR->INFO.RAM * 1024` and is called only by Nordic's
already-routed `nrf_sdh_ble_enable` diagnostics. `rank_highest` creates the zero-initialized
`PM_EVT_BONDED_PEER_CONNECTED` event and delegates to `pm_handler_flash_clean`.
`rank_vars_update` calls `pm_peer_ranks_get`, maps `NRF_ERROR_NOT_FOUND` to invalid-peer/rank-zero,
and sets the initialized flag only for success or not-found. `set_security_req` maps all six
`security_req_t` values to the exact encoded GAP mode/level bytes used by `characteristic_add`.

The complete extents, SHA-256 hashes, and direct caller sets are checked by:

```sh
python3 tools/summarize_r1_nordic_ble_static_helpers.py
```

Provider family is `nordic_nrf5_sdk_17_1_0`; disposition is `use_nordic_sdk`. openR1 compiles the
pinned provider files. No BLE common, SoftDevice handler, or Peer Manager body is recreated locally.
