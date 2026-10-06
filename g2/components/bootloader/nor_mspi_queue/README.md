# Apollo510 MSPI command-queue source candidate

This leaf-sized source candidate implements the bootloader's MSPI clockgen
control, CQ wrappers, the linked generic command-queue init/enable/disable/
term/index-update functions, and the 480-byte scalar peripheral resource table
at stock address `0x430880`. The output is not yet integrated into the shared
bootloader build.

The generic queue state rows are at `0x200262f0`, stride `0x2c`; the operation
table is at `0x430880`, stride `0x28`. The MSPI module state rows are at
`0x2001caa0`, stride `0x8d0`, with the queue-handle slot at offset `0x828`.
The operation table and state layout are derived from the pinned image, and
the synthetic tests exercise the four actual MSPI interfaces (8–11).
`resources.c` emits all 12 rows at `0x430880`; all pointer-shaped fields are
`0x400xxxxx` MMIO addresses, and no field points to executable code or a
callback. The table's exact stock-byte SHA-256 is
`1ed1fa3682f9c16c403ee0e6cee7761b70ca610656a2b6e56de3f0b05cee7fea`.

Link-time dependencies are deliberately limited to the stock critical-save
routine (`0x41b8ec`), clock request (`0x4222f0`), and delay entry (`0x41d1c0`).
The first dependency and PRIMASK restore execute stock instructions in the
comparison harness; clock request and delay are injected callbacks. All queue
state transitions and register access in this component execute from source.
The clockgen implementation is an independent duplicate candidate; the root
integration is using the separate upstream worker's implementation.
Compile this component with `-DOPENCFW_USE_EXTERNAL_MSPI_CLOCKGEN` when linking
that upstream implementation; this excludes only the duplicate clockgen body.

Build and compare from the repository root:

```sh
make -C g2/components/bootloader/nor_mspi_queue OUT=/tmp/nor-mspi-queue
/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/mspi-queue/verify_mspi_queue.py \
  --elf /tmp/nor-mspi-queue/nor_mspi_queue.elf \
  --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/mspi-queue/result.json
```

The comparison uses only Unicorn synthetic RAM/MMIO. It does not access a
device or establish behavior for queue post/release/interrupt flows.
