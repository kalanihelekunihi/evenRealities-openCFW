# G2 smart glasses firmware

The target is the official EVENOTA bundle `s200_v2.2.6.10`: 4,301,227 bytes,
SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`,
locked in [`workflow/target.json`](workflow/target.json). The goal is C source
that compiles, with the original toolchains, into a bundle byte-identical to
it.

| Payload | Processor | Original toolchain | Size |
| --- | --- | --- | ---: |
| `ota/s200_firmware_ota.bin` (main application) | Apollo510B Cortex-M55 | IAR EWARM + DLIB | 3.52 MB |
| `ota/s200_bootloader.bin` (Even bootloader) | Apollo510B Cortex-M55 | IAR EWARM | 149 KB |
| `firmware/ble_em9305.bin` | EM9305 ARCv2 EM | Synopsys MetaWare T-2022.09 | 211,948 B |
| `firmware/codec.bin` | GX8002B C-SKY CK804EF | C-SKY GCC (release open) | 326,092 B |
| `firmware/touch.bin` | PSoC 4000T Cortex-M0+ | GCC indicated | 34,464 B |
| `firmware/box.bin` (case) | STM32G0B1-class Cortex-M0+ | GCC indicated | 55,784 B |

## Process

Follow [`workflow/README.md`](workflow/README.md): inventory, whole-image
pseudocode with independent review, freeze, and only then C reconstruction and
byte comparison. The cross-device plan and the list of shortcuts are in
[`../docs/roadmap.md`](../docs/roadmap.md).

## Layout

```
g2/
├── workflow/          active procedure, target lock, gates, prompt pack, task records
├── blobs/official/    versioned firmware mirrors, metadata, and provenance
├── manifests/         g2-2.2.6.10.json (reference EVENOTA layout);
│                      g2-2.2.6.10-core-source.json (codec region map read by
│                      the hash-pinned codec analyzer)
├── docs/reference/    formats, memory map, toolchains, libraries, protocols,
│                      capability checklist, hardware notes
├── symbols/           address-keyed naming seeds per payload
├── config-recovered/  recovered upstream configuration headers and patches
├── research/          retained Ghidra corpus: all 7,449 Apollo functions, case
│                      frontier, EM9305 rounds, IAR and QP/C evidence
├── components/em9305/source_image/record_package.py   EM9305 record-package codec
├── tools/             EVENOTA packer, container analyzers, Ghidra pipeline
└── tests/             tests for those tools
```

Upstream libraries are pinned as submodules in
[`../third-party/`](../third-party/README.md). Hardware facts are in
[`../docs/hardware/`](../docs/hardware/README.md).

## Commands

The user-authorized bounded foundation implementation adds
[`components/foundation/touch_scb/`](components/foundation/touch_scb/README.md)
and [optional resource preservation](tools/RESOURCE_PRESERVATION.md).
`make foundation-test` compiles/tests the callback-based C component and the
lossless local resource path; `make foundation-object` builds a freestanding
Cortex-M0+ object. These are reusable components and tools; they are
not target-linked firmware providers or evidence that the corpus freeze/source
build gates passed. The locked reference providers remain unchanged.

```sh
make -C g2 test              # kept tool tests; payload-dependent ones skip if absent
make -C g2 reference         # byte-identical repack of the official payloads
make -C g2 verify            # plus manifest and research-corpus checks
make -C g2 ghidra-harvest OPENCFW_APOLLO_GHIDRA_PROJECT=/abs/project
```

## History

The hybrid-overlay campaign was removed on 2026-09-29. It compiled per-function
overlays and patched them into stock bytes. It also produced behavioural
rewrites of the touch and case images, and GX8002 equivalence proofs. None
of it produced a byte-identical payload. Its durable facts are in the
references above, and the files are in Git history (commit `832137ec`).

The history contains official-derived firmware under `g2/.tmp-*` paths. Do not
publish or mirror it as-is.

The source-backed [Ambiq MSPI interrupt subset](components/foundation/ambiq_mspi/README.md)
has a standalone Cortex-M55 callable simulator target:
`make ambiq-mspi-simulator` / `make ambiq-mspi-simulator-test`. It is not a
bootable production provider; clocks, IRQ/DMA and board initialization remain
external to its synthetic tests.
