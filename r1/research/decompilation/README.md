# Even Realities R1 firmware decompilation corpus

## Result

This directory is the exhaustive, address-indexed export of every R1 firmware byte region that is
actually present in this workspace. It covers the signed OTA application payload from release
`2.2.6.0009`, the live 24 KiB production bootloader span recovered from an owned retail ring, and
the supplied UICR/protection snapshots. The export contains:

- 2,687 fixed-point Ghidra-discovered application functions at their linked addresses;
- 285 fixed-point and evidence-seeded bootloader functions at their linked addresses;
- C-like decompiler output for 2,971 of those 2,972 functions;
- a checked manual C recovery for the one Ghidra low-level overlap failure at `0x000979dc`;
- complete function, symbol, call-edge, memory-block, and decoded-instruction tables; and
- a compiled C image emitter that reproduces every supplied unsigned/raw artifact byte-for-byte.

This is a complete export of the **supplied corpus**, not a claim that stripped, optimized machine
code can be inverted into the vendor's original source tree. Original identifiers, comments,
typedefs, macros, file boundaries, inline boundaries, compiler version/options, linker script, and
undefined-behavior assumptions are not encoded in the binary and cannot be uniquely recovered.
The generated `decompiler-output.c` files are therefore analysis-grade C-like output, not a
drop-in firmware build.

## Supplied image map

| Region | Address range | Bytes | Status |
| --- | --- | ---: | --- |
| S140 MBR + SoftDevice dependency | `0x00000000...0x00026fff` | 159,744 | Not present in the workspace; the signed init packet requires S140 `7.2.0` / firmware ID `0x0100` |
| R1 application `2.2.6.0009` | `0x00027000...0x000c4d07` | 646,408 | Present, SHA-256 pinned, wholly exported |
| Application-aligned tail/private flash/staging gap | `0x000c4d08...0x000f7fff` | 209,656 | No byte dump supplied; behavior/layout is documented elsewhere, but contents cannot be decompiled |
| Live production bootloader | `0x000f8000...0x000fdfff` | 24,576 | Present, SHA-256 pinned, wholly exported |
| MBR parameter page | `0x000fe000...0x000fefff` | 4,096 | Not supplied |
| Bootloader settings page | `0x000ff000...0x000fffff` | 4,096 | Not supplied |
| UICR snapshot | begins at `0x10001000` | 776 | Present as a partial live snapshot; exact bytes preserved |
| APPROTECT runtime words | mixed register reads | 12 | Present; this is not a contiguous flash mapping |

Because the exact SoftDevice/MBR bytes, gap/private-flash contents, parameter page, and settings
page are absent, a truthful full-device image cannot be synthesized from this corpus. The exact
application payload and bootloader span can be reproduced independently.

## Corpus layout

| Path | Purpose |
| --- | --- |
| [`artifact-inventory.csv`](./artifact-inventory.csv) | Source path, load address, byte count, digest, and signing-material disposition |
| [`application/functions.csv`](./application/functions.csv) | All 2,687 application function bodies and addresses found by fixed-point Ghidra analysis |
| [`application/decompiler-output.c`](./application/decompiler-output.c) | Address-delimited C-like output for each application function |
| [`application/manual-recovery/0x000979dc.c`](./application/manual-recovery/0x000979dc.c) | Compile-checked semantic recovery for the sole automatic decompiler failure |
| [`application/disassembly.s`](./application/disassembly.s) | Every decoded application instruction with exact address and bytes |
| [`application/call-graph.csv`](./application/call-graph.csv) | Direct call edges with caller, call site, target, and callee |
| [`application/symbols.csv`](./application/symbols.csv) | Complete Ghidra symbol/reference-label export |
| [`bootloader/functions.csv`](./bootloader/functions.csv) | All 285 bootloader function bodies and addresses found by fixed-point analysis plus evidence-backed optimized tail-target seeds |
| [`bootloader/decompiler-output.c`](./bootloader/decompiler-output.c) | Address-delimited C-like output for every bootloader function |
| [`bootloader/disassembly.s`](./bootloader/disassembly.s) | Every decoded bootloader instruction with exact address and bytes |
| [`rebuild/emit_image.c`](./rebuild/emit_image.c) | Compilable C program that emits any supplied raw image region |
| [`rebuild/manifest.json`](./rebuild/manifest.json) | Exact unsigned/raw rebuild sizes and digests |

The `functions.csv` files are the canonical function-address indexes. The disassemblies and byte
includes retain evidence that a decompiler necessarily classifies as literal pools, tables,
strings, model weights, padding, or currently undecoded data. No supplied byte is discarded.

## Reproduction

Regenerate the Ghidra corpus from the pinned local inputs:

```sh
python3 scripts/firmware/export_r1_decompilation.py --overwrite-projects
```

Compile and verify the exact-byte C emitter:

```sh
make -C docs/r1-firmware-decompilation/rebuild verify
make -C docs/r1-firmware-decompilation/rebuild clean
```

Validate function/export/rebuild coverage:

```sh
python3 scripts/firmware/verify_r1_decompilation.py
```

The exporter repeats auto-analysis until two consecutive passes agree on the function count. Ghidra
projects are disposable derived state under `build/r1-ghidra-projects`; all durable findings are in
this directory.

## What “recompilable” means here

There are two separate fidelity claims:

1. **Byte fidelity:** `rebuild/emit_image.c` compiles on the host and emits the exact captured raw
   application, bootloader, UICR, or runtime snapshot. The verification step checks SHA-256 and
   size. No OTA signature or private signing key is included.
2. **Semantic recovery:** the Ghidra C-like files and the manual recovery express discovered
   control/data flow at fixed addresses. They are suitable for audit and incremental human
   reimplementation, but cannot be promised to compile into identical machine code without the
   missing types, source/library versions, compiler/linker configuration, and absent flash regions.

Conflating these claims would make the output look more complete than the evidence permits. A
future source reconstruction should promote functions from decompiler output into reviewed C one
subsystem at a time, compare execution against the captured instructions, and retain the exact-byte
lane as the immutable oracle.

## Signing boundary

The OTA init packet and its package signature are not embedded in the rebuild corpus. The live
bootloader necessarily contains the public verification key and signature-checking code because
those bytes are part of the captured executable; no private signing key is present. This corpus
does not patch, disable, emulate, or validate a secure-boot/signature-enforcement bypass.

Detailed behavioral findings remain in
[`../r1-2.2.6.0009-firmware-analysis.md`](../r1-2.2.6.0009-firmware-analysis.md), the 199-row
[`../r1-capability-matrix.csv`](../r1-capability-matrix.csv), and
[`../r1-bootloader-security-decompilation.md`](../r1-bootloader-security-decompilation.md).
