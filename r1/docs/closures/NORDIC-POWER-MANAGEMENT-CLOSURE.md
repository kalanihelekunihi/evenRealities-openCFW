# Nordic power-management shutdown closure

Two formerly unclassified application functions / 332 bytes are exact Nordic nRF5 SDK 17.1.0
`components/libraries/pwr_mgmt/nrf_pwr_mgmt.c` provider code. openR1 compiles the pinned Nordic
translation unit and does not recreate either body.

| Recovered extent | Bytes | Nordic symbol | Direct callers | SHA-256 |
| --- | ---: | --- | --- | --- |
| `0x00079D50..<0x00079DA8` | 88 | `nrf_pwr_mgmt_shutdown` | `0x00052070`, `0x000567B8` | `c6e216bd9dac1ac011389a3d30b918072e3f66c599095e1f57350bd3dc356772` |
| `0x0008F234..<0x0008F328` | 244 | `shutdown_process` | `0x00079DA2` | `5e2fb1680fe1e62efad43cc8374fb60605b392a677f4f1683cb09f1a15852725` |

The recovered `nrf_pwr_mgmt_shutdown` matches the SDK operation-by-operation:

- acquire the Nordic atomic System-OFF mutex and return when it is already held;
- treat shutdown type 4 as `NRF_PWR_MGMT_SHUTDOWN_CONTINUE`;
- reject a second non-continue request, otherwise store the shutdown event and started flag;
- retain the provider assertion/log path;
- call `shutdown_process` directly, establishing `NRF_PWR_MGMT_CONFIG_USE_SCHEDULER=0`; and
- release the mutex on every returning path.

The static `shutdown_process` iterates the SDK shutdown-handler linker section exactly once per
call, returns when any handler reports not ready, flushes Nordic logging, resets for event 2
(`PREPARE_DFU`) or 3 (`PREPARE_RESET`), and otherwise checks whether the SoftDevice is enabled
before invoking System OFF. The terminal hardware path preserves the SDK barriers and WFE loop.
That flow establishes `SOFTDEVICE_PRESENT` and retains Nordic's shutdown ordering; it is not an
R1-owned power-policy implementation.

The exact image, body extents, hashes, caller sets, provider configuration, and non-local ownership
are checked by:

```sh
python3 scripts/firmware/summarize_r1_nordic_power_management_closure.py
```
