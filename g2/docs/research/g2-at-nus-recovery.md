# G2 pathless `AT^NUS` command recovery

Status: complete linked-handler census and fail-closed behavioral analysis;
historical source unavailable, no source candidate, and not
production-routed. Run addresses use `run = file_offset + 0x00437FE0`.

## Result

The standalone handler body `[0x005A5520,0x005A552C)` is twelve bytes with
SHA-256
`6e4a3e381abcbd8e2cc20d13cf39e575c0165b96e20b8ec1b7a8da780ff1548a`.
Its four-byte literal pool `[0x005A552C,0x005A5530)` points to the retained
response and has SHA-256
`2567cbc76b274edabf68bf27abbc7935b2877b2e743e89d5ca54da297b43693d`.
The complete sixteen-byte object has SHA-256
`e7839a2d6e1af4863ff17f7010a3fc079e44f5565526b612458904f5c539ace8`.
The preceding retained `at_codec.c` object ends exactly at `0x005A5520`; the
retained `at_fs.c` object begins exactly at `0x005A5530`.

The record `[0x006C92A0,0x006C92B0)` registers `AT^NUS` with odd Thumb
pointer `0x005A5521`. That is the only stored ingress. There is no direct entry
or strict-interior branch/pointer, including `B.W`. The handler passes
`NUS+OK\r\n` to output provider `0x00541430` and returns one; it does not read
its arguments or perform additional validation.

No retained source path or exact historical symbol survives. The manifest's
`atNusHandler` name is descriptive, not a recovered source symbol. Historical
source inventory, source-only function count, license, and whole-source
identity therefore remain unknown. No clean-room candidate exists, the
handler is absent from `overlay.json`, and it claims zero package ownership
bytes.
