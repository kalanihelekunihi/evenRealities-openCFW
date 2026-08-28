# G2 bootloader PIO-mixed callback wave (`0x0042488E`–`0x0042499C`)

Status: production-routed exact dual-profile source; physical validation is
blocked by unavailable physical evidence.

AmbiqSuite 5.1.0 `mspi_piomixed_configure` occupies 232 bytes at
`[0x0042488E, 0x00424976)` with SHA-256
`e8323e8e0ac6f59465ce1d30087eb6f4a2e3de336c45bff3e6954325a2e32fee`.
Its direct caller is `0x004258B8`. The typed host model covers all 26 device
values and maps them to normal, D2, AD2, D4, AD4, D8, or AD8 in `CTRL1` bits
0–3 at `0x40060004 + module * 0x1000`; unknown values remain successful no-ops.

The adjacent AmbiqSuite `mspi_dummy_callback` is the exact `bx lr` body at
`[0x00424976, 0x00424978)`. Its Thumb pointer is stored at `0x00426C00`.
Both adapters compile byte-identically under the two reviewed target profiles
and have no relocations.

The adjacent 36-byte `mspi_seq_loopback` callback at
`[0x00424978, 0x0042499C)` increments the completed index from the last
programmed index, clears the transaction interrupt, publishes transfer
completion, and writes `0x40` to the per-module `CQSETCLEAR` register. Its
target adapter is also byte-identical under both reviewed profiles.

After production admission, component accounting is 28,041 source-owned bytes,
12,454 exact in-place bytes, and 119,255 retained official bytes. The next
four bytes at `0x0042499C` are the retained `0x40060000` MSPI base literal;
the next executable body is AmbiqSuite `mspi_clkgen_ctrl` at `0x004249A0`.

This software-only source wave performed no flash, reset, signing, or MMIO
operation. PIO mixed-mode protocol, callback, and cold-boot qualification is
blocked by unavailable physical evidence; this source closure does not by itself declare
firmware functional completeness.
