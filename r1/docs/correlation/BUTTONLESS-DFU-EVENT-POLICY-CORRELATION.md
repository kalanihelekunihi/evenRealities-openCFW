# Buttonless-DFU event-policy correlation

## Decision

The independently registered callback at `0x0005232C..<0x00052498` is R1
product policy around Nordic's unbonded buttonless-DFU service. It is classified
`r1_product_specific` / `clean_room_behavior_only`; the Nordic DFU service,
advertising module, connection-state iterator, reset path, and bootloader handoff
retain their existing source/provider boundaries.

The local equivalent, `r1_runtime_plan_buttonless_dfu_event`, is a pure typed
plan. It never invokes BLE, disconnects a link, logs, resets, or enters the
bootloader.

## Exact identity and registration

| Recovered range | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x0005232C..<0x00052498` | 364 | `0e16e5502df7200684ef2bd4aa90bdca0aeb726f7938f8e4374d487273e39357` |

There are no direct branch callers. Initializer `0x0004C92C` loads the exact
Thumb pointer `0x0005232D` from literal address `0x0004C944` and passes it to
Nordic `ble_dfu_buttonless_init` at `0x000520E4`. Ghidra's main function CSV
omitted the independent body, so the byte-pinned range is a manual provenance
supplement.

## Event policy

| Nordic event | R1 plan |
| ---: | --- |
| `0` — prepare | disable advertising-on-disconnect, disconnect every connected link, and expose the returned link count for diagnostics |
| `1` — enter | diagnostic only |
| `2` — asynchronous enter failure | diagnostic only |
| `3` — response-send failure | diagnostic only |
| all others | unknown-event diagnostic only |

The event-0 body initializes the product advertising parameters at `0x000489E6`,
sets their first byte to one, calls Nordic
`ble_advertising_modes_config_set` at `0x000517FE`, and calls Nordic
`ble_conn_state_for_each_connected` at `0x00051E38`. Those provider effects are
represented only as booleans in the local plan; the clean C does not reproduce
the Nordic implementations or the registered per-link disconnect callback.

## Verification

```sh
python3 tools/evidence/summarize_r1_buttonless_dfu_event_policy.py
```

The evidence check pins the complete body, recovered-image hash, lack of direct
callers, callback literal, three event-0 call edges, and all five diagnostic
families. Host tests cover events 0 through 3 plus multiple unknown values.
