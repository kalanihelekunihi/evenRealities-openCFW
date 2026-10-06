# MSPI status-transfer wrapper recovery

This slice recovers the shared status/command PIO wrapper at stock address
`0x004205F4`, which is called by NOR status polling including
`0x0042074E`. The 24-byte PIO transfer layout is locally reconstructed from
the instructions. The actual MSPI transfer and error-event provider remain
explicit synthetic boundaries in the comparison fixture.

## Image identity and exact range

- Locked image: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`,
  SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
- Base address `0x00410000`; function range
  `[0x004205F4, 0x0042069E)` (170 bytes), file range
  `[0x105F4, 0x1069E)`.
- Body SHA-256:
  `7fe24d8d1ac2fda0dcce1f4e7d4364b2bbe3df283c05000ab32d357de04a6749`.
- Raw disassembly is preserved in `original-disassembly.txt`.
- Literal at `0x00420874` contains `0x200270DC`, the active-handle slot.
  Literal at `0x00420F0C` contains `0x000F4240` (1,000,000). The matching
  Apollo510 HAL prototype documents `ui32Timeout` in microseconds.
  Literal at `0x00420FF4` contains `0x00431420`, passed as the error module.

## Contract and command layout

The recovered five-word AAPCS ABI is
`(uint32_t instruction, uint32_t address, uint32_t send_address,
void *destination, uint32_t length)`. The instruction is used only at 16-bit
width; the fifth argument is on the caller's stack. The wrapper loads the
active MSPI handle from `0x200270DC`; null handle
returns `2`. Null destination or zero length returns `6`. Address `>=
0x02000000` returns `5`, even when the send-address option is false. There are
no other argument, pointer-alignment, length, overflow, or end-address checks.

On accepted input it zeroes a 24-byte PIO command, then submits one blocking
transfer with timeout `1,000,000`:

| Offset | Value | Meaning |
|---:|---|---|
| 0 | `length` | transfer byte count |
| 4 | 0 | scrambling off |
| 5 | 0 | DCX off |
| 6 | 0 | RX direction |
| 7 | `((uint8_t)send_address != 0)` | normalized send-address flag |
| 8 | `address` if normalized flag is nonzero, else 0 | device address |
| 12 | 1 | send instruction |
| 14 | low 16 bits of instruction | device instruction |
| 16 | 1 | turnaround enabled |
| 17 | 0 | write latency disabled |
| 18 | 0 | continuation disabled |
| 19 | 0 | cleared padding/reserved byte |
| 20 | `destination` | receive buffer |

The send-address input is first truncated to eight bits. For example, `0x100`
means false, while `0x101` means true. The range check always tests the
original 32-bit address. If the transfer returns nonzero, the wrapper calls
`0x00415FAE` with module `0x00431420`, low-16-bit instruction, original
address, **length** (not destination pointer), and transfer status; then it
returns the status unchanged.

Callers include ready poll `0x0042074E`, which passes instruction `5`, address
`0`, send-address `0`, one-byte output buffer, and length `1`; the nearby
status-register helper `0x0042059E` passes instruction `0x9F`, no address, and
length `3`; `0x00420800` also uses this wrapper with instruction `0x15` and one
byte. These call patterns are consistent with one shared PIO submit wrapper,
not separate special-case decoders.

## Candidate build and tests

`nor_read_status.c` exposes the wrapper as readable C and keeps the MSPI
blocking transfer and error helper as linked provider interfaces. The
original/source fixture injects selected provider statuses and synthetic RX
bytes; it executes stock or source wrapper instructions and compares return
status, exact command bytes, helper calls, log arguments, and output buffer.

Build/test commands:

```sh
make -C g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status OUT=/tmp/nor-read-status
/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status/verify_nor_read_status.py --elf /tmp/nor-read-status/nor_read_status.elf --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status/nor-read-status-comparison.json
```

Result: **PASS**, 13 cases and 170 distinct original instruction bytes. Tests
cover success with and without an address, 8-bit send flag truncation,
instruction truncation, a transfer crossing the 32-MiB boundary, out-of-range
start, null/zero arguments, null active handle, a large unchunked length, RX
buffer writes, and unchanged nonzero status plus exact error-helper arguments.
No physical MSPI or NOR activity is claimed.

The standalone candidate is compiled using the Cortex-M4 Thumb subset so the
available Unicorn engine can execute its source instructions. That subset is
valid on Cortex-M55; this semantic comparison does not claim final target
compiler code generation.
