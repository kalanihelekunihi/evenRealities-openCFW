# G2 NemaVG stroke-cap source candidate

Status: three stock callable bodies identified and represented by maintained,
semantic clean-room C; production routing remains closed.

The authenticated Apollo decompilation contains a symmetric pair at
`0x0051B8F0` (1,664 body bytes) and `0x0051BF7C` (1,636 body bytes). Both call
the same nine vector-command helpers and implement butt/round/square cap
dispatch. The exact public Ambiq Apollo5 Nema archive pinned by
`g2-nemagfx-ambiq-provenance.json` retains DWARF names and declaration lines:
`draw_start_cap` at `nema_vg.c:1853`, `draw_end_cap` at line 1888, and the
inlined coordinator `draw_caps` at line 1924. Stock `draw_caps` is the
3,298-byte body at `0x0051C5EC`; it accesses both cap styles and has the union
of the two endpoint call graphs. The stock context accesses independently
agree: `+0x2E1` is the end-cap style and
`+0x2E0` is the start-cap style.

`runtime_nemavg_stroke_caps_candidate.c` implements the three cap policies as
caller-owned geometry and command-emission callbacks. Round tessellation is
bounded to 94 arc segments, square caps normalize the outward tangent, invalid
styles fail closed with the stock `0x00800000` class, and provider failures are
explicit. Host geometry/error tests and an undefined-symbol-free Cortex-M55
object gate cover the maintained C.

This is not an exact-stock ABI or production-placement claim. The stock Nema
context binding, nine command-provider ABIs, dual compiler placement, live GPU
command semantics, antialiasing, and winding behavior require further proof;
physical validation is blocked by unavailable physical evidence.
