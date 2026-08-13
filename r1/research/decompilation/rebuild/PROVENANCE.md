# R1 image reconstruction

This directory rebuilds the four pinned R1 `2.2.6.0009` images byte-for-byte
from stored byte arrays, and authenticates the result against
[`manifest.json`](manifest.json).

```sh
make -C r1/research/decompilation/rebuild verify
```

That compiles `emit_image.c`, emits each image, and fails closed unless every
size and SHA-256 matches. The rebuilt application is what the R1 analysis
scripts under [`../../../tools/`](../../../tools) read by default.

## Pinned images

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| application | 646,408 | `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a` |
| bootloader | 24,576 | `566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b` |
| uicr | 776 | `1a6dc7725aa1903ed240dd245ecd036a6c72b244e8b26179affdd0fdde74b150` |
| approtect-runtime | 12 | `fafdd44c03daf5f7ecfa57113ebd319de6fb8f84fa0b7b0c5ac60d09f811fb71` |

No signing material is included; `manifest.json` records that explicitly.

## What is and is not in this repository

The `*.bytes.inc` arrays are the vendor firmware in another encoding, so they
are **not** tracked here — the same policy this repository already applies to
the G2 OTA payloads under
[`../../../../g2/blobs/official/`](../../../../g2/blobs/official). What *is*
tracked is everything needed to rebuild and check them once you supply your own
copy:

- `emit_image.c`, `Makefile`, `verify.py` — the reconstruction and its gate;
- `manifest.json` — the sizes, digests, and the source image each array came
  from;
- the decompilation corpus in [`../application/`](../application) and
  [`../bootloader/`](../bootloader) — disassembly, decompiler output, call
  graph, symbols, and memory blocks, which are analysis products rather than
  vendor bytes.

To regenerate the arrays, dump your own copy of each image as a C byte array
(16 bytes per line, `0x%02x, ` formatting) into the matching
`<image>.bytes.inc`, then run `make verify`. A digest mismatch means the source
image is not the pinned one.

## Without the payload arrays

`make verify` and the ~145 analysis scripts that default to
`rebuilt-application.bin` cannot run. Everything else in this repository is
unaffected: the R1 firmware builds and its full test suite passes with no
vendor payload present.

```sh
make -C r1 test sanitize arm-objects
```
