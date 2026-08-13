# G2 eAT audio-control recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `platform\service\eAT\at_codec.c` owns one
exact-named handler and its pool in `[0x005A5488,0x005A5520)`.
`_atAudioCtrl` occupies `[0x005A5488,0x005A54FE)` and contributes 118 code
bytes with SHA-256
`628aa45af330f4c03626207810d875e9810f93929d14de2f83df360a26ec701a`.
The 34-byte alignment/literal region has SHA-256
`4f10eb7e21c7a624181dd3495b5622e5fb7ca67624108870925107e20a7e84f3`.
The complete 152-byte object has SHA-256
`73f108e6a639ee2be60360f24c80f3547aa9980e836c289da0464a6322c08b1b`.
The preceding object ends exactly at `0x005A5488`; the next unrelated body
begins at `0x005A5520`.

The handler has no direct `BL` caller. Its sole ingress is the odd Thumb entry
pointer at `0x006C9298` in command record `[0x006C9290,0x006C92A0)`, whose
fields are `{0, "AT^AUDIO", 0x005A5489, 0}`. The body contains ten direct
calls. Exhaustive raw scans find no other entry or interior pointer, and
direct `BL`/`B.W` scans find no strict-interior ingress.

## Command behavior

The handler logs the input parameter and compares only its leading byte. A
leading ASCII `1` invokes provider `0x0054F380` with selector seven; a leading
ASCII `0` invokes provider `0x0054F50E` with the same selector. Other leading
bytes invoke neither provider. Every path prints retained response
`AUD_AUDIO+OK\r\n` and returns one.

The exact symbol `_atAudioCtrl`, command record, `1`/`0` selectors, provider
sites and arguments, response, source path, complete physical bytes, and
ingress topology are pinned by `tools/analyze_g2_at_codec.py`.

No authenticated historical source or license is available. There is no
clean-room candidate, the service is absent from `overlay.json`, and it claims
zero package ownership bytes.
