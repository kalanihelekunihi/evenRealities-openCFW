# Ambiq GPU-patch dash-line source-candidate audit

Status: bounded production-excluded clean-room candidate; no production
overlay, release manifest, binary archive, or hardware state is changed.

## Result

`lv_ambiq_dashline_create` is no longer behaviorally opaque. Two independent
compiled forms agree:

| Evidence | Span | Identity |
|---|---:|---|
| Exact AmbiqSuite 5.1.0 GCC section | 144 bytes | SHA-256 `9f465e5e7bc8c95a022a491d937c46f461071479093ad7f7101581c4a902f20b` |
| Stock G2 IAR function | `[0x005FA7C0,0x005FA84A)`, 138 bytes | SHA-256 `aeda115cd2ea2bba4eee91b8510ec396bdb40b94184a16d51bfc86ba12ae70c0` |

The public object's DWARF names original source line 268 and locals
`dash_buffer_size_pixel`, `ratio`, and `w`. The GCC section has seven function
relocations and one `nema_context` relocation. The stock body has the same six
semantic callees, including repeated color/rectangle calls, followed by the
same clip-pop tail.

This is the fourth bounded clean-room candidate among the 11 GPU-patch
exports, and the fourth of six exports directly required by the exact Ambiq
LVGL subtree.

## Recovered algorithm

For texture width `T`, dash width `D`, and gap `G`, the function computes:

```text
dash_pixels = truncate_to_u32((float)D / (float)(D + G) * (float)T)
```

It then emits exactly:

1. temporary clip `(0, 0, T, 1)`;
2. blend `(1, texture, 0xFFFFFFFF, 0xFFFFFFFF)`;
3. input RGBA raster color;
4. filled rectangle `(0, 0, dash_pixels, 1)`;
5. zero raster color;
6. gap rectangle `(dash_pixels, 0, T - dash_pixels, 1)`;
7. clip pop.

The width comes from `nema_context->texs[texid].w`. DWARF fixes `tex_t` at
`0x18`, `nema_context_t` at `0x100`, its texture array at `+0x38`, and
`nema_tex_t` as one byte. Stock loads the context through pointer cell
`0x20074EFC`. OpenCFW's candidate delegates width lookup and the six Nema
effects through an explicit port table, so no private Nema context structure
or binary API is silently embedded in independently authored source.

The candidate deliberately preserves the upstream valid-input behavior. The
public body contains no guard for `D + G == 0` or unsigned addition overflow;
callers must provide a nonzero, non-overflowing period. The focused oracle
covers zero-dash, zero-gap, fractional truncation, exact partitioning, and the
one-byte texture ID.

## Stock topology

The stock IAR body has direct calls at:

| Call site | Target | Recovered role |
|---|---|---|
| `0x005FA7E2` | `0x004B1516` | temporary clip |
| `0x005FA7F0` | `0x00513924` | blend |
| `0x005FA820`, `0x005FA832` | `0x00522A16` | raster color |
| `0x005FA82C`, `0x005FA83E` | `0x00522AE0` | raster rectangle |
| tail `0x005FA846` | `0x004B1548` | clip pop |

The instruction sequence performs unsigned-to-float conversions, one float
division and multiplication, and truncating float-to-unsigned conversion just
like the public GCC body. Compiler-specific register allocation and prologue
bytes differ, so this is semantic/source recovery rather than a false archive
byte-match claim.

## Reproduction and gates

```sh
make ambiq-gpu-patch-accessors-candidate
python3 tools/analyze_g2_nemagfx_ambiq_provenance.py \
  --sdk-root /path/to/AmbiqSuite_v5
```

Seven focused dash-line tests pin effect order and arguments, edge partitions,
texture ABI, complete stock span/call topology/context literal, exact public
section metadata, Cortex-M55 hard-float compilation, relocation-free candidate
body, independent naming, and production exclusion.

Production admission still requires atomic binding to the selected Nema
archive and real context/HAL, concurrency review around temporary clip state,
and Apollo510 rendering validation. The original implementation source, if it
becomes available, should replace inference as the primary oracle.

