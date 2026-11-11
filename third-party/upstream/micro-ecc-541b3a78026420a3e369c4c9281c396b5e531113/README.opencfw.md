# Pinned micro-ecc C source slice

Upstream: https://github.com/kmackay/micro-ecc
Revision: 541b3a78026420a3e369c4c9281c396b5e531113

Unmodified source files and license were fetched at this exact revision;
`provenance.json` records source URLs and SHA-256 hashes. The R1 bootloader
uses the Nordic SDK micro-ecc adapter, P-256 only, native little-endian
coordinates, four-byte words, optimization level 2 and `uECC_PLATFORM=0`.
The latter explicitly selects portable C rather than ARM assembly.
Unused assembler includes and other repository files are not part of this slice.

This version rejects a valid signature under the curve-generator public key
(private scalar 1) in the original unmodified-source verification probe. See
`r1/docs/reference/boot-ecc-c-review.md` for the confirmed scope and product-key
check. Source availability and successful linking do not imply complete crypto
or physical DFU qualification.

The normal R1 composition subsequently replaces the raw verification function
in a generated translation unit with `r1/src/bootloader/crypto/uecc_verify_complete.h`.
The pinned files here remain unmodified. Current correction evidence is in
`r1/docs/reference/boot-ecc-complete-c-review.md`.
