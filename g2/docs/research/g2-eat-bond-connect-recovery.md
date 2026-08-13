# G2 pathless eAT bond/connect command recovery

Status: complete two-handler census and fail-closed behavioral analysis;
historical source unavailable, no candidates, and not production-routed. Run
addresses use `run = file_offset + 0x00437FE0`.

## Result

Two handlers and their private pool occupy `[0x005A4FA4,0x005A4FD0)`, ending
exactly where retained `at_buzzer.c` begins. `AT^CLEANBOND` owns a sixteen-byte
body, while `AT^BLE_KEEPCONNECT` owns an eighteen-byte body. Their 34-byte
concatenation has SHA-256
`3e9408b876d80efd450be92dcd28f209c51fba952fef4d93431198bad37f66d4`.
The ten-byte alignment/pool tail has SHA-256
`b2a1b8bf327cbfd103f143d160bf78ce3b58c79a9eb8a24f4e5279a8dbb43cbc`;
the complete 44-byte object has SHA-256
`32c7ffcc3bff0ac19951e69f662ee02c93ede84871d98e026f65c0db3f72c5d6`.

Records `[0x006C9260,0x006C9280)` provide the only two entries. The clean-bond
handler calls provider `0x004B46CE`, emits `CLEANBOND+OK`, and returns zero.
The keep-connect handler calls provider `0x0046F2DC` with argument one, emits
`BLE_KEEPCONNECT+OK`, and returns zero. The pair has four direct provider calls
and no direct entry, stored strict-interior pointer, or direct `BL`/`B.W`
strict-interior target.

No retained source path or exact historical symbols survive. The manifest's
handler names are descriptive. Historical source partition, inventory,
source-only count, license, and whole-source identity therefore remain
unknown. No clean-room candidate exists, neither handler is in `overlay.json`,
and OpenCFW claims zero ownership bytes.
