# GX8002 recognition and audio shutdown

The two helpers derive from authenticated NationalChip `lvp/common/snpu_engine/lvp_kws.c`
and `lvp/common/lvp_audio_in.c` at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. The native macOS C-SKY builder
uses the upstream GRUS callback type and exact audio-exit declaration.

`LvpKwsDone` at runtime `0x10206dac` (package `0x10338`) calls
`gx_snpu_exit`, clears the callback slot `0x20027b50`, then returns zero.
Its 20 compiled bytes match stock. The callback has a four-byte typed C BSS
definition; it is NOBITS and contributes no firmware payload bytes.
`LvpAudioInDone` at `0x102073f8` (package `0x10984`) calls
`gx_audio_in_exit`, then returns zero. It uses 10 of the original 12 bytes.
Both have four-byte frames, ignoring driver failures as the upstream and
stock implementations do.

Decoded source and stock code match an independent oracle in 3,108 cases,
varying initial registers/callback contents and driver return values.
The model clobbers caller-saved registers and allows a driver to change the
callback, testing that recognition clears it after the driver call.
Eight regression tests cover wrong slot, order, driver, return and frame.
This is a helper-call boundary model, not proof of asynchronous timing or
of either driver's hardware behavior. The drivers remain retained.

These helpers are registered in the integrated codec build; all 357 tests
pass. The package and Makefile include `NATIONALCHIP-STREAM-NOTICE.txt`
as the eleventh notice.

```sh
python3 g2/tools/verify_gx8002_stream_shutdown.py
python3 -m unittest discover -s g2/tests -p test_gx8002_stream_shutdown.py
```

Evidence: [gx8002-stream-shutdown-verification.json](gx8002-stream-shutdown-verification.json).

Next driver observations (not yet qualified):

- `gx_snpu_exit` at `0x10205d40` / package `0xf2cc`, 32 bytes, frame 8:
  helper at `(0xffe2ea88 + 0x101f6a74) & 0xffffffff` with argument 12,
  helper at package `0xf01c`, save return, helper at adjusted `0xffe2ea90`
  with argument 12, then helper at package `0xeb38` only if saved return is
  zero. Return that saved value. Identify helper symbols before implementing.
- `gx_audio_in_exit` at `0x10204984` / package `0xdf10`, 44-byte envelope,
  frame 4: helper at package `0xd214`, then gate calls at adjusted `0xffe2e60c`
  with `(3,0)`, `(2,0)`, `(8,0)`, `(7,0)`, return zero. Gate target resolves
  to the previously identified clock gate `0x10025080`.
- Pinned upstream supplies these drivers as `drivers_lib/snpu/grus/snpu.o`
  and `drivers_lib/audio_in/v2.0/audio_in.o`. Use them only as symbol/code
  comparison oracles, not firmware payload. Find source upstream if available;
  otherwise reconstruct reviewed C from observed behavior.

Authenticated object relocation evidence now identifies the SNPU exit helpers
as `gx_mask_irq(12)`, `suspend()`, `gx_unmask_irq(12)`, and
`snpu_device_exit()` on suspend success. The audio helper at package `0xd214`
is `_ain_reset`. See `gx8002-driver-exit-identification.json` and the two
`build/gx8002-board/*-exit-oracle.disassembly.txt` artifacts. No driver payload
is admitted by this identification.
