# Compiler/runtime follow-up after PM closure

Read latest owner touch-pdl14-history-layout-2026-10-09/REPORT.md before extending work. ExecuteCallback now matches all228bytes with the independently supported -fdata-sections contract; all eight former residuals have exact candidates. No remaining PM-lowering mismatch is asserted. Independent review/admission remains separate. Older syspm-linkage report is historical and should not be treated as current residual state.

## New exact-release runtime source provenance

Official Arm release-metadata repository acquired read-only into acquisitions/arm-gnu14-release-metadata, branch releases/14.2.rel1, commit `ae6adf750d347d0233418fba02bed493ddf4b31a`. release_notes.md:175–184 identifies GCC ARM/arm-14 revision `a05ea1e5ee0867191bb432a84c055be99dbdbc16`, newlib/newlib-nano `7923059bff6c120c6fb74b63c7553ea345c0a8f3`, binutils `74c7803f0cc8d3d66513b6d6549bff2fbe737a7d`. These revision facts are vendor release metadata, not inferred from generic GCC14.2 tag.

Acquired selected exact-revision source files from gcc-mirror/gcc into acquisitions/gcc-arm14-runtime. Every URL, byte count and SHA256 is in provenance.json, alongside hashes of the official metadata. No downloaded code was run.

- libgcc/config/arm/t-arm:1 binds LIB1ASMSRC to arm/lib1funcs.S.
- libgcc/config/arm/t-elf:21 selects _udivsi3 and _dvmd_tls among assembly functions, directly corresponding to owner matched archive-member names.
- lib1funcs.S:1053–1172 is L_udivsi3 section with EABI aliases and uidivmod wrapper;1055–1083 distinguishes __prefer_thumb__ and __OPTIMIZE_SIZE__, selecting THUMB1_Div_Positive for the non-size Thumb branch. Macro body at914+ and divide-zero paths are retained. This documents a real runtime build distinction; application -Os does not authenticate which prebuilt library multilib branch was selected.
- lib1funcs.S:1459–1476 is L_dvmd_tls, weak __aeabi_idiv0/__aeabi_ldiv0 under __ARM_EABI__, using RET. It is an authentic source candidate for owner matched zero-hook member, not a replacement stub.
- Direct textual includes ieee754-df.S, ieee754-sf.S, bpabi.S, bpabi-v6m.S were acquired to retain source dependencies; config.host retains target-selection rules. Generated build headers, full recipe/configure command and exact source rebuild remain owner inputs, not proven here.

## License provenance

lib1funcs.S and bpabi.S source notices state GPLv3-or-later plus GCC Runtime Library Exception3.1. Exact-revision COPYING3 and COPYING.RUNTIME retained and hashed. This supplies requested license evidence; no blanket licensing/legal conclusion is made. Official Arm EULA.md is separately retained.

## Limits and proposals

This closes source revision/license discovery for the selected libgcc comparator, not runtime source rebuild or byte-equality gate. Target memcpy at0xAA2C remains an explicitly external owner binding; exact newlib revision is identified but memcpy-producing member/source/build has not been authenticated. No repeated PM history/flag sweep conducted. No all-public-source exhaustion claimed.

Proposed optional comparison-only submodule reference: third-party/reference/gcc-arm14-runtime, https://gcc.gnu.org/git/gcc.git, pin a05ea1e5ee0867191bb432a84c055be99dbdbc16. Prefer a sparse/documented acquisition because full GCC checkout is large; selected local files alone are not a registered submodule. Official Arm release metadata can be referenced by its pinned URL without adding a submodule. No .gitmodules or index changes performed.
