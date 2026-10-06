# NOR initializer source slice

The source candidate implements the startup NOR orchestrator at `0x00420476`
and its immediate JEDEC-read helper at `0x0042059e`. It reuses the previously
recovered status-transfer source for `0x004205f4` from
`../nor-read-status/nor_read_status.c`. The required link symbol is
`opencfw_provider_420476`.

## Reference and provenance

- Locked blob: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`
- SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`
- Raw load address: `0x00410000`; file offset is address minus `0x00410000`.
- `0x420476` range: `[0x420476,0x42052a)`, 180 bytes,
  SHA-256 `5be1a86e4e5b4c50b9d8eac9043747caec7abd1ad916fc13ceace39fa5ddb662`.
- `0x42059e` range: `[0x42059e,0x4205f4)`, 86 bytes,
  SHA-256 `76375cc441140c585f955d99008ebaf467fb7eb54882cc857cff55b7aaa0f48e`.
- The comparison receipt binds its generated ELF, source files, and original
  instruction trace: `nor-init-comparison.json`.

## Recovered behavior

`0x420476` calls the MSPI-device initializer with `(1, 0, 0x200270d8)`. On
failure it logs level 1 at line `0x284`, powers the flash MSPI via
`0x41fe28`, and returns the status. On success it calls delay argument `10`,
reset-enable/reset commands (`0x42052a`), XIP/read setup (`0x420f10`), flash
status-register read (`0x4201ba`), XIP/read setup again, then reads three JEDEC
bytes through `0x42059e` → `0x4205f4`.

The JEDEC helper issues instruction `0x9f`, address `0`, `send_address=0`, and
length `3`. It byte-swaps the received three-byte word to a `0x123456`-style
numeric ID. A failed transfer logs `command_read ERROR` from
`DRV_Mx25u25643g_read_id` at line `0x2d8`; the caller then logs the ID failure
at line `0x28e`. A successful read logs the numeric ID at line `0x292`, then
calls flash XIP setup `0x420890`, flash XIP mode `0x420c5c(1)`, and runtime
flag-group creation `0x41fe62`. Both ID outcomes finally call `0x41fe28` and
return the JEDEC-helper status.

The delay routine receives exactly the raw argument `10`; this evidence does
not assign a physical time unit. The C source owns its log strings, so its
pointer addresses differ from the original; the comparison checks string
contents, log levels, line numbers, formatting arguments, call order, and
return statuses.

## Validation and boundaries

`make -C g2/components/bootloader/nor_init verify
PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python` builds the ARM
Cortex-M4 source profile and runs original-vs-source execution. The saved
comparison covers six combinations: initializer status `0`, `1`, `7`, and
`0xffffffff`; transfer status `0`, `5`, and `0xffffffff`. All six pass,
matching final status and provider/log events. The fixture executes all
original bytes in the `0x420476` and `0x42059e` bodies and executes the
reachable instruction paths through `0x4205f4`; the receipt reports 414
distinct original instruction bytes.

Synthetic boundaries remain at the high-level MSPI initializer `0x420254`,
delay `0x41f9d8`, command/reset helper `0x42052a`, read-mode setup `0x420f10`,
status-register read `0x4201ba`, XIP configuration `0x420890`, mode command
`0x420c5c`, runtime flag creation `0x41fe62`, power control `0x41fe28`, logger
`0x4176ce`, and lower blocking transfer `0x4262e0`. Original helper
`0x415ff4` is represented by zeroing the synthetic stack buffer. These tests
do not reconstruct those providers, prove physical flash identification or
clock behavior, or claim hardware boot and byte-identical image completion.

The component reuses the status source in the analysis evidence tree through
its Makefile include/source path; production integration should promote that
shared source to the component tree once the parent integration layout is
selected, instead of forking a second implementation.
