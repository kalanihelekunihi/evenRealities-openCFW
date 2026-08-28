# Apollo `0x5Dxxxx` none-census source admission

This directory is a controlled, production-excluded source admission for all
198 bodies (33,644 bytes) in the closed `none` census:

- 192 bodies / 33,124 bytes map to the authenticated FreeType 2.9.1 snapshot.
  They retain the FreeType Project License (`g2/third_party/freetype/LICENSE`)
  and all file-specific notices.  In particular, Adobe-authored `psft.c`
  retains its copyright, permission terms, and patent grant in the source.
- Six bodies / 520 bytes map to SEGGER RTT 6.18a.  The provider is the copy in
  Nordic nRF5 SDK 17.1.0, pinned by the repository's fetched-provider manifest.
  Its source, headers, and `license/license.txt` are materialized together under
  `segger_rtt_6_18a`; line endings are normalized for the repository, and both
  the exact archive digest and deterministic normalized-file digests are checked.
  This repository does not relicense or locally recreate it.
- Four surrounding non-census intervals / 1,118 bytes remain SHA-pinned typed
  external boundaries because the authenticated corpus has no complete callable
  records for them.  They are accounted, non-opaque, and not implementations.

`analyze_g2_cordio_ll_sea_none_source_admission.py` is the canonical admission
record.  It expands all 198 address/body rows, pins every local upstream module,
checks every claimed symbol against its module, verifies the license/provenance
files, checks the external SEGGER provider record, and reconciles the four typed
boundaries.  The C files are MIT metadata glue only; they copy no upstream code.

## Binary-admission blocker

Source admission is ready, but stock-address binary overlay admission is
intentionally false.  No reviewed recipe currently proves all of the following:

1. the exact original compiler version, options, FreeType configuration macros,
   ABI choices, and link-time optimization state;
2. function-section, literal-pool, constant-table, veneer, and data placement at
   the authenticated addresses for every one of the 198 bodies;
3. complete relocation and caller/callee rewrite closure, including calls that
   cross this census and the four incomplete non-census boundaries;
4. a reviewed flash/RAM/stack/WCET budget for the rebuilt provider graph; and
5. exact product `sdk_config` values and the reviewed target critical-section
   adapter required by the Nordic-flavoured SEGGER configuration.

Consequently, this admission supplies no overlay manifest, no stock-address
redirects, and no production build route.  The Cortex-M55 freestanding harness
proves that the provider/accounting contract and the materialized SEGGER source
compile for the target ABI, while unavailable binary-placement claims fail closed.
