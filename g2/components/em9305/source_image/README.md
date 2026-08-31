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

This closes the software container-generation gap. It does not provide the
still-unavailable controller/vendor record sources, choose install placement
for the target-linked QP/C component, modify a device, or claim a complete
community EM9305 firmware image. Physical validation is blocked by unavailable
physical evidence.
