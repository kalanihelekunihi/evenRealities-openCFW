# G2 eAT buzzer-command recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\eAT\at_buzzer.c` owns one exact-named handler and its pool in
`[0x005A4FD0,0x005A5488)`. `_atBuzzerTest` occupies
`[0x005A4FD0,0x005A53C6)` and contributes 1,014 code bytes with SHA-256
`b2a6c3ec39cd168200cc68667e3939d0bf4067ea862115c5108b653b07d38d28`.
The 194-byte alignment/literal region has SHA-256
`75323c9f7c225d63ae1dfb650d70f62e6791e42120c075a6e5280ca97236e8d6`.
The complete 1,208-byte object has SHA-256
`8ed84915f03b701c32e522528da58df5c52d7a60dd81f91504a78fef7a248aca`.

Two tiny bodies immediately before `0x005A4FD0` are deliberately excluded.
Their independent command-table records identify them as handlers for
`AT^CLEANBOND` and `AT^BLE_KEEPCONNECT`; their private pool ends at the buzzer
handler start. The next unrelated body begins at `0x005A5488`, closing the
buzzer object's other boundary.

The handler has no direct `BL` caller. Its sole ingress is the odd Thumb entry
pointer at `0x006C9288` in the sixteen-byte command record
`[0x006C9280,0x006C9290)`, whose fields are `{2, "AT^BUZZER",
0x005A4FD1, 0}`. The record's SHA-256 is
`dc6356d5f0069fbbe59b1e3e38d1bf65a76be62db80090eac5f1da2e0e8ec195`.
The body contains 76 direct provider/API calls. Exhaustive raw scans find no
other entry or interior pointer, and direct `BL`/`B.W` scans find no
strict-interior ingress.

## Command behavior

With no parameter string, the handler prints the retained four-command usage
text. Otherwise it splits the first comma-delimited token and recognizes these
subcommands:

- `note,<note>,<tone>,<beat>` requires note 0-7, tone 0-3, and beat 1-100,
  then calls `DRV_BuzzerPlayNote` at `0x00502BF8`.
- `play,<type>` accepts the documented type range 0-10 and calls
  `DRV_BuzzerPlay` at `0x00502BF0`. The separately closed driver later rejects
  queued predefined-voice indices 9 and 10 because its compiled table has nine
  records; the mismatch is preserved as stock behavior.
- `start,<freq>,<duty>` requires frequency 1-20,000 Hz and duty 0-100 percent,
  then calls `DRV_BuzzerStart` at `0x00502C88`.
- `stop` calls `DRV_BuzzerStop` at `0x00502D4C`.

Missing, malformed, out-of-range, and unknown inputs select distinct retained
diagnostics. Successful paths emit the corresponding status text and
`AT^BUZZER+OK`. The exact symbol `_atBuzzerTest`, command name, subcommands,
formats, limits, source path, driver call sites, complete physical bytes, and
ingress topology are all pinned by `tools/analyze_g2_at_buzzer.py`.

No authenticated historical source or license is available. There is no
clean-room candidate, the service is absent from `overlay.json`, and it claims
zero package ownership bytes.
