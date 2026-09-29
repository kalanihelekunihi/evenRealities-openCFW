# R1 documentation

Start with the consolidated references. They separate stock-proven facts from
values the retired openR1 implementation chose.

| Document | Contents |
| --- | --- |
| [`memory-map.md`](memory-map.md) | flash, RAM and UICR layout, FDS and FAL partitions, bootloader regions, image hashes, rebuild oracle |
| [`toolchain-and-dependencies.md`](toolchain-and-dependencies.md) | stock SDK and library identities, Arm Compiler evidence, SDK link set, byte-equality blockers |
| [`protocol.md`](protocol.md) | BAE8 service and buttonless DFU, EUS and pb_tran framing, CRCs, dispatch tables, sync packets |
| [`storage-formats.md`](storage-formats.md) | kv.bin, health.db, sleep.db, log.bin, ep.bin, pKey.bin, retained RAM, FDS |
| [`hardware-pinout.md`](hardware-pinout.md) | TWIM and software-TWI buses, GPIO, SAADC, peripheral addresses, PMIC single-wire timing, clocks |
| [`security-and-bootloader.md`](security-and-bootloader.md) | DFU trust model, and stock defects a byte-identical build must reproduce |
| [`hardware-observations.md`](hardware-observations.md) | field firmware versions and physical measurements |
| [`PROVENANCE.md`](PROVENANCE.md) | stock address index for recovered behaviour |
| [`SECURITY.md`](SECURITY.md) | security audit findings on the stock firmware |

Evidence records, filed by kind:

| Directory | Contents |
| --- | --- |
| [`correlation/`](correlation) | one record per subsystem, pinning behaviour to stock addresses, byte counts and record layouts |
| [`boundaries/`](boundaries) | per-provider seams and attribution for binary-only vendor code (GoMore, Goodix, IQS7211E and others) |
| [`closures/`](closures) | Nordic SDK closure proofs and the B56EE2 hardware validation |
| [`reference/`](reference) | function ownership for all 2,972 stock functions, the Ghidra entry census, and BSim run summaries |

Some correlation and boundary records describe how the retired openR1 code
corresponded to stock, and cite its `src/` and `platform/` files. Those files
are available at Git commit `832137ec`. The stock-side addresses and layouts
in the records remain valid.
