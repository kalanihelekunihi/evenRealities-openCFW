# Codec image-A XIP fixed-address link eligibility

`audit_xip_link_eligibility.py` joins the retained native function
catalogue, explicit source-binding census, and current coherent
230-input Codec candidate (`codec-placement-gated-round`, SHA-256
`4bf4688c38c3f7f4c2ce5629283f357203b050f8b60ca5f5ccd8913cb949e934`).
The reproducible `xip-link-eligibility-manifest.json` records every
native body range, next fixed native entry, source candidate, exact
target ELF function/section size, and each section relocation and
target. It also carries all 267 between-function native gap ranges
(2,332 bytes) from the separately hashed stock range audit.

For the 339 retained labels before the XIP data tail at `0x1020a8aa`:

- 198 have a direct native-address-named symbol whose entire compiled
  section fits before the next native label. This is only a necessary
  size condition; no section has been admitted to final placement.
- 113 direct symbols have sections larger than their fixed native slots,
  totaling 1,910 bytes of individual overlap. Fifty-four named
  function bodies alone exceed their slots. The largest current
  overflows are `0x10206a84` formatter (+164 bytes), `0x10207070`
  audio input/output (+150), and `0x10208098` UART receive callback
  (+116). Reaching those original entry addresses while retaining
  following native entries requires a producing-code size change,
  trampolines/new address map, or other proved relocation strategy.
- 28 labels lack a direct address-suffix symbol. Twenty-seven have an
  explicit candidate source binding, often a generic provider or pinned
  library body with a different symbol. One (`0x10209c74`) is the
  previously demonstrated interior fallthrough label in unsigned
  division, not an independent native function. The 27 source
  bindings need final ABI/alias symbol decisions; they are not a claim
  of 27 absent algorithms.

The 311 directly named compiled sections carry 854 target relocations.
Their targets, kinds and section offsets are in the manifest; none has
been range-qualified under a final map. The post-code XIP data tail
has 23 raw Ghidra labels separately attributed to literals/tables.
Exact string/table section placement and the 267 in-code literal/case
gaps remain distinct from these function slots. A fixed-address linker
script for the full XIP span would overlap at the 113 recorded slots;
this audit therefore does not emit a false full-image link.

An isolated target `-Os` sweep recompiled all 73 component source files
contributing to those 113 overflowing sections. Plain `-Os` would
clear 53 slots but create five new overflows in two source files.
`xip-os-qualified-sources.json` selects 35 files with 51 cleared slots
and no newly overflowing native-bound section in those files. The
Codec builder applies `-Os` only when a selected source hash matches
its target probe; otherwise it retains `-O2` and reports stale
evidence. The integrated image-A candidate SHA-256
`0acb19d7692096fccd3ef719de0e12c4a6cacd5c0f116eb404143dd833eede9e`
has a fresh `xip-link-eligibility-os-manifest.json`: 249 section-size
eligible, 62 still overflowing, 28 without direct native suffix
symbols, and 1,150 total bytes of individual fixed-slot overflow.
Its named sections have 860 relocations. This is a measured layout
improvement and still not a complete original-address link.

`image_a_known_data.ld` remains the isolated, passing vector/initialized
tail/BSS placement check. Full Codec image-A source closure still
requires an authenticated callable address strategy, relocation and
literal-pool placement, loader/runtime alias semantics, and the three
genuine FP/ambient KWS imports.
