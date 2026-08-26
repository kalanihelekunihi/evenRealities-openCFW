# G2 charging-case UART/update source closure

Status: implemented in freestanding Cortex-M0+ C; destructive/live validation
is blocked by unavailable authorized charging-case evidence. No hardware,
serial port, erase, program, option-byte write, reset, signing, or flashing
operation was performed.

The authenticated case image establishes a `5A A5 FF` frame signature, a
header search limited to the first four receive offsets, an eight-bit additive
frame checksum seeded with `length - 2`, a 32-bit additive sum of big-endian
image words, nine write attempts in the stock `1..9` retry loop, command
`0x58` update offers, command `0x5A` nested chunk checksums, and the logged
dual-bank OTA sequence.

`components/shared/case/runtime_case_uart_update.c` reduces that complete
protocol boundary to eight APIs:

- bounded frame search and validation;
- exact frame checksum;
- image word-sum calculation;
- OTA offer decoding and version decision;
- chunk checksum validation;
- channel retry/failure-fill policy;
- OTA context initialization;
- callback-driven dual-bank state advancement.

The update state machine orders readiness, running-bank discovery, target-bank
erase, serial-window copy-forward, image receive, image verification, glasses
result notification, and option-byte bank swap/reset. All destructive work is
available only through explicit callbacks; the source unit itself has no
register, UART, flash, option-byte, reset, or device access.

The target gate compiles all eight definitions for
`thumbv6m-none-eabi`/Cortex-M0+ with warnings as errors. Host tests cover frame
bounds, checksum mutation, big-endian sums, offers, chunks, the exact retry
bound, failure fill, erase retry, serial-copy ordering, verify arguments,
notification, and bank swap.

Run:

```sh
make case-uart-update-closure
```

The official case payload remains in generated firmware packages. Replacing it
requires an authorized case, a UART capture, and backups of all four device-
specific serial windows: `0x0803F000..0x0803F00F`,
`0x0803F800..0x0803F807`, `0x0807F000..0x0807F00F`, and
`0x0807F800..0x0807F807`. Those physical preconditions are unavailable.
