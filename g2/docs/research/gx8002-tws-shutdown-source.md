# GX8002 TWS shutdown and buffer wrapper

Two lifecycle wrappers are reconstructed from NationalChip
`lvp/lvp_mode_tws.c` at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. The builder authenticates the
source and headers. It compiles the actual mode and queue types plus exact
shutdown/buffer function declaration excerpts with native macOS C-SKY GCC.

The buffer-init wrapper at `0x10208644` (package `0x11bd0`) is eight bytes;
it returns `LvpInitBuffer()` unchanged. The shutdown wrapper at `0x1020864c`
(package `0x11bd8`) is 36 bytes. It clears the 20-byte queue at `0x2002e6ec`,
calls `LvpKwsDone`, calls `LvpAudioInDone`, then prints its exit message.
It ignores the next-mode argument and helper return values, as upstream does.
Both preserve their four-byte frames and compile exactly to the stock bytes.
The C exit string at `0x1020b218` supplies 24 exact bytes.

A decoded-code interpreter checks each implementation against an independent
call-order and return-value oracle. The 3,108 cases vary register seeds and
helper results, including high-bit and negative integer encodings. Caller-saved
registers are clobbered across each helper call. Seven regression tests check
clear extent/address, call order, buffer helper/return, and stack restoration.

This qualifies the wrappers' call contracts; it does not qualify the bodies
of the retained recognition/audio shutdown or buffer initialization helpers.
Memset and printf have independent source qualification. No hardware run or
whole-TWS completion is claimed. These wrappers and their string are now registered in the integrated codec
builder; all 349 integration tests pass.

Reproduce:

```sh
python3 g2/tools/verify_gx8002_tws_shutdown.py
python3 -m unittest discover -s g2/tests -p test_gx8002_tws_shutdown.py
```

Evidence: [gx8002-tws-shutdown-verification.json](gx8002-tws-shutdown-verification.json).
