# G2 liblc3 ltpf/bits 0x43xxxx cluster census

Status date: 2026-08-16
Target: official G2 `s200_v2.2.6.10` Apollo-main image
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

The [liblc3 encoder-internals census](g2-liblc3-encoder-internals-census.md)
attributes 41 of the 72 `0x59xxxx`-scope functions to liblc3 v1.1.3 modules
and records, as out-of-scope dispatch observations, that the `ltpf.c` and
`bits.c` cores are linked in the early `0x43xxxx` island — link order does
not group this codec into one range.  This census closes that island cluster
as an additive, self-contained increment:

- **22 of the 26 scope rows (5,108 official bytes)** are attributed to a
  liblc3 module — 7 at high, 5 at medium, and 10 at low confidence.
  `ltpf.c` takes 13 rows (11 corpus functions, 4,094 official bytes);
  `bits.c` takes 9 rows (9 corpus functions, 1,014 official bytes).
- **3 rows (0 official bytes)** are shared compiler-runtime helpers inside
  the call neighborhood, identified but never module-attributed: IAR
  `memmove` 0x00439710, an IAR DLIB `sqrtf` candidate 0x004397A8, and its
  math domain-error helper candidate 0x00439CA4.
- **1 row (10 official bytes)** stays `investigation required`:
  0x004396B8, a 10-byte `x*10+1` leaf whose sole caller is the
  parent-census `spec.c` `lc3_spec_analyze`; no ltpf.c/bits.c evidence.

The scope and every byte total are re-derived from authenticated inputs on
every run: the 197-function island composition, the 6-seed dispatch
sequence, the 7-entry `resample_12k8[]` table, the table census, every
caller set, and the pinned 26-row attribution map are hard-checked, and any
drift raises `CensusError`.  The parent censuses are not modified.

## Method

Scope is derived deterministically in five disjoint partitions:

1. **Seed closure (15).** The forward static-call closure, inside
   `0x438000`–`0x43FFFF`, of the six island callees of `lc3_encode`.
2. **Closure extension (4).** Island functions whose entire corpus caller
   set lies inside the closure union the parent-census liblc3 universe
   (the 41 attributed functions plus `lc3_tns_analyze` 0x0059AA84).
3. **Dispatch table (4).** In-corpus targets of the `resample_12k8[]`
   static pointer table at 0x00439680, referenced by `lc3_ltpf_analyse`'s
   `PTR_FUN` label and byte-verified against the image in `LC3_SRATE`
   enum order (8K, 16K, 24K, 32K, 48K, 48K_HR, 96K_HR).
4. **Dispatch table, non-corpus (2).** Table targets 0x00438400 (16K) and
   0x00438604 (48K/48K_HR), which Ghidra never emitted as functions; the
   Thumb addresses are byte-verified table entries but carry no envelope
   or byte attribution.
5. **Dispatch-table callee (1).** 0x00438BF0, whose caller set is exactly
   the 24K and 96K table entries.

Evidence tiers are then evaluated in strict priority order; every row gets
exactly one status, module, evidence class, and confidence.

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `dispatch-graph-direct` | medium | the five liblc3 seeds: direct static callees of `lc3_encode` at fixed v1.1.3 `lc3.c` `analyze()`/`encode()` source positions |
| 2 | `dispatch-graph-external` | low | the sixth seed, IAR `memmove`: compiler runtime, not liblc3 |
| 3 | `dispatch-table-entry` | high | Thumb pointer in the byte-verified `resample_12k8[]` table at the pinned `LC3_SRATE` slot |
| 4 | `upstream-table-match` | high | literal-pool cells point into a vendored-snapshot C array matched byte-for-byte and private to `ltpf.c` |
| 5 | `dispatch-graph-indirect` | low | reachable only through cluster or parent-census liblc3 functions; full corpus caller set pinned exactly |
| 6 | `caller-family-shared` | low | caller families span non-liblc3 code; shared compiler runtime, never module-attributed |
| 7 | `none` | none | investigation required |

Three independent evidence mechanisms anchor the cluster:

1. **Dispatch-order match, cross-checked with the parent census.** The
   island callees of `lc3_encode` in decompiled order are exactly
   `0x00438FB8, 0x00439710, 0x00439868, 0x00439B12, 0x004396C2,
   0x004399E4` — the parent census's six pinned external-dispatch
   observations (tuple equality is hard-checked against the parent
   analyzer's constants on every run).  The v1.1.3 `lc3.c` source fixes
   the positions: `analyze()` calls `lc3_ltpf_analyse` then `memmove`;
   `encode()` opens with `lc3_setup_bits`, spills the pitch-bit
   `lc3_put_bits` inline to `lc3_put_bits_generic`, calls
   `lc3_ltpf_put_data` at position 7, and ends with `lc3_flush_bits`.
2. **Byte-exact snapshot tables.** Five cluster functions reference
   module-private `ltpf.c` tables through their literal pools: the four
   in-corpus resamplers hit their coefficient matrices
   (`h_8k_12k8_q15`, `h_32k_12k8_q15`, `h_24k_12k8_q15`,
   `h_96k_12k8_q15` — each matching its `LC3_SRATE` table slot), and
   0x00438924 hits the 32-byte `h4_q15` 4-tap phase filter, stored
   in-island at 0x00438BD0.  No other island function holds any
   module-private table hit (set equality hard-checked).
3. **Thumb pointer-table evidence.** The 7-word `resample_12k8[]` table
   at 0x00439680 is read out of the image and every entry must be the
   pinned Thumb address; the label's first target must match slot 0, the
   word past the table must not extend it, and no other corpus function
   may hold a pointer label into the span.

Confidence semantics mirror the parent census: **high** is a
byte-verified classification; **medium** is a structural inference at a
fixed source position; **low** is a candidate name for queue ordering,
never proof of ownership.

## Per-module attribution

Official bytes are the parent census's per-function official-opaque-byte
attribution, summed per module over the 26-row scope.

| Module (snapshot source) | Rows | Corpus functions | Official bytes | High | Medium | Low | Members |
|---|---:|---:|---:|---:|---:|---:|---|
| `ltpf.c` | 13 | 11 | 4,094 | 7 | 2 | 4 | `lc3_ltpf_analyse` (1,710 B), `lc3_ltpf_put_data`, 6 `resample_12k8[]` entries (2 non-corpus), `resample_x192k_12k8` candidate, `interpolate` (h4_q15-pinned), `dot`/`correlate`/`interpolate_corr` candidates |
| `bits.c` | 9 | 9 | 1,014 | 0 | 3 | 6 | `lc3_setup_bits` (862 B), `lc3_flush_bits`, `lc3_put_bits_generic`, `lc3_ac_write_renorm`, `lc3_get_bits_left` candidate, `get_bits_left`/`ac_get_range_bits` candidates, `accu_flush`/`ac_shift` clones |
| **Attributed** | **22** | **20** | **5,108** | **7** | **5** | **10** | |
| shared runtime | 3 | 3 | 0 | | | 3 | IAR `memmove`, `sqrtf` + domain-error helper candidates |
| investigation required | 1 | 1 | 10 | | | | 0x004396B8 |

Attribution notes:

- The five liblc3 seeds' decompiled bodies match the v1.1.3 sources
  shape-for-shape (setup layout with mode-conditional accumulator init,
  the flush padding loop with inlined `ac_terminate`, the generic
  accumulate/flush/re-accumulate slow path, the renorm-over-`ac_shift`
  loop, and the pitch bit + 9-bit pitch-index write).
- `lc3_ac_write_renorm` 0x00439B54 is called by exactly the three
  `lc3_put_symbol` sites: the parent-census `bits.c` clone 0x0059A9C8,
  `lc3_tns_put_data` 0x0059B5C4, and `lc3_spec_encode` 0x0059C204.
- `accu_flush` 0x0043992C is called by exactly `lc3_flush_bits` and
  `lc3_put_bits_generic` — the two source callers in `bits.c`.
- `lc3_get_bits_left` 0x00439914's sole caller is `lc3_spec_encode`
  0x0059C204; its helper 0x004397FA reproduces `get_bits_left`'s
  arithmetic-coder pending-bits accounting (`26 - range_bits +
  ((cache >= 0) + carry_count) * 8`) field-for-field.
- The `sqrtf` candidate 0x004397A8 (SQRT intrinsic with a domain-error
  tail through 0x00439CA4, which stores EDOM `0x21` through
  `DAT_00439CD4`) is called from the ltpf, mdct, sns, and spec analysis
  internals *and* from first-party code — a shared IAR DLIB helper, like
  `memmove`, that no caller topology can attribute to liblc3.

## Reconciliation vs the parent census

| Set | Rows | Official bytes |
|---|---:|---:|
| Parent-census 6 external dispatch observations (0x43xxxx) | 6 | 2,650 |
| — re-bucketed here as liblc3 modules (5 seeds) | 5 | 2,650 |
| — re-bucketed here as shared runtime (IAR `memmove`) | 1 | 0 |
| Cluster scope total | 26 | 5,118 |
| Attributed to `ltpf.c`/`bits.c` | 22 | 5,108 |
| Shared runtime | 3 | 0 |
| Investigation required | 1 | 10 |

All six parent observations are accounted for: five become
`dispatch-graph-direct` module rows at the same addresses with the same
modules the parent hypothesized (`0x00439B12` is named
`lc3_put_bits_generic`, the exact v1.1.3 source name for the parent's
"`lc3_put_bits` slow path"), and `memmove` keeps its non-liblc3
classification.  The two dispatch-authenticated functions the parent
recorded as parent-bucketed `first-party` (`lc3_hr_setup_encoder`
0x0059123A, `lc3_tns_analyze` 0x0059AA84) are **not** in this scope and
are not re-bucketed here, per the parent census's record-only note.

Island composition (197 corpus functions in `0x438000`–`0x43FFFF`):

| Category | Functions |
|---|---:|
| This census's corpus scope (all parent `investigation-required-no-evidence`) | 24 |
| Remaining parent no-evidence rows | 44 |
| Parent `lvgl` bucket | 79 |
| Parent `easylogger` bucket | 7 |
| Parent `first-party` bucket | 5 |
| Path-anchored (owned by linked-provider manifests; not censused by the parent) | 38 |

The rest of the island is triage-level only: the 79 `lvgl`-bucket and 7
`easylogger`-bucket rows are provider-attributed elsewhere; the 38
path-anchored functions carry linked-manifest ownership (the dominant
families are IAR DLIB runtime — memset/memcpy/printf-style cores with
hundreds of callers — and C-library init); the 44 remaining no-evidence
rows include the 0x43A1B0/0x43A698 float cluster called from first-party
0x0055F848 and the 0x43C8D2 stdio family.  None shows ltpf/bits evidence.

Byte check: 5,108 + 0 + 10 = 5,118 = cluster scope total; the 24 claimed
rows leave 68 − 24 = 44 island no-evidence rows, zero drift.

## Reproduction

```sh
python3 tools/analyze_g2_liblc3_ltpf_bits_cluster.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-liblc3-ltpf-bits-cluster-map.tsv` — all 26 rows
  (entry, body range, envelope and official bytes, scope partition,
  parent bucket, status, module, attribution, evidence, confidence,
  detail).
- `tools/manifests/g2-liblc3-ltpf-bits-cluster-summary.json` —
  reconciliation, per-module roll-up, island composition, and
  limitations.

The fail-closed guard is
[`../../tests/test_analyze_g2_liblc3_ltpf_bits_cluster.py`](../../tests/test_analyze_g2_liblc3_ltpf_bits_cluster.py):
corpus-independent unit tests (closed class sets, expectation-table
totality, scope-partition disjointness, arithmetic closure, snapshot-hash
mutation rejection) plus corpus-backed checks (exact reconciliation,
pinned attribution, seed-order/caller-set/table-evidence mutation
rejection, byte-for-byte manifest regeneration).

## Limitations

- Module attribution is evidence-tiered triage, not per-function source
  ownership, behavioral reconstruction, or production-candidate
  readiness.
- `dispatch-graph-direct` module names rest on the fixed v1.1.3 `lc3.c`
  `analyze()`/`encode()` call order; `dispatch-graph-indirect` names are
  candidates corroborated only by caller topology and body shape.
- `upstream-table-match` proves the stock function reads a byte-identical
  snapshot table; it does not prove the whole function body is pristine
  upstream code.
- 0x00438400 (`resample_16k_12k8` slot) and 0x00438604
  (`resample_48k_12k8`, slots 4–5) are byte-verified table entries that
  Ghidra never emitted as functions; they carry no envelope or byte
  attribution.  The neighboring envelopes bound their likely extents
  (0x00438400–0x00438504 and 0x00438604–0x00438770), but that is
  inference, not census data.
- The `ltpf.c` `h4` float table parse truncates at the implicit trailing
  initializers, so the strict unique byte-match fails closed and
  0x00438EF0 (`interpolate_corr` candidate) stays low-confidence even
  though its `DAT_004396B4` pointer lands on `h4` row 0 at 0x006D54D8.
- Several `bits.c` and shared-runtime envelopes report zero official
  opaque bytes under the parent census's ownership accounting (already
  production source-owned); the module attribution is unaffected.
- Ghidra envelope boundaries and partial MVE/Helium decoding
  (`dot`/`correlate` bodies) are analyzer artifacts inherited from the
  corpus.
- Decoder-only liblc3 objects (`lc3_ltpf_synthesize`, `lc3_ltpf_disable`,
  `lc3_ltpf_get_data`, the bits.c read path) are absent from the linked
  encoder surface and are not censused here.
