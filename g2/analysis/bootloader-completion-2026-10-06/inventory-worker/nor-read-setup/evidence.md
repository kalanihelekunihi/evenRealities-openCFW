# NOR-read setup, teardown, and ready-wait helpers

This owned source slice recovers the four helpers called by `0x00420F70` and
the directly linked local configuration/poll loops. Hardware-facing HAL,
delay, activity, copy, logging, runtime-notify and device-state routines remain
explicit provider edges. The fixtures intercept those edges; no device or
flash is touched.

## Locked image and byte evidence

- Artifact: `ota_s200_bootloader.bin`, SHA-256
  `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, base
  `0x00410000`.
- Main entry bodies (runtime range, size, SHA-256):
  - `0x0041FF08–0x0041FF1E`, 22 B,
    `02963ef679faf897f9108a5e1526bd79eccabb28b11192d6325dfb4165ca0dc5`.
  - `0x0041FF1E–0x0041FF34`, 22 B,
    `ecb3a585f0f910e6428aa9a722ff0f2a621ca1d195b8fd8b4a9d4f2820f0dddd`.
  - `0x00420E8C–0x00420F0C`, 128 B,
    `d3eeee3b649bcab6d485d604bb94fe739a753064b80b6918a4d5a9db616b86ef`.
  - `0x004207F4–0x00420800`, 12 B,
    `bceeab3a47379a62e78b6b07417c52a86da437468ee68ddb43e56468065e7329`.
- Source-command disassemblies are saved alongside this report. File offset is
  runtime address minus `0x00410000`.

## Recovered behavior

`0x0041FF08` runs an activity check using the 32-bit word at `0x200270E0`; if
nonzero it invokes `0x004166AA(context, 0xFFFFFFFF)` and, on nonzero result,
emits the stock info log (line `0xC3`). It then reads byte `0x200271C5`; if it
is not `1`, it calls `0x00426808(*0x200270DC, 0, 1)` and writes byte `0` to
`0x200271C6`, regardless of the HAL return. `0x0041FF1E` performs the inverse
conditional: if byte `0x200271C5` is not `1`, it calls
`0x00426808(*0x200270DC, 2, 1)` and writes byte `1` to `0x200271C6`; it then
checks `0x00416710(context)` and emits stock info log line `0xCC` on nonzero.
The exact EasyLogger tag/file/function/format pointers and line arguments are
passed in the source candidate.

`0x00420E8C` copies exactly 24 bytes from the RAM object at `0x20000224` to a
local config, then writes `config[0]=8`, halfword `config[4]=0x006C`,
`config[8]=16`, and `config[15]=1`. Its local configure helper at `0x00420E08`
performs `am_hal_mspi_disable(handle)`, `am_hal_mspi_device_configure(handle,
config)`, then `am_hal_mspi_enable(handle)`, stopping and returning `1` at the
first nonzero status. Each failure logs its distinct stock line `0x58A`,
`0x592`, or `0x59A`. On success it calls `0x0041FADC` with the device object
loaded through slot `0x200270D8` and `config[8]`, and returns `0`. The outer
helper logs line `0x5AE` if configuration failed. On success it changes byte
`0x20000241` to `8`, calls MSPI control request `0x10`, then calls request
`0x18` with a one-byte value `16`; nonzero final control status logs line
`0x5B5`. The helper itself is `void` and discards both control statuses.

`0x004207F4` calls `0x004207A2(500)`. That local retry loop calls poll helper
`0x0042074E` up to 200 times; after each busy result it passes `5` to
`0x0041D1C0`. If still busy, it then performs up to the caller-supplied retry
count. Each secondary iteration asks `0x00416088` for runtime state: state `2`
calls `0x00416378(1)`, all other states pass `1000` to `0x0041D1C0`. It then
polls again; ready ends the loop with zero, exhaustion returns one.

Poll helper `0x0042074E` zeroes a five-byte local result buffer and calls
`0x004205F4(5, 0, 0, buffer, 1)`. A nonzero provider status logs line `0x376`
and is returned. Otherwise it returns the result byte's bit 0. The caller
treats any nonzero result—including a provider error—as busy.

The name `delay_us` is present in the symbol catalogue for `0x0041D1C0`, but
the slice does not assert units. Raw instructions convert the incoming
unsigned argument to Q5, consult clock-selection bits, apply a `250.0/96.0`
float factor in one branch, subtract branch-specific overhead (`24` or `15`),
then call ROM seam `0x00000040` with a cycle count. No tick or wall-clock
measurement was available here to establish the input unit independently.

## Linked provider ABI and validation

`nor_read_setup.c` declares the exact register-level argument roles used at
these callsites. HAL operation addresses are the bootloader entries already
being recovered by the parent work: power control `0x426808`, disable
`0x4250F0`, device configure `0x424BE4`, enable `0x425066`, and control
`0x4251C0`. Other explicit local providers are copy `0x4156AC`, activity
predicate `0x4166AA`, pending predicate `0x416710`, logger `0x4176CE`, delay
`0x41D1C0`, runtime mode `0x418B56`, notify `0x416378`, status transfer
`0x4205F4`, and device-state publisher `0x41FADC`.

Build and run:

```sh
make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup OUT=/tmp/nor-read-setup
/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup/verify_nor_read_setup.py --elf /tmp/nor-read-setup/nor_read_setup.elf --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup/nor-read-setup-comparison.json
```

Result: **PASS**, 17 original/source cases and 784 distinct stock instruction
bytes executed. Coverage includes activity / pending logging predicates,
power-state branches, each disable/configure/enable failure, successful device
configuration and both control requests, poll error, ready/busy transitions,
the 200-poll secondary-loop transition, runtime notify, and both delay values.
The fixture's external calls are deterministic synthetic stubs. The report
does not claim physical power sequencing, accurate elapsed time, HAL hardware
effects, scheduler interaction, or real NOR readiness.

## Linked status-transfer variant

`make linked-status` builds a second test ELF from this setup source plus
`inventory-worker/nor-read-status/nor_read_status.c`. Its linker routes the
setup poll ABI to the compiled status-transfer function. The stock profile
above remains unchanged. In the linked comparison, stock executes both
`0x0042074E` and `0x004205F4`; the candidate executes compiled setup/poll code
and the compiled command builder. Both reach only injected lower transfer
`0x004262E0` and status-error helper `0x00415FAE`.

Build/run:

```sh
make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup linked-status OUT=/tmp/nor-read-setup
/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup/verify_nor_read_setup_linked.py --elf /tmp/nor-read-setup/nor_read_setup_status.elf --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup/nor-read-setup-linked-status-comparison.json
```

Result: **PASS**, 7 cases and 644 distinct stock instruction bytes. Tests
compare ready, busy-then-ready and transfer-error-then-ready poll sequences,
including exact one-byte command construction and status-error arguments. A
direct wrapper test confirms a length of 3 arrives through the fifth stack
argument and appears in the PIO command; a direct error case verifies
low-16-bit instruction logging. Successful and failing configure paths are
also covered through the linked image. Only lower MSPI transfer and error helper behavior is
synthetic. In the combined link, the status-source object is compiled with
the M4 Thumb subset for Unicorn's instruction support; the setup object uses
the M55 target. This is a semantic test, not final code-generation evidence.
