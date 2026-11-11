# R1 sparse source-region HEX, 2026-11-11

`./make.sh r1-source-regions` now compiles and strictly links the R1 C
application and bootloader, then exports their checked raw bytes and two
source-linked UICR words to a sparse Intel HEX. The exporter is
`tools/build/r1_source_regions.py`. It verifies that the two receipts share
the same source report and manifest, that each link is valid with no missing
symbols or archive members, that all 1,023 participating C source files still
match the strict source report, that the raw files still match their recorded
hashes, and that the flash and UICR ranges do not overlap. It writes only
these four regions:

| Region | Address interval | Bytes |
| --- | --- | ---: |
| Application | `0x27000..0xd07e3` | 694,244 |
| Bootloader | `0xf8000..0xfd9ef` | 23,024 |
| Bootloader-start UICR | `0x10001014..0x10001017` | 4 |
| MBR-params UICR | `0x10001018..0x1000101b` | 4 |

An end-to-end run under `build/r1-source-regions-integrated-20261111/`
produced `r1-source-regions.hex` with SHA-256
`34c5c2a7fb2d511bd38e17cc09ef4438d02eb1158f99f1970ab76c216754ac18`.
The application and bootloader region hashes remain
`2c3bf3d374eb1df387c8bf0ae942e983420065b69c814d7de8460c4f26c579ab`
and `08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
A second run from the earlier same-image receipts produced byte-identical
HEX. GNU `objcopy` independently parsed the output into 14 allocated ELF
sections; comparing every parsed byte against the four original inputs
covered all 717,276 bytes with no missing, extra, or differing byte.
Negative probes rejected a changed application hash, a bootloader receipt
from a different source build, and a source-report entry whose claimed C
source hash disagreed with the current file.

This HEX is **not** an installable whole-device image. It excludes Nordic's
precompiled S140/MBR, DFU settings, FDS/FAL contents and package metadata.
It establishes sparse placement and provenance for the C-linked regions,
not stock byte identity, physical boot, or an assembly-free application.

An ignored checksum-verified parse of the pinned SDK S140 7.2.0 HEX records
155,956 vendor bytes in `0x00000..0x00aff` and `0x01000..0x26633`.
Its SHA-256 is
`c52b61a6ceeb58438dbef075abfc5f6812718dda78630b39e82a20829f09c125`.
It does not overlap any source-linked region; the application starts at
`0x27000`. The parse receipt is
`build/r1-source-regions-verified-20261111/s140-layout.json`. This is a
placement check only; the vendor binary remains outside the C-source claim.

After removal of the R1 EABI division adapters, the current strict receipts
at `build/r1-link-eabi-pure-c-20261111/` and
`build/r1-boot-link-eabi-pure-c-20261111/` also pass the exporter. It rechecks
1,023 participating C sources, including the generated copies of pinned
upstream files. The current sparse HEX is
`build/r1-source-regions-eabi-pure-c-20261111/r1-source-regions.hex`, SHA-256
`77acfc719dbbfa55039cf4f5600fb05989f3847e22c4e627690be5fa0f5e43c9`.

The signed Goodix AGC correction passes a fresh strict build and exporter
under `build/r1-source-regions-eabi-agc-signed-20261111/`. Its application
region is 694,196 bytes, SHA-256
`6ca24db9ec3209c9abd20858fede662b368f84ea8be5bb0cfb698b6b9f405068`;
the bootloader region is unchanged. The current sparse HEX SHA-256 is
`3717ad7fe9f8e8d5bc9bb0cfc0cb4dfe259b180f34205992f5b2a78134243b62`.
