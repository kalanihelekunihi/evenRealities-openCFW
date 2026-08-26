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
`2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`,
`7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`,
and `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`.
The 2,568,527-byte flash plan has 3,685 placed, two unresolved, five
container-only, and six protected regions; SHA-256 is
`80d2f655555786d495d9df72b85013dee8e0076554b0d2deb82159a5c876e292`.
No image was signed or flashed. Audible/codec power behavior is blocked by
unavailable authorized responsive G2 and live audio hardware evidence.
