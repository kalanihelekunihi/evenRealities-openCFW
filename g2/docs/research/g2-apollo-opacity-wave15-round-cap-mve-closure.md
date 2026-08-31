# Apollo opacity Wave 15: round-cap MVE closure

Status date: 2026-08-28
Target: official G2 `s200_v2.2.6.10` Apollo-main image
Mode: software-only, read-only

> Historical accounting note: later public-DWARF correlation identifies this
> root as NemaVG `draw_start_cap` and its sibling as `draw_end_cap`. They now
> form a reviewed 3,308-byte semantic source candidate, but both stock endpoint
> records remain retained and unpatched because their exact no-argument/global-
> context ABI, MVE/stack construction, and lower helpers are not sufficiently
> recovered. The historical `typed-external-provider-unavailable` label below
> is superseded for readiness by
> [the stroke-cap candidate audit](g2-nemavg-stroke-caps-source-candidate.md);
> it is not a production-routing claim.

## Result

Wave 15 closes the largest post-Wave-14 residual root at `0x0051B8F0` / 1,668
official opaque bytes. Its complete residual-only static closure contains no
additional positive function: all nine targets were typed by Waves 1, 2, 3,
or 6.

The authoritative residual changes from **1,292 functions / 134,476 bytes**
to **1,291 functions / 132,808 bytes**. The next largest root is the paired
sibling at `0x0051BF7C` / 1,640 bytes.

## Call and data closure

An independent Thumb scan finds exactly 20 direct `BL` sites and no wide
non-link branch continuation or register `BLX`. The nine targets are the prior
command-state, record-builder, tessellation, polyline, trigonometric, and
square-root boundaries. Eight Ghidra `func_0x...` expressions in vectorized
blocks have no corresponding branch site and remain zero-byte MVE callother
artifacts.

The two decoded ranges omit one four-byte `180.0f` literal inside the official
envelope. Outside it, `0x0051BF74` is the context-pointer cell already
reconciled by Wave 10, and `0x0051BF78` is the shared `180.0f` literal before
the sibling root. All three direct data labels are covered without adding or
double-counting function bytes.

## Provider boundary

The body is the paired round-cap/fan coordinator adjacent to Wave 10's round
join coordinator. Its behavior family is supported by source order, repeated
control-state fields, and exact helper topology. That does not authenticate an
internal NemaVG symbol. The root is absent from the stock-resolved Nema symbols,
and the available Apollo5 archive uses GCC and is not byte-identical to the IAR
stock image.

At the time of this wave, no maintained implementation source or applicable
license was available in the checked-in evidence. The function was therefore a precise SHA-pinned
`typed-external-provider-unavailable` boundary. No replacement, production
route, or hardware operation is performed.

## Reproduction

```sh
python3 g2/tools/analyze_g2_apollo_opacity_wave15.py --pretty
python3 -m unittest g2.tests.test_analyze_g2_apollo_opacity_wave15
```
