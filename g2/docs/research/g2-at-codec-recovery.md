# G2 eAT audio-control recovery

Status: complete linked-object census plus independently authored production C
and fail-closed routing. Run addresses use
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

No authenticated historical source or license is available. The clean-room
`at_codec.c` candidate implements only the recovered behavior and copies no
stock code. Its 44-byte Cortex-M55 leaf has three strict call relocations to
`AUDM_appAcquire`, `AUDM_appRelease`, and the retained AT output provider. A
guarded redirect replaces all 118 callable stock bytes while retaining the
34-byte authenticated alignment/literal pool. Host tests cover leading `1`,
leading `0`, other and null input, selector seven, acknowledgement, and the
return value.

The canonical overlay/component/package identities are 240,076 / 3,763,472 /
4,541,966 bytes with SHA-256 values
`2db11ff707bf253280eb07667c3d76954347cc9e31796c7589faf788fed629ae`,
`b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed`,
and `275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85`.
The 2,568,527-byte flash plan has 3,685 placed, two unresolved, five
container-only, and six protected regions; SHA-256 is
`bfdbc3b09c31f281cabb3b31b95f80523c7cfdd62edc83677f5f9adc50aac60f`.
No image was signed or flashed. Audible/codec power behavior is blocked by
unavailable authorized responsive G2 and live audio hardware evidence.
