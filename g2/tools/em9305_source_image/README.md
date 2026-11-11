# EM9305 source-image record package

SPDX-License-Identifier: MIT

This directory provides the deterministic deployment wrapper for source-built
EM9305 records. The package contains a four-byte format marker, total payload
length, record count, erase-sector count, contiguous `(file offset, size,
target address)` descriptors, 16-bit erase-sector IDs, zero alignment padding,
and record payloads.

`record_package.py` parses and rebuilds the authenticated four-record stock
container byte-for-byte. `build_image.py` accepts only an explicit JSON layout
whose record bytes come from caller-supplied build outputs. It rejects empty,
overlapping, wrapped, non-contiguous, truncated, or noncanonical packages.

The G2 source linker produces a candidate C NVM bootloader at `0x300000`,
record 2 (`FHDR` and NVM entry), and the application separately. The C
bootloader implements the stock boot sequence and header-processing roles
identified in records 0 and 1, with a different byte layout. Record 2 is compiled from
`g2/src/em9305/boot-header/nvm_header_entry.c`; its length and CRC fields are
finalized from the linked application by `tools/build/em9305_record2.py`.
The authenticated stock record round-trips through that finalizer exactly.
`tools/build/link_g2_sources.py` wraps the three source outputs into a
source-candidate package. The source bootloader's selection and reset behavior
has not been shown equivalent to stock, and no physical EM9305 run has been
validated. The candidate package is not a hardware-qualified release.
