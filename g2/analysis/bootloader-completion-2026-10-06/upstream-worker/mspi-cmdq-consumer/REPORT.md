# Stock MSPI command-queue initialization provider

## Result

Reconstructed `am_hal_cmdq_init` at `0x00427794..0x00427878` as a readable
freestanding C provider in `am_hal_cmdq_init.c`. The source implements the
private 32-bit table layouts and direct register writes observed in the locked
bootloader; it does not import or claim compatibility with a public SDK CMDQ
structure.

The ARM build and original/source Unicorn comparison pass:

- Isolated consumer: 19 cases; all 228 stock instruction bytes reached and
  source results match for status, all 12 state rows, the full synthetic
  peripheral window, and the output handle.
- Chained enable → `mspi_cq_init` → `am_hal_cmdq_init`: 12 cases; 398 distinct
  stock instruction bytes reached across the three functions, with complete
  compared state/peripheral snapshots matching. The chain includes module IDs
  0–3 and validates the `module + 8` queue interface mapping.
- Chained source-table profile: the same 12 cases and 398 distinct stock
  instruction bytes, with the source ELF supplying the operation table at its
  stock address. All 480 compiled bytes match the locked table exactly.

Run `make test`, `make chain-test`, and `make chain-table-test` with the pinned
local Unicorn environment. The source ELFs, exact differential results, and
byte traces are in `out/`.

## Recovered provider ABI and data

The function’s literal at `0x00427c80` resolves to state base
`0x200262f0`; its literal at `0x00427c84` resolves to the 12-row interface
operation table at `0x00430880`. The stock body uses 0x2c-byte state rows and
0x28-byte operation rows. Their accessed fields are laid out explicitly in
the C file, with offsets based on the function’s loads and stores only.

For interface `i`, the state row is `0x200262f0 + i*0x2c`. The function reads
the bit-24 initialization guard at row+0, stores queue buffer/indices at
+4, +8, +c, +10, and +14, queue size in bytes at +18, zeros +1c/+20, and stores the
operation-row address at +24. It does not touch +28. The check is bit 24,
confirmed by stock `UBFX #24,#1`; it is not the sign bit.

The operation row is `0x00430880 + i*0x28`. Accessed words are: option
register pointer +0, buffer pointer +4, two reset-register pointers +8/+c,
control-register pointer +10, and OR mask +14. Rows 0–7 point into the
`0x400502xx` through `0x400572xx` register blocks with mask `0x8000`. Rows
8–11 point into `0x400602xx` through `0x400632xx` with mask `0x4000`.
Initialization zeros the two reset registers, ORs the mask into the control
register, writes the configured queue buffer, writes `((config[8] & 1) << 1)`
to the option register, and stores the state-row address through the output
slot. It makes no function calls; its platform boundary is the ops table’s
MMIO addresses.

The three-status contract is directly observed: `5` for interface IDs at or
above 12, `6` for invalid config/buffer/output/size, `7` if the state row’s
bit-24 initialization guard is already set, and `0` after initialization.
The size check accepts values of at least two half-units; the wrapper
`mspi_cq_init` supplies `queue_size_input >> 1`.

## Provenance and verification

The reference bytes came from
`g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
The function range hash is
`ad7e3d6257b791855a8cd7fe90389313dfb9496262724777900d6a4193c09b52`, matching
`g2/symbols/bootloader.tsv`. The two absolute table bases were read from the
body’s PC-relative literals and independently checked against the image bytes.

`cmdq_ops_table.c` reconstructs the constant 12×0x28-byte table as source
data. The table is linked at `0x00430880`; `chain_with_ops.ld` keeps that
placement. The source-table profile extracts the linked ELF bytes and compares
all 480 bytes directly against the locked image before execution. Both hashes
are `1ed1fa3682f9c16c403ee0e6cee7761b70ca610656a2b6e56de3f0b05cee7fea`.
That profile runs with the reference image bytes absent from the source
machine’s mapped image region, so its table data comes only from the source
ELF. The earlier `chain-test` profile remains available and continues to use
the reference image table.

The chained link reuses the independently reconstructed sources in sibling
`mspi-enable/` and `mspi-cq-init/` directories. Only a thin linker-name adapter
connects the CQ wrapper’s stock `mspi_cq_init` and `am_hal_cmdq_init` names to
these sources. Clang targets ARM Cortex-M55 Thumb/soft-float and the link uses
the local GNU ARM binutils. Unicorn runs the original image and compiled ELF
offline with synthetic RAM; no device or live peripheral is accessed.

## Remaining boundary

This closes only the three-function queue-initialization path. The test seeds
the literal operation table from the locked image and maps peripheral targets
as ordinary RAM, so it confirms pointer/layout/dataflow agreement but cannot
establish MSPI clocking, reset semantics, command-queue execution, DMA, timing,
or hardware behavior. Other command-queue APIs, MSPI setup/clock providers,
full startup, original IAR runtime/linker layout, and complete firmware/bundle
byte identity remain outside this work. The compiled source is not claimed to
reproduce the original toolchain’s machine code.
