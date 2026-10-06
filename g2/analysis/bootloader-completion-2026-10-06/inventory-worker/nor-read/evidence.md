# NOR read wrapper recovery

Scope is only the stock provider at `0x00420F70` (Thumb), from the locked
`ota_s200_bootloader.bin`, plus a compiled source candidate and a synthetic
provider-boundary comparison. It does not implement MSPI setup, HAL transfer,
or physical NOR access.

## Identity and disassembly provenance

- Artifact: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, 148,599 bytes, SHA-256
  `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
- Link base `0x00410000`; function runtime interval `[0x00420F70,0x00420FF2)`;
  file interval `[0x10F70,0x10FF2)`, 130 bytes.
- Function-body SHA-256: `ce201805b566c9d5c4a70d675e0bdb145133d2771bc9098e4255245a8d6067e3`.
- Reproduction command:
  `arm-none-eabi-objdump -D -b binary -marm -Mforce-thumb --adjust-vma=0x00410000 --start-address=0x00420f70 --stop-address=0x00420ff2 g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`.
- `0x00421010` is a literal containing `0x200270dc`, the address of the RAM
  slot holding the active MSPI handle. `0x004210C4` contains `0x000f4240`
  (1,000,000). Literal bytes were checked at image offsets `0x11010` and
  `0x110C4` respectively.
- Disassembly stores the status from `am_hal_mspi_blocking_transfer` and
  returns it after `0x0041FF1E`; no status translation is present.

## Recovered contract

The AAPCS inputs are `(uint32_t device_address, void *destination,
uint32_t length, uint32_t reserved)`. The fourth argument is saved but unused.
The wrapper loads the active handle via RAM slot `0x200270dc`; if the handle,
destination, or length is zero it returns `6` without setup calls. If the
starting device address is at least `0x02000000`, it returns `5` without setup
calls. The AmbiqSuite 5.1.0 `am_hal_status_e` declaration orders these as
`AM_HAL_STATUS_INVALID_ARG == 6` and `AM_HAL_STATUS_OUT_OF_RANGE == 5`.

On accepted inputs it calls `0x0041FF08`, `0x00420E8C`, and `0x004207F4`,
then submits one PIO command to `0x004262E0`, and finally calls `0x0041FF1E`.
The command is exactly 24 bytes:

| Offset | Value | Meaning |
|---:|---|---|
| 0 | `length` | transfer byte count |
| 4 | 0 | scrambling disabled |
| 5 | 0 | DCX disabled |
| 6 | 0 | RX direction |
| 7 | 1 | send device address |
| 8 | `device_address` | 32-bit NOR address |
| 12 | 1 | send instruction |
| 14 | `0x006c` | QREAD4B instruction |
| 16 | 1 | turnaround enabled |
| 17 | 0 | write latency disabled |
| 18 | 0 | continuation disabled |
| 19 | 0 | zero from the stock 24-byte clear |
| 20 | `destination` | RX buffer pointer |

The transfer timeout is `1,000,000` microseconds, as documented by the
matching Apollo510 HAL prototype. The public header's PIO structure agrees
with these offsets when compiled for the target's short-enum ABI; repository
toolchain reference records that ABI. This candidate independently spells
the minimal field layout and asserts size/offsets rather than importing the
SDK implementation.

There is no explicit pointer-alignment, end-address, overflow, or maximum
length check in this wrapper. The address predicate checks only the start.
Thus a start of `0x01ffffff` is accepted, and a request beginning below 32 MiB
may cross its end. The wrapper does no chunking and submits the full length in
one PIO call. A normal littlefs read callback computes
`0x01400000 + block*0x1000 + offset` and passes the requested size through;
its callback maps low-level success to 0 and any nonzero status to LFS I/O
error `-5` (`decomp/004212d8.c`, stock address `0x004212D8`).

## Candidate and validation

- `nor_read.c` is readable C for the wrapper only. The exact local setup,
  configure, delay, teardown, and blocking-transfer addresses are linker
  aliases. Their behavior is intentionally not reconstructed here.
- Build: `make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read OUT=/tmp/nor-read`.
- Compare:
  `/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read/verify_nor_read.py --elf /tmp/nor-read/nor_read.elf --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read/nor-read-comparison.json`.
- Result: **PASS**, 10 original-vs-source Unicorn cases, 174 distinct stock
  instruction bytes executed. Fixtures covered normal and 4096-byte reads,
  high-bit transfer status propagation, start at `0x01ffffff`, a request
  crossing 32 MiB, invalid/zero arguments, and null handle. Each valid case
  compared exact 24-byte command bytes, provider order, handle, and timeout.
- Provider stubs only record calls / return selected values. No physical
  device, flash access, kernel, nor lower MSPI implementation ran.

No external blocker is identified for this bounded wrapper candidate. The
remaining unknowns are the semantics of the four adjacent local helpers, the
HAL transfer implementation/configuration, transfer-size constraints below
the wrapper, and actual flash/device behavior.
