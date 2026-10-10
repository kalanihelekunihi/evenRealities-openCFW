# G2 shortcut theory: independent v4.2, provenance, and build-path continuation

Three Daybreak Blue Low agents worked in separate evidence lanes on 2026-10-10. They preserved the locked target, existing checkout changes, `.gitmodules`, canonical coverage ledgers, and `P2_EXECUTING` state. This report supersedes the preliminary classifications in the first v4.2 source receipt while retaining that receipt for audit.

## Independent EM9305 comparison

The v4.2 standard IHEX/SYM pair at pinned mirror commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54` produced 40 exact named-symbol byte matches, each unique across the full 211,948-byte locked EM9305 payload. Thirty-five agree with a canonical boundary and name. Four entries are configuration/data-shaped, and `RF_RfChannel2BleChannel` maps to the canonical `llConvertRfChanToChanIdx` record; no canonical rename is proposed.

Eighteen matches distinguish the historical v4.2 material from authenticated v4.6: seven same-sized bodies differ in bytes and eleven same-name symbols differ in size. The earlier claim that `scan15_4CheckParameters` was absent by name in v4.6 was wrong; it is present at a different size. Conservative Thumb branch and 16-bit PC-relative masking found **zero** additional matches beyond the exact 40. This negative result does not cover relocation records, literal-pool relocation, 32-bit PC-relative forms, or compiler changes. Reproducible script and results: `../em9305-v42-reloc-independent-20261010-daybreak-low/`.

## Historical SDK provenance and configuration

The mirror is a two-commit personal copy, with a verified GitHub commit but no authenticated EM upstream relationship or repository-level license. Twelve selected files are locally retained in ignored vendor-input storage with commit/blob IDs and SHA-256 receipts. Its v4.2 build scripts and headers establish `ccac`/`arac` tool families, ARCv2 EM core4 and narrower `em9305` profiles, ASIC/DI build families, APEX instruction encodings, and historical memory/configuration contracts. They do not identify the exact MetaWare release, options, link script, or source for the standard EM-Core image. See `../em9305-v42-provenance-config-20261010-daybreak/`.

A submodule remains unjustified for this 128 MB unlicensed personal mirror with mostly generated or proprietary bulk and no maintained upstream history. Its small useful subset is pinned by immutable Git identifiers and hashes. No new maintained, licensed upstream source was authenticated in this lane.

## Apollo IAR scatter constraint

The complete authenticated scatter table at `0x0075D3C8..0x0075D410` has five destination contracts, all using absolute addresses and none setting the handler's static-base/r9-relative mode bit. Three compressed stored inputs form a gapless tail ending at the exact image EOF. This excludes candidate outputs that flag any of these five records relative and constrains table ordering and packing. It does not determine the IAR release, full compiler/project options, ICF, or global RWPI choice. The original-byte replay passes; see `../iar-scatter-destination-discriminator-20261010-daybreak/`.

## Current boundary

The 18 v4.2 release discriminators and their function-versus-data classifications are private P2 candidates, not admitted pseudocode. Progress now requires scoped independent canonical review, a new authenticated producer input, a wider EM9305 relocation/semantic model, first-party behavior, resident-ROM evidence, or hardware observations. G2 pseudocode completion and G3–G6 remain closed; nothing here establishes a complete custom-compilable firmware image.
