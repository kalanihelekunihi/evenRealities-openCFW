# Apollo `0x5Dxxxx` none-group source attribution: batch 5

Status: research-only, software-only, not production-routed.

Batch 5 resolves the next coherent link-order community: seven census
functions / 1,010 bytes from FreeType PSNames.  The first is
`pstables.h:ft_get_adobe_glyph_index`; the remaining six are the
`psmodule.c` Unicode-name parser, extra-glyph checks, Unicode map builder, and
binary-search index/next operations.

Evidence includes the Adobe glyph trie traversal, exact `uniXXXX` and
four-to-six-digit uppercase-hex rules, the `0x80000000` variant bit, ten-entry
extra glyph state tables, shrink-below-half policy, and base-glyph-aware
binary searches.  Both source files, every image body, and the authenticated
decompiler log are pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 121 | 23,800 |
| Exact source recovered in batch 5 | 7 | 1,010 |
| Cumulative none-group source | 84 | 10,854 |
| Typed external remainder | 114 | 22,790 |

The source-ordered `compare_uni_maps` callback occupies 68 bytes at
`0x005D9672`–`0x005D96B6` but is absent from the function census.  It is
content-pinned and reported as an unclaimed typed external; the provider
adapter rejects its address.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains only identity/provider metadata.  No
production component, global census, package, overlay, Makefile, or hardware
path is modified.
