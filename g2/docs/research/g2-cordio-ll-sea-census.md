# G2 Cordio link-layer-island census of the 0x5Dxxxx sea

Status: authenticated call-topology triage map for the `0x5Dxxxx`
no-evidence sea of official G2 `2.2.6.10` Apollo-main.
Analysis mode: read-only; no signing, flashing, erase, or hardware operation.

## Result

The [Apollo unanchored-function provenance census](g2-apollo-unanchored-census.md)
leaves 300 no-evidence functions (52,866 official opaque bytes) in the
`0x5Dxxxx` region, initially hypothesized as "LVGL vendor-fork draw/Nema
internals".  The [LVGL vendor-fork census](g2-lvgl-vendor-fork-census.md)
actively contradicted that hypothesis: the sea's only external callers are
Cordio — the anchored `dm_conn.c` function at `0x005D2BAE` (8 call edges) and
the medium-confidence Cordio function at `0x005D2E0C` (4 edges) — and no LVGL
or Ambiq-backend function calls in.  This census attributes the sea inward
from those two anchored Cordio seeds through the closed call graph:

- **102 functions (19,222 official bytes)** form the `cordio-ll-island`
  bucket — the directed call-graph closure of the two seeds inside the sea:
  12 at medium confidence (the direct seed callees) and 90 at low confidence
  (one caller-side member and the hop-2/3/4 closure).
- **198 functions (33,644 bytes)** stay explicitly `investigation-required`
  with deterministic per-function hypotheses: 6 have external callers (all in
  the no-evidence `0x5C`/`0x5E`/`0x5F` functions), 5 are caller-side
  neighbours of the closure through undirected intra-sea components, and 192
  have no static caller in the corpus at all (function-pointer/table
  dispatch or dead-stripped candidates).

The vendored Packetcraft r20.05c snapshot (`third_party/cordio`) contains
**no link-layer/controller sources** — the five vendored translation units
(`atts_csf.c`, `dm_conn_sm.c`, `smp_db.c`, `app_db.c`, `wsf_buf.c`) are
host/profile/WSF oracles and the tree closure covers only the 41 selected
paths — so per-module attribution to public Packetcraft `lhci`/`lmgr`/`ctrl`
or `sec` units is not defensible offline.  The island is bucketed as a
**vendor link-layer cluster adjacent to the anchored `dm_conn.c` island**;
per-function source ownership requires unavailable vendor controller source.

Scope, seeds, closure, and every cross-check are re-derived on every run from
the authenticated image, the authenticated 64-shard Ghidra corpus, the
checked-in parent and LVGL census manifests, and the vendored Cordio headers
— nothing is hardcoded from this report.  The analyzer fails closed on any
drift in the 5,610-row parent manifest, the 1,484-row LVGL manifest, the
300/52,866 sea, the seed sets, the hop census, the evidence census, the
sea-level external topology, or the vendored HCI opcode cross-check.

## Method

Every sea function gets exactly one bucket (`cordio-ll-island` or
`investigation-required`), one evidence class, and one confidence level.
Evidence tiers are evaluated in strict priority order:

| Tier | Evidence class | Confidence | Basis |
|---|---|---|---|
| 1 | `cordio-anchor-callee` | medium | direct static callee of the anchored `dm_conn.c` function `0x005D2BAE` |
| 2 | `cordio-medium-callee` | medium | direct static callee of the medium-confidence Cordio function `0x005D2E0C` |
| 3 | `cordio-island-caller` | low | statically calls one of the two seeds (caller-side evidence) |
| 4 | `cordio-closure-hop-N` | low | reachable from tiers 1–3 at call-graph hop N (2–4) through sea-internal edges |
| 5 | `none` | none | no directed call path from the seeds; deterministic hypothesis recorded |

Seeds are authenticated on every run: `0x005D2BAE` must remain the only
Cordio-path-anchored function in `0x5C0000`–`0x5FFFFF` (path
`third_party\cordio\ble-host\sources\stack\dm\dm_conn.c`, string evidence),
and `0x005D2E0C` must remain the parent census's `cordio` /
`call-topology-single-family` / medium row.  Closure hops propagate only
through directed static call edges that stay inside the sea; labels never
feed other analyses.

Confidence semantics mirror the parent census: **medium** is a single-family
structural inference from an authenticated seed; **low** is a closure or
caller-side hypothesis — useful for queue ordering, never proof of ownership.

## Bucket census

| Bucket | Evidence | Functions | Official bytes |
|---|---|---:|---:|
| cordio-ll-island | `cordio-anchor-callee` (medium) | 8 | 1,492 |
| cordio-ll-island | `cordio-medium-callee` (medium) | 4 | 7,928 |
| cordio-ll-island | `cordio-island-caller` (low) | 1 | 448 |
| cordio-ll-island | `cordio-closure-hop-2` (low) | 59 | 5,006 |
| cordio-ll-island | `cordio-closure-hop-3` (low) | 22 | 3,400 |
| cordio-ll-island | `cordio-closure-hop-4` (low) | 8 | 948 |
| **cordio-ll-island subtotal** | | **102** | **19,222** |
| investigation-required | `none` | 198 | 33,644 |
| **Total** | | **300** | **52,866** |

Closure hop census: hop 1 = 13 (8 + 4 + 1), hop 2 = 59, hop 3 = 22,
hop 4 = 8.

## The cordio-ll-island cluster

The island is the vendor link-layer cluster hanging off the anchored
`dm_conn.c` island:

- The anchored `dm_conn.c` function `0x005D2BAE` computes connection-event
  timing in 16.16 fixed point (constants `0x3E80000` = 10⁶·2¹⁶/10³-scaled
  microseconds, `0x999A` ≈ 0.6, sleep-clock margin arithmetic) against a large
  link-layer context structure (offsets `0x214`/`0x218`/`0x224`/`0x22C`/
  `0x230`).  Its eight sea callees are the cluster's public surface:
  `0x005D2418` (1,014-byte connection-event scheduler), `0x005D2A18`
  (fixed-point timing distribution), and six small context accessors
  (`0x005D3238`–`0x005D327E`).
- The medium seed `0x005D2E0C` is the connection-establishment wrapper; its
  four sea callees include the sea's largest member `0x005D4ED0` (7,880
  envelope bytes, multi-KB stack frames), called only from within the island.
- The single caller-side member `0x005D3068` allocates a 0x228-byte link
  control block, copies connection parameters, and calls `0x005D2E0C`; it has
  no static caller itself (function-pointer dispatched).
- The closure's external callees are only the medium seed, one first-party
  utility (`0x0046CACC`), and 17 no-evidence helpers — the IAR
  memset/memcpy family (`0x00439BE4`/`0x00439C04`/`0x0043C0E4`), the
  `0x5244EE`–`0x524F2E` 16.16 fixed-point math cluster (itself no-evidence in
  the parent census's `0x52xxxx` region), and the `0x529148`/`0x52919C`/
  `0x529256` allocate/free helpers.  These stay out of scope; this analyzer
  never re-buckets the parent census.

A development-time comparison against the public Packetcraft r20.05c
`dm_conn.c` (git-hash-authenticated checkout at the pinned commit
`3656312d6b73…`) found no body resembling `0x005D2BAE`: the public file's
connection functions are CCB managers and HCI event actions, not fixed-point
event schedulers.  The G2 `dm_conn.c` translation unit therefore carries
vendor link-layer code absent from the public file — consistent with the
retained path string, not with pristine public source.

## Module-hypothesis cross-checks (negative results, fail-closed)

- **HCI dispatch: rejected.**  The vendored r20.05c `wsf/include/hci_defs.h`
  yields 152 `HCI_OGF_*`/`HCI_OCF_*` defines resolving to 140 distinct
  `HCI_OPCODE_*` values.  No sea body references any of them in a
  comparison or `case` context (0 hits, pinned).  Three storage-parser
  functions (`0x005DD584`, `0x005DD780`, `0x005DD832`) alias opcode values
  `0x200C`–`0x2010` as big-endian field offsets into serialized records —
  documented false positives, excluded by context and pinned as the exact
  alias set.  HCI command processing lives in the already-censused host
  islands, not in the sea.
- **SEC (sec_ccm/sec_aes): no evidence.**  No sea function references
  peripheral registers (`0x4xxxxxxx`) or the vendored `sec_api.h` shapes;
  the G2 AES path is the Ambiq HAL queue documented by the existing
  `smp_main` patch record, outside the sea.
- **Public lhci/lmgr/ctrl: not attributable.**  The vendored snapshot
  excludes controller sources and its tree closure does not cover them, so
  no authenticated public controller oracle exists offline.  No module label
  below `cordio-ll-island` is claimed.

## Investigation-required remainder (198 functions / 33,644 bytes)

Hypotheses are recorded per function in the manifest `detail` column.
Notable sub-clusters (intra-sea undirected components):

| Region | Shape | Hypothesis |
|---|---|---|
| `0x005D008E` component (20 fns / 3,854 B) | called only from `0x005CF9E8`, a TLV record parser in the `0x5Cxxxx` no-evidence region | first-party settings/storage parse helpers |
| `0x005DA1E8`–`0x005DFF5A` tail | big-endian serialized-record parsers (range lists, index walks, string tables) beside the first-party `g2-nvdb-*` manifest functions at `0x005D9ED0`–`0x005DA034`; called from `0x5Exxxx`/`0x5Fxxxx` no-evidence functions | first-party NVDB/storage parsers |
| `0x005D70A4`–`0x005D9462` component (56 fns / 7,696 B) | no static callers; link-adjacent to the closure | unresolved — table-dispatched vendor LL scheduler vs first-party |
| 5 caller-side neighbours (`0x005D188A`/`0x005D18C8`/`0x005D18EE`/`0x005D1958`/`0x005D2F22`) | undirected component members of the closure with no directed path from the seeds | vendor LL helper clones; caller-side only |

## Reconciliation

- Sea: **300 functions / 52,866 official bytes** — exact match with the
  parent census frontier and the LVGL census `sea-0x5d` scope, zero drift;
  largest member `0x005D4ED0` at 7,880 envelope bytes confirmed.
- LVGL census contradiction finding: the 12 sea rows carrying
  `external callers: cordio` are exactly the 8 anchor callees plus the 4
  medium callees, and the single `calls: cordio` row is exactly
  `0x005D3068` — pinned and enforced on every run.
- Bucket totals: 102 attributed (19,222 B) + 198 investigation-required
  (33,644 B) = 300 / 52,866; evidence census sums with no remainder.
- Sea external callers (whole sea): `0x005D2BAE` (anchored), `0x005D2E0C`
  (medium Cordio), and the no-evidence `0x005CF9E8`, `0x005E0002`,
  `0x005E12C8`, `0x005F9FE8` — pinned.  Sea external callees: four
  first-party utilities (`0x0044A43C`, `0x0046CACC`, `0x004751C8`,
  `0x005BF004`), the medium Cordio seed, and 46 no-evidence helpers —
  pinned.  No other provider family touches the sea.

## Public-Packetcraft boundary

The boundary between public-Packetcraft-attributable and
unavailable-vendor-source code **does not move into the sea**: zero of the
300 sea functions match any public Packetcraft module, and the
vendored-header cross-checks actively reject the HCI/SEC module hypotheses.
What moves is the family-level triage: the 102-function island around the
anchored `dm_conn.c` seed is now defensibly triaged as **vendor Cordio
link-layer internals** (needing unavailable vendor controller source for
per-function ownership), replacing the falsified LVGL/Nema hypothesis for
that cluster.  The remaining 198 functions keep their
investigation-required status with sharper hypotheses; in particular the
sea tail looks like first-party storage code, not Cordio, and not LVGL.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_ll_sea_census.py \
  --ghidra-corpus /path/to/full64-j64-auth \
  --write-manifests tools/manifests
```

Machine-readable output:

- `tools/manifests/g2-cordio-ll-sea-census.tsv` — all 300 per-function
  assignments (entry, body range, envelope and official bytes, bucket,
  evidence, confidence, hop, detail).
- `tools/manifests/g2-cordio-ll-sea-census-summary.json` — the seed,
  reconciliation, and evidence-census blocks above.

The fail-closed guard is
[`../../tests/test_analyze_g2_cordio_ll_sea_census.py`](../../tests/test_analyze_g2_cordio_ll_sea_census.py):
24 tests covering evidence-table closure, seed-set disjointness, frozen-census
internal consistency, the vendored-header opcode parser (including header
drift rejection), parent and LVGL manifest loader/schema/mutation rejection,
the exact seed/tier/hop/evidence pins, the sea-level external topology pins,
the HCI opcode negative result and documented alias rows, the island-members
closure invariant, and byte-identical manifest regeneration.

## Limitations

- Bucket membership is call-topology triage for queue ordering, not
  per-function source ownership, behavioral reconstruction, or
  candidate-readiness claims; `low`-confidence closure labels in particular
  are hypotheses.
- The `cordio-ll-island` bucket is a vendor link-layer cluster hypothesis
  anchored on the `dm_conn.c` path-string island; the vendored r20.05c
  snapshot contains no controller/LL sources, so public-Packetcraft
  per-module attribution (`lhci`/`lmgr`/`ctrl`/`sec`) is not defensible
  offline.
- Hop-N closure labels are structural inferences and never feed further
  propagation; the hop-4 frontier is the current evidence limit.
- Call targets are recovered from address tokens in decompiled bodies; data
  references that alias function entries are indistinguishable from calls.
- The HCI opcode cross-check rejects HCI dispatch in the sea only for the
  vendored public opcode inventory; vendor-specific opcodes (OGF `0x3F`)
  are not enumerable from the snapshot.
- Functions with no static caller may be dispatched through data tables the
  decompiler does not resolve; "no static caller" is not proof of dead code.
