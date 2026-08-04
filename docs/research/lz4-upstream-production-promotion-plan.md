# Historical authenticated upstream LZ4 production-promotion result

Status: **completed production integration**. This document records the final
result of the former promotion plan. The source profile builds and routes the
active EvenHub mode-2 path through authenticated upstream LZ4 v1.10.0. The
artifact pins below are the LZ4 milestone, superseded by the subsequent
FreeRTOS queue/task closure production tranche; the LZ4 code and topology
remain active.

## Decision and evidence limit

openCFW selects the authenticated LZ4 snapshot at commit
`ebb370ca83af193212df4dcbadcc5d87bc0de2f0` (`v1.10.0`) as its maintained
decompression source. The production closure is deliberately limited to:

- the single `LZ4_decompress_safe` function section compiled from
  `third_party/lz4/lz4.c`;
- the 64-byte read-only `inc32table` and `dec64table` closure;
- the four-byte G2 ABI tail adapter from
  `components/apollo_main/core_overlay/evenhub_lz4_upstream_adapter.c`; and
- the 30-byte source-owned EvenHub mode-2 adapter from the same file.

No compressor, frame API, writable LZ4 state, or other public LZ4 function is
linked. This source selection is not a claim that the official G2 image
contains LZ4 v1.10.0. The stripped stock decoder is compatible with the
material v1.9.4 and v1.10.0 family evidence; the exact stock point release
remains unresolved.

## Authenticated stock boundary and reachability result

All addresses use the Apollo application run mapping from the 32-byte-preamble
official image, base `0x00438000`.

| Boundary | Complete stock span | Bytes | SHA-256 / result |
|---|---:|---:|---|
| EvenHub mode-2 entry | `[0x004E0C0C,0x004E0C34)` | 40 | `c97a5644f2451934f190a189006304f2a01f8b732fa5dd08711a2cc8272e5fc2`; three direct callers |
| LZ4 variable-length reader | `[0x0054EE90,0x0054EF08)` | 120 | `ac7afc67dfe6e35d5ccf23ba3e232439b75084fb80ae8b997674c0e473412a55`; reachable only through stock generic before retargeting |
| Stock generic decoder | `[0x0054EF08,0x0054F338)` | 1,072 | `8d8e6a9598ea565a6ca9b7fa1a41a67a2b1756b8fb43e84e684ed5b11de990ae`; sole external route was the safe-wrapper call |
| Stock safe wrapper | `[0x0054F338,0x0054F356)` | 30 | `d824bb067efb6bac662409f00f466631da69272c25c9bea6134c658e713eaef1`; sole direct caller was mode-2 |

Production redirects the complete mode-2 stock entry to the appended mode-2
leaf and the complete safe-wrapper stock entry to the appended safe adapter.
The active path therefore retains the established null/zero guards, argument
reordering, and `result < 1 ? 0 : result` mapping while calling upstream
`LZ4_decompress_safe`.

The production gate decoded the entire official application at every
halfword for direct Thumb branches and scanned every byte offset for even and
Thumb pointer encodings. It found no valid external branch to an interior and
no stored pointer to the safe, generic, reader, mode-2, or memory-provider
entries. Two raw narrow-branch matches and eight raw generic-interior pointer
matches were classified as second-halfword, aligned-data, or instruction-byte
false positives. Retargeting safe therefore cuts the only route to the stock
generic decoder and its reader. Complete caller sets, digests, and
classifications are recorded in
`lz4-stock-reachability-memory-provider-audit.md`.

## Retained unreachable compatibility sections

The first promotion intentionally did not compact existing primary-overlay
code. The hand decoder and its primary mode-2 caller were renamed to
`open_cfw_lz4_decompress_safe_legacy` and
`open_cfw_evenhub_mode2_decompress_legacy`. They keep their established
profile-specific positions and are unreachable:

| Legacy section | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Primary mode-2 caller | `[0x007973E8,0x00797406)`, 30 bytes | retained at its existing profile-specific position, 30 bytes |
| Hand decoder | `[0x00797408,0x007976C0)`, 696 bytes | retained at its existing profile-specific position, 650 bytes |

The official generic decoder and reader also remain as unreachable opaque
compatibility bytes. This choice leaves every later primary function at its
previous address. Removing either dead source section or either stock body is
a future compaction tranche, not part of this integrated promotion.

## Compiler and closure results

Both reviewed profiles compile pristine upstream with `LZ4_FREESTANDING=1`
and the pinned Thumb Cortex-M55, `-O2`, freestanding, sectioning, ROPI,
no-jump-table, no-unwind, no-unaligned-access, and no-machine-outliner
contracts. Section extraction rejects every unlisted code/data section,
writable allocation, symbol, relocation, size, alignment, or hash.

| Contract | Apple clang 21 | Exact-root Linux clang 22.1.8 |
|---|---|---|
| Decoder section | `.text.unlikely.LZ4_decompress_safe`, 1,660 bytes, align 4 | `.text.LZ4_decompress_safe`, 1,690 bytes, align 4 |
| Unrelocated text SHA-256 | `3bb106d1a943c19f0c3f6e2252ae1fbb2bbb78a8a69772e4729a15596bc9da49` | `6d7e83dea96cf39e7ff5d65a1f66116ced40d3f952d2b2074913fd97fd0a916b` |
| Relocated text SHA-256 | `a7e5690af5e74e5395a51a716c9ebde2ee692dcf38decbf92141a3be261d358e` | `632ad34cdf299a714e4d81b7f2ba55e4edb1ac897ff65744622ab29b914bc542` |
| Tables | 64 bytes, align 4, SHA `361b3c2a85717050294fd9e3c6440690de35c0a9455d50e487ea8f0881c40f03` | identical |
| Decoder-plus-table closure | 1,724 bytes, SHA `dc4a643ed862582b1cde268c894f74c51adabf9c242620179f5a6e4f3601cddf` | 1,756 bytes including two alignment bytes, SHA `499387fe05f3c3676375779ede3138e09efea4617efaf5b1a9ff68a3cd5efd62` |
| Relocated safe adapter | 4 bytes, SHA `589f67fc5b672f2be0809e999e8168708b11b90452088fb401a8d76d604959f5` | 4 bytes, SHA `b30709dd4480368a7662bc4ec880846e7d74cb1da1386d4bbad8240d447894c2` |
| Relocated mode-2 adapter | 30 bytes, SHA `577501eac08ce8028c0262f19c84864439e11378314bc9f2874bd8acc77729b6` | identical |

The memory relocations resolve as follows:

- Apple: `+0xF4 -> __aeabi_memcpy`, `+0x636 -> __aeabi_memmove`, and
  `R_ARM_REL32` table references at `+0x674/+0x678`.
- Linux: `+0x1C2 -> __aeabi_memcpy`, `+0x652 -> __aeabi_memmove`, and
  MOVW/MOVT PREL table pairs at `+0x41A/+0x41E` and `+0x442/+0x446`.
- Both safe adapters have one `R_ARM_THM_JUMP24 -> LZ4_decompress_safe` at
  `+0x0`; both mode-2 adapters have one
  `R_ARM_THM_CALL -> open_cfw_lz4_decompress_safe` at `+0x10`.

The overlay extractor was extended to carry the one named read-only section,
its two local symbols, Apple `R_ARM_REL32` and Linux MOVW/MOVT PREL forms, and
fixed-address external calls. The final reports expose text, alignment,
read-only data, adapters, resolved relocations, and relocated hashes. The
former closure-tooling blocker is resolved; there is no manual post-link
exception.

## Final append layout

| Item | Apple offset / runtime span | Linux offset / runtime span |
|---|---|---|
| Upstream decoder text | `116816 / [0x007B0B74,0x007B11F0)` | `118660 / [0x007B12A8,0x007B1942)` |
| Alignment before tables | none | `120350 / [0x007B1942,0x007B1944)`, 2 bytes |
| `inc32table` | `118476 / [0x007B11F0,0x007B1210)` | `120352 / [0x007B1944,0x007B1964)` |
| `dec64table` | `118508 / [0x007B1210,0x007B1230)` | `120384 / [0x007B1964,0x007B1984)` |
| Safe ABI adapter | `118540 / [0x007B1230,0x007B1234)` | `120416 / [0x007B1984,0x007B1988)` |
| Mode-2 adapter | `118544 / [0x007B1234,0x007B1252)` | `120420 / [0x007B1988,0x007B19A6)` |
| Overlay end | `118574 / 0x007B1252` | `120450 / 0x007B19A6` |

Apple appended exactly 1,758 bytes after the scheduler-cluster baseline;
Linux appended 1,790. Both remain below the `0x007F0000` ceiling.

## Authenticated stock EABI dependencies

The selected upstream object resolves its two memory calls to complete,
hash-pinned stock providers:

| Provider | Complete span | Bytes | SHA-256 |
|---|---:|---:|---|
| `__aeabi_memcpy` | `[0x00439BE4,0x00439C8A)` | 166 | `8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd` |
| `__aeabi_memmove` | `[0x00439710,0x004397A6)` | 150 | `31caf15ad676c4a99eace5673e1fe46b818b64d901707c461074e8acc5474b28` |

Both use the AAPCS EABI void contract `(r0 destination, r1 source, r2 count)`;
the selected decoder consumes no returned destination pointer. `memcpy`
advances `r0` and includes a genuine alternate aligned-copy entry at
`0x00439C04`. `memmove` handles overlap with complete backward byte/word/
halfword paths returning at `0x00439730` or `0x0043976C`; non-overlap,
including zero length, makes a non-linking tail `B.W` from `0x00439718` to
`memcpy`, preserving the original caller's `lr`.

These are explicit opaque dependencies allowed by the binary-blob policy.
They must not be declared as ISO C functions whose return values are usable.
Reviewed source-owned EABI shims remain a later closure improvement.

## Semantic result

The active implementation now follows pristine upstream v1.10.0 behavior.
Valid block output remains byte-equal, while reviewed malformed/edge behavior
differs from the retired hand decoder:

- upstream enforces the final-match `MFLIMIT` rule;
- the upstream safe path accepts the tested malformed zero-offset block that
  the hand decoder rejected;
- specific negative error positions differ, so callers may rely only on
  “negative means failure”; and
- the EvenHub adapter continues converting every non-positive result to zero.

Regression coverage pins valid blocks, empty blocks, extended literals and
matches, overlap, `MFLIMIT`, zero offset, truncation, length overflow,
guard-byte preservation, output bounds, and representative negative results.

## Final artifact and accounting results

| Artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Overlay | 118,574 bytes / `1a0b92e12203b78f48191969744128bfbcc2559c811ae40a1f393370eceacea9` | 120,450 bytes / `2901320d6169c2b9ad49d501cb25e7f50ceaa90b94e7d0640f80d318932d8fc7` |
| Apollo-main component | 3,641,970 bytes / `6621c7d0403e37d0598c5f2f521633afb13b98034542c8010cf9d210f576e91d` | 3,643,846 bytes / `140cac71e8ec612f2129800ee9a205c30f743dfd51664207c1661fdb337d8f8d` |
| Core-source package | 4,420,424 bytes / `d576be2c4626006a830593a5ad1aae21da8ee3e16d67d80c62eb8f3994bfc294` | 4,422,300 bytes / `cb1516c2c61402626a723f05f4fb315e8af91adae599818830b2f8e1ffee0bf8` |

| Accounting | Apple | Linux |
|---|---:|---:|
| Component source-owned | 118,756 | 120,632 |
| Component generated patch-site | 82,478 | 82,644 |
| Component replaced-stock | 82,660 | 82,826 |
| Component opaque base | 3,440,704 | 3,440,538 |
| Component wrapper | 32 | 32 |
| Package source | 119,370 | 121,291 |
| Package generated | 84,277 | 84,232 |
| Package opaque | 4,216,777 | 4,216,777 |

No new stock span was added to generated/replaced ownership: the 30-byte safe
entry and 40-byte mode-2 entry were already generated replacements. Source
coverage grows through the appended active closure. The two stock EABI
providers and unreachable compatibility bodies remain explicitly opaque.

## Completed gates and safety boundary

The integrated result satisfies the former promotion blockers:

- the vendored source, header, license, provenance, commit, and tree are
  authenticated by `third_party/lz4/verify_snapshot.py`;
- the official-image boundary, caller, interior-target, stored-pointer, and
  complete provider/ABI audits pass;
- closure-aware read-only-data extraction and all Apple/Linux relocation forms
  are implemented and fail closed;
- both toolchain profiles have exact decoder, table, adapter, overlay,
  component, and package pins;
- active adapters replace both public stock entries without shifting existing
  primary functions;
- no writable LZ4 section, compressor symbol, unlisted relocation, unresolved
  symbol, overlap, or ceiling violation is accepted; and
- focused semantic, adapter, closure, placement, manifest, accounting, and
  package verification cover the integrated path.

This result establishes reproducible structural and host-test evidence. It
does not authorize device writes and is not evidence of physical G2 execution.
No hardware was flashed, reset, or executed during the promotion.
