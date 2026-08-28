# Apollo `0x5Dxxxx` closure-hop-2 source attribution

Status: research-only, software-only, not production-routed.

The corrected `g2-cordio-ll-sea-census.tsv` classifies 59 functions (5,006
bytes) as `cordio-closure-hop-2`.  That label records graph reachability, not
per-function ownership.  The census method cannot distinguish every code
reference from an address-like data reference.  The authenticated bodies show
that 45 of these functions (1,844 bytes) are instead exact members of the
vendored FreeType Adobe CFF engine.

## Positive identity evidence

The identification is not based on neighbourhood or visual similarity alone:

- `0x005D1D1C` is the exact three-step xorshift body of `cff_random`.
- `0x005D22F2` through `0x005D23BA` preserve the ordered `CF2_ArrStack`
  initializer/finalizer/accessor family, including its 10-element growth chunk,
  32-byte record layout, and bounds-error behavior.
- `0x005D2EA8` through `0x005D3500` preserve the ordered `psft.c` adapter
  family: transform limits, outline callbacks, 1/64 scaling, CFF private-dict
  fields, region buffers, SEAC callbacks, and default/nominal widths.
- `0x005D4AFE`, `0x005D4B14`, and `0x005D4B4C` match the hint-mask initializer,
  validity accessor, and byte reader.
- `0x005D6D98` and `0x005D6DB8` match the bounded CF2 byte reader and end test;
  the stock error `0x55` is FreeType `Invalid_Stream_Operation`.
- `0x005D6DCA` through `0x005D70A2` preserve every ordered `CF2_Stack` routine,
  including 8-byte typed values and errors `0x82`, `0xA0`, and `0xA1` for stack
  overflow, syntax error, and stack underflow.

The analyzer pins the official image, authenticated Ghidra log, census, and six
vendored upstream source files.  It also verifies retained FreeType/Adobe terms,
source definition order, representative semantic signatures, every stock byte
range, and each research-adapter row.

## Licensing and boundary

The implementation already exists under `g2/third_party/freetype/src/psaux` and
retains the FreeType Project License plus the Adobe patent grant in each source
header.  The new code in `g2/research/candidates/cordio_ll_sea_hop2` is an
Apache-2.0 typed integration adapter only; it does not copy or relicense those
upstream bodies.

The other 14 hop-2 functions (3,162 bytes) remain anonymous, typed external
boundaries.  The adapter rejects them without calling a provider.  It also
rejects unknown addresses, null invocations, missing providers, and provider
failures.  No behavior is fabricated.

## Accounting

This tranche changes the evidence-backed unsupported accounting as follows:

| Partition | Functions | Bytes |
|---|---:|---:|
| Prior unsupported remainder | 288 | 43,446 |
| Exact upstream source recovered | 45 | 1,844 |
| Remaining unsupported | 243 | 41,602 |
| Unselected after closing hop 2 | 229 | 38,440 |
| Selected typed external hop-2 boundary | 14 | 3,162 |

The isolated analyzer is
`g2/tools/analyze_g2_cordio_ll_sea_hop2_candidate.py`; focused host tests are
`g2/tests/test_g2_cordio_ll_sea_hop2_candidate.py`.  Neither file changes the
global census summary, manifests, packaging, overlays, Makefiles, or hardware.
