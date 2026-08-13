# Cordio `attc_sign.c` exclusion audit

## Result

Optional ATT client signing is not linked in the stock G2 image. All seven
`attc_sign.c` definitions are source-only: the three control-block helpers,
two callbacks, `AttcSignedWriteCmd`, and `AttcSignInit`. No executable or data
bytes are assigned to this translation unit.

This is a positive exclusion, not merely a missing source-path match. Stock
`AttcInit` at `0x00531B1C` explicitly writes null to `attcCb.pSign` at
`attcCb + 0x1B0`, and its sole caller is the normal stack initializer at
`0x004B806A`. The entire image contains only two literals for
`attcCb=0x2006F904`, both owned by already-bounded `attc_proc.c` and
`attc_main.c`; there is no direct literal for `0x2006FAB4` and no later
callback-interface installation.

## Independent provider census

A linked `attcSignMsgCback` must call both `DmSecGetLocalCsrk` and `SecCmac`.
The complete image has one local-CSRK call, owned by SMP, and two CMAC calls,
owned by the ATT server database-hash path and SMP. No third client-signing
consumer exists.

A linked `AttcSignedWriteCmd` must call `DmConnSecLevel` and fall back to
`AttcWriteCmd` on an encrypted connection. `AttcWriteCmd` has exactly one
stock caller, in the complete product dispatcher body
`[0x004C4910,0x004C4B7E)`; that body has no `DmConnSecLevel` call. The image
also contains no `attc_sign.c`, `attcSign`, or exported signed-write marker.
Together with the null interface, these independent fingerprints account for
every public and internal source definition.

The ordinary ATT client core still recognizes signed-write/CMAC message IDs
and null-checks `pSign`; with the optional interface absent, those paths are
safe no-ops. This does not exclude ATT server-side signing, which is a
separate `atts_sign.c` unit.

## Source compatibility and provenance

The build-ready Apache-2.0 compatibility oracle is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`0595be9f0ae3f7b7f19c5d8d4fb0074eb6a0cf97`, 9,927 bytes, SHA-256
`0c13297d0724fbd2f2bd44ca6e86431423c14e0648d76116e2fe069b01f1f0b9`.
The file is byte-identical from r20.05 through r20.05c and in the later
official AmbiqSuite R4.4.1 import. The r19/AmbiqSuite 2.x oracle is blob
`3d3c2858d3820dc0460a4e911c14561c3bad979b`, SHA-256
`0a6b0a0c117f8305d6866a587d4ee8053ec7843b124a6c3910a1bd6268a959ee`.

No stock function survives to discriminate these source versions. The r20
selection is compatibility alignment with the independently proven stock EATT
core, not a claim that this absent file generated any firmware bytes.

## Reproducibility

`tools/analyze_g2_cordio_attc_sign.py` pins the official image, seven-function
source inventory, both `attcCb` literal cells, the exact `AttcInit` nulling
sequence and caller, every CMAC/local-CSRK/security-level/write-command call,
the sole `AttcWriteCmd` caller body, and all absent markers. Source hashes are
in `tools/manifests/packetcraft-cordio-attc-sign-function-map.tsv`; provenance
is in `tools/manifests/packetcraft-cordio-attc-sign-provenance.tsv`.

This audit changes provenance only: zero stock bytes are replaced and zero
source-owned production bytes are added.
