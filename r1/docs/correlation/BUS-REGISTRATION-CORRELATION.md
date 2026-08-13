# Two-wire bus registration correlation

This closure separates six R1-owned fixed bus-binding wrappers from the unidentified stock generic
device registry. It admits only recovered board configuration and CMSIS semaphore setup. OpenR1
uses direct typed Nordic/vendor bindings instead of cloning the global name-list registry, and it
does not admit a GPIO-driven software-I2C engine.

## Exact recovered wrappers

| Stock extent | Bytes | SHA-256 | Fixed binding |
|---|---:|---|---|
| `0x00054F90..<0x00054FBC` | 44 | `0e1b2dbfdc68ac597dc2f5cacc0e26a9b14466bb5afe1ce353fd89ce5766a7cc` | hardware `i2c_0` / TWIM0 |
| `0x00054FC4..<0x00054FF0` | 44 | `2a087f558d9bc124cf2ad77e0621ee2776ef8f87aee88270a35262dcf561d83b` | hardware `i2c_1` / TWIM1 |
| `0x00056508..<0x0005651A` | 18 | `c7d415efc98ffaf074711600bdeaf04a11fec5528111b893e69c4797c499a826` | software `i2c_2` |
| `0x00056520..<0x00056532` | 18 | `9e60cf6d29f5b93e12a23a50db834e92e71f77e55edadceb72f66bdb5a43d302` | dormant software `i2c_3` |
| `0x00056538..<0x0005654A` | 18 | `0452b13b80732815593970ee5f5fbfd4e9ecf3f4c0e4e56f0496def65a6d0481` | software `i2c_4` |
| `0x00056550..<0x00056562` | 18 | `c6003bad98c688df45118e27e1ef5b17b9f4552c584701d9e05b9aae86957979` | software `i2c_5` |

These entry points were missed by Ghidra's function inventory. Their boundaries are independently
established by complete Thumb return or tail-call boundaries and are included as exact manual
provenance supplements.

## Recovered behavior and memory

The hardware wrappers operate on fixed records at `0x20006FF4` (`i2c_0`) and `0x20007060`
(`i2c_1`). Each copies its leading instance word into the embedded registry record at offset
`0x24`, points that record at its operation table at offset `0x3C`, and submits the embedded record
to stock `device_registry_register` at `0x00085D58`. Each then calls authenticated CMSIS-FreeRTOS
`osSemaphoreNew(1, 0, NULL)` at `0x0007D60C`, stores the handle in the corresponding transfer-state
object, and enables semaphore synchronization only when creation succeeds. The primary transfer
state begins at `0x20006FE8`; the secondary begins at `0x20007054`.

The four software wrappers use fixed records at `0x20007400`, `0x20007470`, `0x200074E0`, and
`0x20007550`. Each copies its leading instance word into the embedded record at offset `0x34`,
points that record at the operation table at offset `0x4C`, and tail-calls the same stock registry.
They create no semaphore. Their recovered pins, consumers, and operation entry points remain
machine-readable through `tools/evidence/summarize_r1_bus_registry.py`.

## Ownership and replacement boundary

The six wrappers are classified as `r1_device_registry_configuration_adapter` with disposition
`clean_room_configuration_only_direct_typed_binding`. That classification does not change the
nine-function registry boundary: `device_registry_register`, name lookup, and seven generic
operation dispatchers remain unidentified and implementation-blocked.

OpenR1's functional replacement is deliberately simpler:

- Nordic SDK `nrf_drv_twi`/`nrfx_twim` and authenticated CMSIS-FreeRTOS own hardware transfer and
  synchronization mechanisms;
- admitted sensor/NFC providers receive direct typed transport bindings;
- R1 code owns only fixed pins, instance selection, per-bus lifecycle policy, and narrow adapters;
- software `i2c_2`, `i2c_4`, and `i2c_5` remain disabled until an attributable/licensed transport
  provider and owned-hardware validation are available; dormant `i2c_3` remains unassigned.

No signing, rollback, protection, diagnostic, or deployment bypass is part of this closure.
