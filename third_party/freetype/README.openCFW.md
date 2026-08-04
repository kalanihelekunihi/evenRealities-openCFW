# FreeType 2.9.1 authenticated upstream snapshot

This directory preserves a bounded, byte-exact source selection from the
official FreeType `VER-2-9-1` annotated tag.  The official ref resolves to tag
object `ad55868d889b6ba8d2aed846b4b4b460f8a83e42`, which peels to commit
`86bc8a95056c97a810986434a3f268cbe67f2902` and tree
`34694611454c8e95bd398d54da805ffb4e94577b`.  Exact raw tag and commit payloads
are retained under `upstream/` so the object identities can be recomputed
offline.  The tag contains a PGP signature made with key ID
`C1A60EACE707FDA5`; the signature bytes are authenticated, but signer trust is
not claimed because that public key is not vendored here.

`PROVENANCE.json` records every selected upstream file by upstream path, local
path, Git mode, byte count, Git blob SHA-1, and SHA-256.  `LICENSE` is the
unchanged upstream `docs/FTL.TXT` (6,743 bytes), renamed only to make the chosen
FreeType Project License conspicuous.

The separate `g2-config/freetype/config/ftmodule.h` records the exact ten-entry
G2 module order recovered from `ft_default_modules[]` at run address
`0x0073EEF8`.  It is clean G2 configuration, not pristine upstream source.  It
is not selected by any production component or firmware manifest.

Run the fail-closed verifier without network access:

```sh
python3 openCFW/third_party/freetype/verify_snapshot.py
```

The focused G2 audit now proves the v40 default with minimal TrueType
subpixel hinting, substantive GX variation service depth, incremental loading,
the non-filtered three-pass LCD path, the Adobe-only CFF engine, and the
autofit CJK/Indic guards, plus the `am_ftsystem.c` allocator.  It also
identifies the exact `FT_Done_Face` body
and its three direct callers.  The G2 font-manager contract is recovered as
four entries per display role, each a 12-byte record containing a type, native
font pointer or FreeType face path, pixel size, and style; the runtime record
contents themselves are not present in the main image.  Remaining unknowns
are `FT_CONFIG_OPTION_*` choices outside the proven subset, optional
compression helpers, the exact IAR compiler/linker version and flags, a stock
`FT_Done_FreeType` entry (the normal retained topology is absent), and the
external font payload identities and runtime configuration-array contents.
This snapshot remains deliberately production-excluded; no source build
should select it without explicit source-configuration and promotion review.
