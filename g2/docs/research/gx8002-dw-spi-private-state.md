# DW SPI private-state evidence

`analyze_gx8002_dw_spi_probe.py` links the authenticated SDK object solely as a
comparison oracle and matches all five sections against stock, including the
268-byte probe section at package 0xfa0c. The pinned object is from NationalChip
SDK commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. This establishes initialized
BSS bindings: device state 0x20027ae0, SPI master 0x20027af0, and private driver
state 0x20027b14. No oracle bytes become firmware inputs.

| Private offset | Supported interpretation |
| --- | --- |
| 0x00 | Back-pointer to SPI master, written by probe |
| 0x04 | Controller pointer, initialized to 0xa3000000 |
| 0x08 | TX depth value obtained through controller +0x18 write/read probe |
| 0x0c | RX depth value obtained through controller +0x1c write/read probe |
| 0x10 | Current message pointer |
| 0x14 | Current transfer pointer |
| 0x18 | Selected TX buffer, or RX buffer when TX is absent |
| 0x1c | Transfer length |
| 0x20 | Zeroed during aligned transfer setup; broader meaning unresolved |
| 0x24 | Meaning unresolved |
| 0x28 | Element width byte; remaining three bytes unresolved |

Initialization attempts threshold values beginning at 2. It increments after
successful readback and has a 256-iteration bound. A mismatch at value 257
records zero; other mismatches preserve the attempted value. If all iterations
succeed, the stored value is 258. Do not assume a conventional power-of-two
FIFO depth or replace this logic with a generic hardware-driver probe.

Probe writes controller +0x2c = 78, drains data at +0x60 while status +0x28 has
bit 3 set, then waits for busy bit 0 to clear. It registers master bus 0 with
one chip select and IRQ 16 with the private-state pointer. The controller base
is separate from the transfer clock-control write at absolute 0xa030008c.
The interrupt handler's low absolute reads at 0x38/0x3c remain unexplained by
these bindings. Full C reconstruction and hardware qualification remain open.
