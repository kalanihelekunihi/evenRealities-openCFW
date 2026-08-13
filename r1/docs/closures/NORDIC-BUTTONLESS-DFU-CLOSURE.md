# Nordic unbonded buttonless-DFU closure

Ten recovered application functions are exact Nordic nRF5 SDK 17.1.0 buttonless Secure DFU
provider code. The build selects `NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS=0`; openR1 compiles the
pinned SDK sources and does not recreate these bodies.

| Recovered executable extent | Ledger bytes | Nordic symbol | SDK source | Direct callers |
| --- | ---: | --- | --- | --- |
| `0x00052018..<0x00052038` + `0x0007876C..<0x000787EE` | 162 | `ble_dfu_buttonless_async_svci_init` | `ble_dfu_unbonded.c` | `0x00075F8C` |
| `0x0005203C..<0x0005204A` | 14 | `ble_dfu_buttonless_backend_init` | `ble_dfu_unbonded.c` | `0x00052112` |
| `0x0005207C..<0x00052090` + `0x00052050..<0x00052078` | 60 | `ble_dfu_buttonless_bootloader_start_prepare` + tail-collapsed `ble_dfu_buttonless_bootloader_start_finalize` | `ble_dfu_unbonded.c` + `ble_dfu.c` | `0x00052182` |
| `0x00052094..<0x000520E4` | 80 | `ble_dfu_buttonless_char_add` | `ble_dfu_unbonded.c` | `0x00052140` |
| `0x000520E4..<0x00052146` | 98 | `ble_dfu_buttonless_init` | `ble_dfu.c` | `0x0004C934` |
| `0x00052154..<0x000521D4` | 128 | `ble_dfu_buttonless_on_ble_evt` | `ble_dfu.c` | SDK BLE observer registration; no direct branch |
| `0x000521D8..<0x0005226E` | 150 | `ble_dfu_buttonless_on_ctrl_pt_write` | `ble_dfu_unbonded.c` | `0x0007CE24` |
| `0x00052278..<0x000522D0` | 88 | `ble_dfu_buttonless_on_sys_evt` | `ble_dfu_unbonded.c` | SDK SoC observer registration; no direct branch |
| `0x000522D8..<0x00052326` | 78 | `ble_dfu_buttonless_resp_send` | `ble_dfu.c` | `0x000521F2`, `0x00052218`, `0x0005222E`, `0x000522A0`, `0x000522BE` |
| `0x0007CDC8..<0x0007CE2C` | 100 | `on_ctrlpt_write` | `ble_dfu.c` | `0x000521D0` |

The closure is 958 executable bytes. One newly resolved function / 100 bytes is removed from the
Ghidra unclassified frontier; the 162-byte asynchronous SVCI initializer was already source-routed
and is now additionally scatter/hash-pinned. Ghidra omitted the independent 128-byte BLE event handler at `0x00052154`,
so the ownership ledger records it as an exact manual provenance supplement. Ghidra also reports
the prepare wrapper as a 60-byte non-contiguous function: its 20-byte entry segment emits
`BLE_DFU_EVT_BOOTLOADER_ENTER_PREPARE` and tail-calls the adjacent 40-byte finalize body.

The recovered behavior fixes the provider variant and semantics:

- backend initialization rejects null and binds the single DFU service state pointer;
- asynchronous SVCI initialization temporarily selects the bootloader vector table, initializes
  the advertising-name service, and restores the application vector table over two executable
  segments;
- the characteristic uses UUID `0x0003`, indication plus deferred variable-length write, maximum
  length 23, and open read/write/CCCD permissions, identifying the unbonded variant;
- service initialization installs UUID `0xFE59`, the Nordic vendor base UUID, invalid connection
  handle, event handler fallback, backend, service, and characteristic in SDK order;
- BLE events track connect/disconnect, authorize only the DFU control-point write operations, and
  enter the bootloader after the expected HVC confirmation;
- the static authorization handler fetches the CCCD, requires indications, retries
  `sd_ble_gatts_rw_authorize_reply` on `NRF_ERROR_BUSY`, and forwards only successful writes;
- control-point opcode 1 enters DFU, opcode 2 validates and forwards a 1...20-byte advertising
  name through the asynchronous SVCI path, and unsupported/error cases return provider response
  codes and events;
- SoC events complete or reject the asynchronous advertising-name operation; and
- the three-byte indication response is `0x20`, opcode, response, with the provider's length check.

The executable-body SHA-256 values, in table order, are:

- `8d0e7bd5c4979c76ad9a2a6a995a60655868dfe568522ce96bedaa07d8d68892`;
- `d1ae97b0f886c52aacc5b46d70056ae09a51a56361f52a3effd920e6546f4c17`;
- `700b470a739cf8d1337ddfc5270e566e9fa570ad963fe6b512bdd8a179796f60`;
- `c7fdf9bc96ae4f458132e5ea6925c6ed2613801b9cd6fe6bc4424f439242fa67`;
- `b22f667515646b95e5ab245b2ae063b917a1f92901ec73dd73ee32192a4480e3`;
- `5ddc4b4f99fdbe120c05f468aa2c5ddc22f970672e6dc348f69f1dae310423f8`;
- `f9eb76118683e5907b1552865294dca624b334075b40307123e48da9bdc8fa08`;
- `52cf952308578630fb15285ae085bdf271b38a6ff46cccbd7a5705222c9e4cf7`; and
- `645ea03f11602b94f1a7e0934ce339a49a27e69b31bd859727710ba8b2abf48f`; and
- `cd658fe13c029d9a2379aaec192cc76ccb2e8e7dbc3684f02bb3df7e13bd4326`.

The image, ordered scatter segments, hashes, required callers, inventory distinction, and provider
variant are checked by:

```sh
python3 tools/evidence/summarize_r1_nordic_buttonless_dfu_closure.py
```
