# Apollo origin-aware byte accounting

## Result

The canonical Apple-profile Apollo component's 3,267,306 builder-owned opaque
base bytes now have a conservative, disjoint origin ledger. The ledger
intersects the flash plan with the authenticated 64-shard Ghidra function map
and 357 retained source paths:

| Opaque-base category | Bytes | Qualification |
|---|---:|---|
| Retained third-party-path function envelopes | 122,876 | Lower-bound family ownership; not a pristine-source claim |
| Retained first-party/project-path function envelopes | 359,684 | Lower-bound project ownership |
| Unanchored discovered functions | 662,584 | Code discovered by Ghidra without a retained-path owner |
| Outside trustworthy function envelopes | 2,122,162 | Mixed data, assets, alignment, missed code, and rejected analyzer artifacts |
| **Total** | **3,267,306** | Exactly reconciles component builder accounting |

The third-party lower bound divides into LVGL 70,362 bytes, Cordio 37,720,
littlefs 11,700, TinyFrame 1,568, TLSF 1,456, EasyLogger 70, and Ring-Buffer
zero. Ring-Buffer is zero in this *opaque* ledger because its linked stock
closure has already moved to controlled ownership.

This replaces the former single opaque percentage as a prioritization tool.
It deliberately does not call the 2,122,790-byte residual “data”: that bucket
also includes code missed by path anchoring or rejected from envelope
accounting.

## Flash-plan metadata reconciliation

The package flash plan currently labels 3,270,038 Apollo bytes as
`official_blob`, 2,732 more than the component builder's canonical opaque-base
count. Exact overlap proves that all 2,732 bytes are controlled patch sites or
in-place source leaves. The companion ledger corrects their accounting
classification without changing emitted bytes or flash addresses and fails
closed on the 28 sites.

This is a metadata normalization gap in the hand-partitioned package manifest,
not an executable ownership gap. A later mechanical manifest regeneration can
split those 19 ranges; until then the analyzer proves and records the exact
delta rather than silently reporting incompatible opaque totals.

## Trust boundary

Ghidra reported 7,370 functions. The accounting accepts 7,362 envelopes no
larger than 16,384 bytes and rejects eight obviously anomalous 60,220- to
1,802,238-byte envelopes. None of the rejected entries has a retained source-
path anchor. Overlapping unanchored envelopes never override a retained path:
third-party and first-party anchors are the stronger evidence, and cross-root
anchored bytes remain forbidden.

The machine-readable authority is
`tools/manifests/g2-apollo-origin-accounting.json`; the fail-closed analyzer is
`tools/analyze_g2_apollo_origin_accounting.py`.

```sh
python3 tools/analyze_g2_apollo_origin_accounting.py \
  --flash-plan build/source/flash-plan.json \
  --component-report components/apollo_main/core_overlay/build/build-report.json \
  --ghidra-corpus /var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth
```

The analysis is read-only and performs no signing, flashing, erase, or hardware
operation.
