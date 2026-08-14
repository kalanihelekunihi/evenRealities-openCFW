# G2 liblc3 encoder-internals census

Status date: 2026-08-13
Target: official G2 `s200_v2.2.6.10` Apollo-main image
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

The [unanchored-function provenance census](g2-apollo-unanchored-census.md)
buckets 10 functions (1,694 official bytes) as the Google liblc3 v1.1.3-era
encoder through the four authenticated public entries, and lists the
`0x59xxxx` region — 62 no-evidence functions, 17,874 official bytes — as its
#4 follow-up frontier ("liblc3 encoder internals below the 4 public
entries").  This census extends the attribution inward through
`lc3_encode`'s dispatch graph against the admitted byte-authenticated
v1.1.3 snapshot at `third_party/liblc3`:

- **41 of the 72 in-scope functions (16,128 of 19,568 official bytes)** are
  attributed to a liblc3 module — 15 at high, 11 at medium, and 15 at low
  confidence, one of them (`lc3_hr` clone `0x0059B6A0`) attributable only to
  the cluster, not to a compilation unit.
- **31 functions (3,440 official bytes)** remain `investigation required`;
  none shows any liblc3 dispatch-graph or module-table evidence, and their
  caller families point elsewhere (first-party handle/state objects, an
  IAR-style float helper, dead or overlapping envelopes).
- **8 out-of-scope dispatch observations** record where the graph reaches
  functions this census must not re-bucket: the `0x43xxxx` ltpf/bits
  cluster, `lc3_hr_setup_encoder` at `0x0059123A`, and `lc3_tns_analyze` at
  `0x0059AA84` (both parent-bucketed `first-party` at medium confidence).

The scope and every byte total are re-derived from the parent census on
every run: the 62/17,874 frontier and the 10/1,694 liblc3 bucket are
hard-checked, and any drift in the dispatch order, loader table, table
census, caller sets, or the pinned 72-row attribution map raises
`CensusError`.  The parent census is not modified; this is an additive,
self-contained increment.

## Method

Evidence tiers are evaluated in strict priority order; every in-scope
function gets exactly one status, module, evidence class, and confidence.

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `documented-public-entry` | high | the four entries of `g2-liblc3-public-entry-map.tsv` |
| 2 | `documented-internal-tail` | high | named by address in the entry-map qualification text (`lc3_hr_frame_bytes` at `0x00590F68`) |
| 3 | `loader-table-entry` | high | Thumb pointer stored in `lc3_encode`'s static 4-entry `load[]` table at `0x005915CC`, byte-verified against the image |
| 4 | `upstream-table-match` | high | literal-pool cells point (directly or through one indirection) into a vendored-snapshot C array matched byte-for-byte in the image, private to exactly one module |
| 5 | `dispatch-graph-direct` | medium | direct static callee of `lc3_encode` at the fixed v1.1.3 `analyze()`/`encode()` source position |
| 6 | `dispatch-graph-indirect` | low | reachable only through tier-4/5 internals; liblc3-side caller set pinned |
| 7 | `none` | none | investigation required; hypothesis from external caller families |

Three independent evidence mechanisms anchor the graph extension:

1. **Dispatch-order match.** The decompiled `lc3_encode` body makes 18
   direct static calls.  Its in-scope subsequence —
   `0x00598284, 0x00598AB8, 0x00598DEC, 0x00598F14, 0x00599714,
   0x0059AA84, 0x0059BAE4` then `0x00599080, 0x0059C1C4, 0x0059B5C4,
   0x0059A910, 0x0059C204` — matches the v1.1.3 `lc3.c` `analyze()` order
   (attdet, ltpf, memmove, mdct, energy, bwdet, sns, tns, spec) followed
   by the `encode()` order (setup_bits, bwdet_put_bw, spec_put_side,
   tns_put_data, pitch bit, sns_put_data, ltpf_put_data, spec_encode,
   flush_bits) exactly, including the out-of-frontier ltpf/bits callees in
   the `0x43xxxx` cluster.
2. **Byte-exact snapshot tables.** 88 flat scalar C arrays are parsed out
   of the SNAPSHOT.sha256-verified sources; 84 of them match the official
   image byte-for-byte exactly once.  Six in-scope functions reference
   module-private tables through their literal pools: SNS scale-factor
   codebooks (`dct16_m`, `lc3_sns_lfcb`, `lc3_sns_hfcb`), the SNS MPVQ
   offset table, the TNS arithmetic-coding bit tables, and the spectrum
   coding tables (`lc3_spectrum_bits`, `lc3_spectrum_lookup`).
3. **Documented quantization discriminator.** The SNS `FLT_MAX`
   (`0x7F7FFFFF`) literal at `0x0059A9AC` pinned by
   `g2-liblc3-source-boundary.tsv` is re-verified in the image and is
   referenced by the SNS analysis function `0x00599714`, tying the
   table evidence to the documented commit-interval discriminator.

Confidence semantics mirror the parent census: **high** is a documented or
byte-verified classification; **medium** is a structural inference at a
fixed source position; **low** is a candidate name for queue ordering,
never proof of ownership.

## Per-module attribution

Official bytes are the parent census's per-function official-opaque-byte
attribution, summed per module over the 72-function scope.

| Module (snapshot source) | Functions | Official bytes | High | Medium | Low | Members |
|---|---:|---:|---:|---:|---:|---|
| `lc3.c` | 12 | 1,834 | 9 | 0 | 3 | 4 public entries, `lc3_hr_frame_bytes`, 4 `load_*` PCM loaders, `lc3_hr_frame_block_bytes` + `resolve_dt`/`resolve_srate` candidates |
| `sns.c` | 5 | 6,240 | 3 | 1 | 1 | `lc3_sns_analyze` (4,604 B, FLT_MAX pin), `lc3_sns_put_data`, VQ quantize + MPVQ units (table-pinned), `compute_scale_factors` candidate |
| `spec.c` | 9 | 4,180 | 2 | 2 | 5 | `lc3_spec_analyze`, `lc3_spec_put_side`, `lc3_spec_encode` + `compute_nbits` (table-pinned), gain/mode/bit-accounting candidates |
| `mdct.c` | 3 | 2,122 | 0 | 1 | 2 | `lc3_mdct_forward`, FFT-core and MVE vector-scale candidates |
| `tns.c` | 3 | 460 | 1 | 1 | 1 | `lc3_tns_get_nbits` (table-pinned), `lc3_tns_put_data`, quantize/unquantize helper |
| `attdet.c` | 1 | 468 | 0 | 1 | 0 | `lc3_attdet_run` |
| `bwdet.c` | 3 | 414 | 0 | 2 | 1 | `lc3_bwdet_run`, `lc3_bwdet_put_bw`, `lc3_bwdet_get_nbits` candidate |
| `energy.c` | 1 | 270 | 0 | 1 | 0 | `lc3_energy_compute` |
| `bits.c`/`bits.h` | 3 | 128 | 0 | 0 | 3 | two `lc3_put_bits` out-of-line clones (overflow tail-calls the `0x00439B12` slow path), one `lc3_put_symbol` arithmetic-coder clone |
| cluster-only | 1 | 12 | 0 | 0 | 1 | `lc3_hr(sr)` out-of-line clone (`common.h` header inline) |
| **Attributed** | **41** | **16,128** | **15** | **11** | **15** | |
| investigation required | 31 | 3,440 | | | | see below |

`lc3_encode` itself contributes the four-format loader table evidence:
the pointers at `0x005915CC`–`0x005915D8` are `0x00590F85`, `0x00591061`,
`0x0059112F`, `0x005911B1` — exactly the four sandwich-bucket functions, in
`LC3_PCM_FORMAT` enum order (`load_s16`, `load_s24`, `load_s24_3le`,
`load_float`).

## Out-of-scope dispatch observations (8)

The dispatch graph reaches eight functions outside the 72-function scope.
They are recorded for completeness; this census does not re-bucket them.

| Entry | Hypothesis | Parent-census state |
|---|---|---|
| `0x00438FB8` | `lc3_ltpf_analyse` (ltpf.c) | no-evidence (0x43xxxx island) |
| `0x004396C2` | `lc3_ltpf_put_data` (ltpf.c) | no-evidence |
| `0x00439868` | `lc3_setup_bits` (bits.c) | no-evidence |
| `0x00439B12` | `lc3_put_bits` slow path (bits.c) | no-evidence |
| `0x004399E4` | `lc3_flush_bits` (bits.c) | no-evidence |
| `0x00439710` | IAR `memmove` (not liblc3) | no-evidence |
| `0x0059123A` | `lc3_hr_setup_encoder` (documented in the entry-map qualification) | first-party, medium |
| `0x0059AA84` | `lc3_tns_analyze` (2,610 B; sixth analyze()-position callee) | first-party, medium |

The ltpf.c and bits.c cores are linked in the early `0x43xxxx` island, not
in the `0x59xxxx` cluster — link order does not group this codec into one
range.  `0x0059123A` and `0x0059AA84` are parent-census `first-party`
medium-confidence topology assignments that the liblc3 dispatch evidence
contradicts; refining them is a parent-census change and is deliberately
out of scope here.

## Reconciliation

| Set | Functions | Official bytes |
|---|---:|---:|
| Parent-census `0x59xxxx` no-evidence frontier | 62 | 17,874 |
| Parent-census liblc3 bucket | 10 | 1,694 |
| **Scope** | **72** | **19,568** |
| Attributed to a liblc3 module (or cluster) | 41 | 16,128 |
| — of the frontier | 31 | 14,434 |
| — of the bucket | 10 | 1,694 |
| Investigation required (all frontier) | 31 | 3,440 |

Byte check: 16,128 + 3,440 = 19,568 = 17,874 + 1,694, zero drift.

## Remaining investigation-required frontier (31 functions / 3,440 bytes)

None has a liblc3 dispatch-graph edge or a module-table reference:

- **Head cluster** `0x00590104`–`0x00590CF4` (9 functions, 2,146 B):
  handle-validated, slot-indexed state objects (magic guard
  `*handle & 0x1ffffff`, 0x1000-stride slots at `DAT_00590D34`), called
  from first-party `0x0057A4D8`/`0x0057A7E0` or uncalled.  Hypothesis:
  first-party audio/driver service objects linked before the codec.
- **Middle cluster** `0x00597C6C`–`0x00597E54` (10 functions, 508 B):
  mutually-calling small helpers reached only from first-party
  `0x00585A12`–`0x00585A74`.  Hypothesis: first-party.
- **`0x00598074`** (186 B): float exponent-decomposition helper called from
  first-party `0x0058EAC4`.  Hypothesis: IAR DLIB math (`logf`-family).
- **`0x00598134`–`0x0059823C`** (7 functions, 70 official B): six
  envelopes are fully production source-owned (0 official bytes); reached
  from first-party `0x0058FB1C`/`0x0058FB2A` and the uncalled
  `0x00590104`.  Hypothesis: first-party.
- **`0x00598994`** (292 B) and **`0x0059AA06`** (126 B): no static caller.
  Both are near-twins of attributed neighbors (`0x0059898C` MVE vector
  scale; the 6-byte `0x0059AA00` tns helper overlaps `0x0059AA06`'s
  decompiled body).  Hypothesis: dead-stripped twin instantiations or
  Ghidra overlapping-entry artifacts adjacent to mdct/tns internals.
- **`0x0059C7AC`/`0x0059C800`** (112 B): called only from the
  `g2-service-algo` manifest object at `0x005918CC`; peripheral-register
  references.  Hypothesis: first-party/AmbiqSuite service-algo helpers.

## Reproduction

```sh
python3 tools/analyze_g2_liblc3_encoder_internals.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-liblc3-encoder-internals-map.tsv` — all 72 per-function
  rows (entry, body range, envelope and official bytes, scope, parent
  bucket, status, module, attribution, evidence, confidence, detail).
- `tools/manifests/g2-liblc3-encoder-internals-summary.json` — reconciliation,
  per-module roll-up, and the 8 external observations.

The fail-closed guard is
[`../../tests/test_analyze_g2_liblc3_encoder_internals.py`](../../tests/test_analyze_g2_liblc3_encoder_internals.py):
corpus-independent unit tests (rule totality, table parser/grammar,
module-rule disjointness, snapshot-hash mutation rejection, pinned
constants) plus corpus-backed checks (exact reconciliation, pinned
attribution, dispatch-order and loader-table drift rejection, byte-for-byte
manifest regeneration).

## Limitations

- Module attribution is evidence-tiered triage, not per-function source
  ownership, behavioral reconstruction, or production-candidate readiness.
- `dispatch-graph-direct` module names rest on the fixed v1.1.3
  `analyze()`/`encode()` call order; `dispatch-graph-indirect` names are
  candidates corroborated only by caller topology and body shape.
- `upstream-table-match` proves the stock function reads a byte-identical
  snapshot table through its literal pool; it does not prove the whole
  function body is pristine upstream code.
- The snapshot admits v1.1.3 as a reproducible tagged baseline; the linked
  surface cannot distinguish it from its dead-stripped spelling-only
  successor, so module attributions inherit that interval.
- Ghidra envelope boundaries, overlapping-entry splits (`0x0059AA00`/
  `0x0059AA06`), and partially decoded MVE/Helium bodies (`0x0059898C`,
  `0x00598994`) are analyzer artifacts inherited from the corpus.
- Decoder-only liblc3 objects (plc.c, synthesis paths) are absent from the
  linked encoder surface and are not censused here.
