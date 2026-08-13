# Nordic BLE advertising module closure

Eight formerly unclassified application functions are exact Nordic nRF5 SDK 17.1.0
`components/ble/ble_advertising/ble_advertising.c` provider code. They are compiled from the pinned
SDK; openR1 does not recreate them.

| Recovered extent | Ghidra bytes | Complete extent | Nordic symbol | Direct callers |
| --- | ---: | ---: | --- | --- |
| `0x00051710..<0x00051716` | 6 | 6 | `ble_advertising_conn_cfg_tag_set` | `0x00048AB4` |
| `0x00051716..<0x000517FE` | 232 | 232 | `ble_advertising_init` | `0x00048AA4` |
| `0x000517FE..<0x00051806` | 8 | 8 | `ble_advertising_modes_config_set` | `0x000523AE` |
| `0x00051806..<0x00051870` | 106 | 106 | `ble_advertising_on_ble_evt` | observer registration; no direct branch |
| `0x00051870..<0x00051AA0` | 554 | 560 | `ble_advertising_start` | `0x0004C852`, `0x0004D12C`, `0x00051832`, `0x00053284` |
| `0x00064F1A..<0x00064F42` | 40 | 40 | `flags_set` | `0x00051A12`, `0x00051A52` |
| `0x0007F0C8..<0x0007F0DE` | 22 | 22 | `phy_is_valid` | `0x00051948`, `0x00051974` |
| `0x00094DD8..<0x00094DF0` | 24 | 24 | `use_whitelist` | `0x00051A04`, `0x00051A44` |

The recovered setup and event functions also match the SDK operation-by-operation:

- `ble_advertising_conn_cfg_tag_set` writes the caller's connection configuration tag at `+0x30`;
- `ble_advertising_init` rejects null pointers and the invalid high-duty-directed-plus-extended
  configuration, copies the 44-byte mode configuration, binds event/error handlers, initializes
  the invalid link/advertising handles and encoded-data buffers, encodes advertising and scan
  response data, installs a legal initial 1 Mbps fast-advertising parameter set through S140
  `sd_ble_gap_adv_set_configure`, and sets the initialized flag only on success;
- `ble_advertising_modes_config_set` copies the complete 44-byte mode configuration; and
- `ble_advertising_on_ble_evt` handles peripheral connection, disconnection, and advertising-set
  termination exactly as the SDK's inlined `on_connected`, `on_disconnected`, and `on_terminated`
  helpers, including restart/error-callback policy and modulo-five next-mode selection.

The recovered `ble_advertising_start` body matches the SDK operation-by-operation:

- reject an uninitialized advertising instance with `NRF_ERROR_INVALID_STATE`;
- clear the seven-byte peer address and request a peer address for directed modes;
- choose the next available directed, fast, slow, or idle mode;
- request a whitelist only for enabled fast/slow advertising while temporary disable is clear;
- clear and populate the 24-byte `ble_gap_adv_params_t`, including validated primary/secondary PHY;
- select directed-high-duty, directed, fast, slow, or idle parameters;
- update advertising flags through `ble_advdata_parse(..., BLE_GAP_AD_TYPE_FLAGS)`;
- invoke S140 `sd_ble_gap_adv_set_configure` (`SVC 0x72`) followed by
  `sd_ble_gap_adv_start` (`SVC 0x73`); and
- report the selected Nordic `ble_adv_evt_t` through the registered callback.

The structure offsets also agree with SDK `ble_advertising_t`: advertising parameters at `+0x3C`,
event callback at `+0x34`, advertising handle at `+0x54`, selected event at `+0x31`, encoded
advertising data at `+0x410`, and peer-address storage at `+0x426`.

Ghidra counts the main function as 554 bytes while its complete contiguous extent is 560 bytes.
The excluded six bytes at `0x000519A2..<0x000519A8` are the inline Thumb `TBB` mode jump table,
SHA-256 `ce1673f6fe175339d6d2959f905c3a5d81ac80f17056048bbd0f372114fe8bfd`.
The concatenated 554-byte instruction body hashes to
`6e76f1577ea6f6dcb1e42015e5d26835b78f9fa9efc8268c38bab8276a70e6e7`; the complete 560-byte
extent hashes to `f25cc50c7ea0c022fe253571d9e9a0eea8885c5ceb06bfaeb60d4bc027b76a2c`.

The seven non-start-function hashes are:

- `ble_advertising_conn_cfg_tag_set`:
  `fa3e2d00b9b20169cfe840228d491dd26092eb80dec02ab831785d0b4b4af13d`;
- `ble_advertising_init`:
  `6b9e719a23c0bc7a3b71b17fe7eceabd6ce098eece3e3d18be9c86d49c4eff08`;
- `ble_advertising_modes_config_set`:
  `20b25156b24161de89c9fd22c2032854b61e5ccac913c5a7ab1f2c8e8be07e9e`;
- `ble_advertising_on_ble_evt`:
  `12e46ab4b53d2b029fe4dcf9322583ed61354924652b09ba33a6f488ca2f967a`;

- `flags_set`: `b6dfd509fc9baa3b3fc82bfaf5755eb2827453428797a0b771a45da1c2a2ffcb`;
- `phy_is_valid`: `6b70e2128c7717798503ef943a89265235996ea6550cacb66c5dfcabbebb4676`;
- `use_whitelist`: `9e1e2214acc2b0a96161cc7371ede0e26d80202506715e37091664245dcaf8c3`.

The exact image, extents, Ghidra body, inline table, hashes, and caller sets are checked by:

```sh
python3 tools/summarize_r1_nordic_advertising_closure.py
```
