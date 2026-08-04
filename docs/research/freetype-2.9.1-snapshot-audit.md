# FreeType 2.9.1 authenticated snapshot audit

**Status:** authenticated source snapshot; deliberately excluded from production

This audit authenticates the official FreeType 2.9.1 snapshot selected by
openCFW as a compatibility baseline for the FreeType family found in the Even
Realities G2 `2.2.6.10` image.  It does not prove that Even used commit
`86bc8a95056c97a810986434a3f268cbe67f2902` unchanged, does not claim that the
complete G2 FreeType build configuration has been recovered, and does not
authorize a production overlay.

## Official release identity

The authoritative repository is
`https://gitlab.freedesktop.org/freetype/freetype.git`.  On 2026-07-31, an
exact ref query returned:

```text
ad55868d889b6ba8d2aed846b4b4b460f8a83e42  refs/tags/VER-2-9-1
86bc8a95056c97a810986434a3f268cbe67f2902  refs/tags/VER-2-9-1^{}
```

The first object is an annotated tag, not a lightweight tag.  Its 308-byte
payload is retained byte-for-byte as `third_party/freetype/upstream/VER-2-9-1.tag`:

- Git tag object: `ad55868d889b6ba8d2aed846b4b4b460f8a83e42`
- payload SHA-256:
  `63e19c1cbd64f317780b1d283129c27bd7ba936dcda7e34225e57dda95a32972`
- target: commit `86bc8a95056c97a810986434a3f268cbe67f2902`
- OpenPGP signature issuer key ID: `C1A60EACE707FDA5`

The exact 1,263-byte commit payload is also retained.  Reconstructing its Git
object header produces commit
`86bc8a95056c97a810986434a3f268cbe67f2902`; the payload names tree
`34694611454c8e95bd398d54da805ffb4e94577b` and parent
`ac97a29653e2a551064705891bc578c53ecf056d`.

The signature bytes are part of the authenticated tag payload.  A clean GnuPG
keyring reported `NO_PUBKEY C1A60EACE707FDA5`, and no public key is vendored.
Consequently this audit records that a signature is present but does **not**
claim independent signer-trust validation.  Authentication rests on the
official repository/ref lookup, exact object identities, raw object payloads,
and per-file blob identities.

## Snapshot boundary

The snapshot contains 297 official upstream files:

- all 92 headers under `include/`;
- all 204 `.c`/`.h` files in `src/autofit`, `src/base`, `src/cff`, `src/psaux`,
  `src/pshinter`, `src/psnames`, `src/sfnt`, `src/smooth`, and
  `src/truetype`; and
- unchanged upstream `docs/FTL.TXT`, stored locally as `LICENSE`.

`LICENSE` is 6,743 bytes, Git blob
`c406d150fa57aaf7a5b950b6cf302daeba1d0bb9`, SHA-256
`08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1`.
Only the local filename differs from upstream.

Every file is recorded in `PROVENANCE.json` with local path, upstream path,
Git mode, byte count, Git blob SHA-1, and SHA-256.  The canonical 297-record
array has SHA-256
`62e233bc18e6ada5974c98d65dfc4faaf15058e39edbc435662337d60549ec32`.
All 297 local blob identities match the selected release tree.  Thirty
upstream Jamfiles, `module.mk`/`rules.mk` files, generator inputs, and
`ftver.rc` are explicitly enumerated as outside this bounded source selection;
none is silently implied to be present.

The 2.9.1 version macros are pinned directly in `include/freetype/freetype.h`.
This agrees with the independently recovered `2`, `9`, and `1` stores in the
G2 `FT_New_Library` implementation.

## Recovered G2 module configuration

The pristine upstream `include/freetype/config/ftmodule.h` remains unmodified.
The clean G2-specific module boundary is instead stored at
`third_party/freetype/g2-config/freetype/config/ftmodule.h`.  It reproduces the
ten pointers in the G2 `ft_default_modules[]` table at run `0x0073EEF8`, in
order:

1. `autofit_module_class` (`autofitter`)
2. `tt_driver_class` (`truetype`)
3. `cff_driver_class` (`cff`)
4. `psaux_module_class` (`psaux`)
5. `psnames_module_class` (`psnames`)
6. `pshinter_module_class` (`pshinter`)
7. `sfnt_module_class` (`sfnt`)
8. `ft_smooth_renderer_class` (`smooth`)
9. `ft_smooth_lcd_renderer_class` (`smooth-lcd`)
10. `ft_smooth_lcdv_renderer_class` (`smooth-lcdv`)

The stock table terminates with NULL at `0x0073EF20`.  When the official image
is available, the offline verifier re-reads every table pointer, each class's
flags and object size, and its module-name pointer.  The recovered header is
876 bytes with SHA-256
`522c1d358dce8a141b2f8afec7020f66bf800d3d829a1ad22f3418ebf3f05d74`.

## Recovered configuration tranche

The production-excluded focused audit
`tools/freetype_g2_config_audit.py` now authenticates a bounded subset of the
G2 configuration directly from the official image:

- the TrueType default is interpreter version **40**, with minimal subpixel
  hinting only (`TT_CONFIG_OPTION_SUBPIXEL_HINTING == 2`); versions 35 and 40
  are accepted by the property setter and the v38/Infinality branch is absent;
- `TT_CONFIG_OPTION_GX_VAR_SUPPORT`,
  `TT_CONFIG_OPTION_EMBEDDED_BITMAPS`, the bytecode interpreter, stream
  support, and `AF_CONFIG_OPTION_USE_WARPER` are enabled;
- `FT_CONFIG_OPTION_PIC` and
  `FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES` are disabled;
- `FT_CONFIG_OPTION_INCREMENTAL` is enabled,
  `FT_CONFIG_OPTION_SUBPIXEL_RENDERING` is disabled, and the LCD renderers use
  FreeType's exact three-pass fallback implementation;
- `CFF_CONFIG_OPTION_OLD_ENGINE` is disabled and the CFF driver defaults to
  Adobe hinting;
- `AF_CONFIG_OPTION_CJK` and `AF_CONFIG_OPTION_INDIC` are enabled, proven by
  the exact fallback-style enum rather than generic property strings;
- the GX service is substantive rather than a name-only stub: all eight
  modern multi-master callables and the H/V/M metrics-variation callables are
  non-null in the firmware records;
- `am_ftsystem.c` constructs a 16-byte `FT_Memory` using the firmware heap
  descriptor at `0x20000354` and exact allocate/reallocate/free entry points;
  the exact `FT_Done_Face` body is `0x00526814..0x0052687E`, with the complete
  three-call topology pinned; and
- the font manager registers two external XIP header locations at
  `0x80100000` and `0x80700000`, but their payload bytes and runtime-populated
  FreeType face names are not present in the main image.

The detailed addresses, hashes, qualifications, and mutation test are in
[`freetype-recovery-audit.md`](freetype-recovery-audit.md).

## Explicit non-claims

The following remain unresolved and are not inferred from upstream defaults:

- the complete set of `FT_CONFIG_OPTION_*` overrides beyond the proven subset;
- optional compression-helper configuration;
- an exact stock entry for `FT_Done_FreeType` (the conventional
  `FT_Done_Memory` topology is absent);
- exact IAR version, compiler flags, and linker configuration; and
- identities, hashes, formats, and runtime names of deployed font assets.

Upstream's default `ftoption.h` is preserved only as release source.  It is not
presented as the G2 configuration.  The snapshot, recovered module header, and
all sources remain absent from production overlays, component build scripts,
and firmware manifests.

## Offline gates

`third_party/freetype/verify_snapshot.py` fails closed on:

- ref/tag/commit/tree provenance drift;
- raw tag or commit object drift;
- any per-file path, size, mode, blob SHA-1, or SHA-256 change;
- added or removed snapshot files;
- FTL or version-marker drift;
- recovered module header/order drift;
- stock module table/class metadata drift when the official image is present;
- removal of an unresolved boundary; or
- any production manifest/component reference to FreeType.

Focused tests also copy the complete snapshot and prove rejection after source,
provenance, tag-object, module-header, and subtree-inventory tampering:

```sh
cd openCFW
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_freetype_snapshot
```

Result at integration: 5 tests passed.  No firmware was executed or flashed.

The separate configuration audit pins twenty-one firmware evidence spans and
rejects any official-image drift:

```sh
cd openCFW
PYTHONDONTWRITEBYTECODE=1 python3 tools/freetype_g2_config_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_freetype_g2_config_audit
```

Result at recovery: 7 tests passed.  This does not add a FreeType source or
binary input to any production component or manifest.
