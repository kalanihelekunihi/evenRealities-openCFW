# G2 eAT buzzer-command recovery

Status: software-complete clean-room production implementation; physical buzzer
validation blocked by unavailable authorized hardware. Run addresses use
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

No authenticated historical source or license is available.

## Production closure

`components/apollo_main/core_overlay/at_buzzer.c` is an independently authored
GPL-3.0-only implementation of the recovered command behavior. It uses retained
command and response strings, a bounded local parser, and five explicit ABI
bindings: AT output at `0x00541430` plus the four buzzer-driver entries above.
It preserves the stock four-byte prefix comparisons (including the accepted
`note-extra` quirk), `atoi`-style nondigit-to-zero behavior for `play`, the
0-10 AT range despite the driver's nine-record voice table, and the distinct
null/malformed/range/unknown response paths. The bounded subcommand buffer
prevents an unterminated unknown token from escaping the handler.

Apple Clang 21.0.0 emits one 2,740-byte Thumb leaf with SHA-256
`a3eeb877b669e96b2f0122ebdd399a5795a6f0a7bd7d3fd938f03375c5cd0305`.
Its 23 strict `R_ARM_THM_CALL` relocations reference only the five reviewed
providers; no source literal/rodata section is admitted. A guarded `B.W`
replacement covers all 1,208 stock bytes, including the pool, while the stored
command-table pointer continues to enter the authenticated stock address.
The source and replacement claim 3,948 production ownership bytes.

Host tests exercise every successful dispatch, null/missing/malformed and
range failures, prefix and `atoi` quirks, bounded unknown echo, provider
arguments, and the single-function Thumb surface. The analyzer additionally
pins source, relocation, patch, build, manifest, and package identities. The
canonical Apple overlay/component/package sizes are 188,812 / 3,712,208 /
4,490,702 bytes with SHA-256
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.

No device was accessed or flashed. Audible output, pitch/frequency, duty cycle,
beat timing, predefined voice playback, and stop behavior require an authorized
physical G2 buzzer/piezo path. That evidence is unavailable, so hardware
validation is explicitly blocked and functional completeness is not declared.
