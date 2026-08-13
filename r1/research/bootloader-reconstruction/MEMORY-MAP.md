# R1 bootloader memory map

All addresses are absolute nRF52840 addresses for the live retail image.

| Start | End inclusive | Bytes | Classification |
| ---: | ---: | ---: | --- |
| `0x000f8000` | `0x000f80ff` | 256 | 64-word Cortex-M vector table |
| `0x000f8100` | `0x000f81ff` | 256 | zero-filled reserved/alignment space |
| `0x000f8200` | `0x000fd867` | 22,120 | Thumb code, literal pools, dispatch tables, and linked constants |
| `0x000fd868` | `0x000fd8a7` | 64 | raw little-endian P-256 public verification key (`X || Y`) |
| `0x000fd8a8` | `0x000fde1b` | 1,396 | linked constants, pointer tables, crypto constants, and small leaf helpers |
| `0x000fde1c` | `0x000fde9b` | 128 | scatter-load, BSS-zero, and runtime-initializer records |
| `0x000fde9c` | `0x000fdf63` | 200 | initial `.data` load image copied to SRAM |
| `0x000fdf64` | `0x000fdfff` | 156 | erased `0xff` padding outside the logical linked image |

The reset metadata reconstructs these SRAM bounds:

| Runtime region | Start | End exclusive | Bytes | Evidence |
| --- | ---: | ---: | ---: | --- |
| initial `.data` | `0x20005978` | `0x20005a40` | 200 | load source `0x000fde9c`, length `0x000000c8` |
| zeroed `.bss` | `0x20005a40` | `0x2000cfa0` | 30,048 | zero length `0x00007560` |
| initial main stack pointer | `0x2000cfa0` | — | — | vector word 0 |

The bootloader runtime and application handoff also reference these external flash regions:

| Region | Address range | Role |
| --- | --- | --- |
| bootloader and MBR-parameter ACL | `0x000f8000...0x000fefff` | write-protected before application handoff |
| MBR parameters/settings backup | `0x000fe000...0x000fefff` | protected retained MBR command and backup settings page |
| primary settings | `0x000ff000...0x000fffff` | writable primary DFU settings page |
| application/staging region | below `0x000f8000` | application and DFU cache/bank storage |

The generated [`vectors.csv`](generated/vectors.csv),
[`instructions.tsv`](generated/instructions.tsv), and
[`defined-data.csv`](generated/defined-data.csv) provide the byte-level evidence behind this map.

