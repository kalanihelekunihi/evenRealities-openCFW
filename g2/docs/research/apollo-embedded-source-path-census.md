# Apollo embedded source-path census

Status: authenticated lower-bound ownership map for official G2 `2.2.6.10`  
Analysis mode: read-only; no signing, flashing, erase, or hardware operation

## Result

The official Apollo-main OTA payload contains 357 unique NUL-terminated C
source paths rooted at:

```text
D:\01_workspace\s200_ap510b_iar_git\
```

The paths divide into 123 `third_party` translation-unit markers and 234
project/first-party markers. All seven retained third-party directory names
were already present in the upstream inventory; this pass found no omitted
third-party family among the embedded `__FILE__` strings.

The analyzer found 712 raw 32-bit pointer cells to those strings. Correlation
against the authenticated 64-shard Lorelei corpus maps 314 paths to 1,760 of
the 7,370 Ghidra-discovered functions. There is no cross-root function in this
map: 530 functions have a `third_party` anchor and 1,230 have an
`app`/`driver`/`framework`/`platform`/`product`/`utils` anchor. The remaining
5,610 discovered functions have no retained-path anchor.

These are function-count facts, not byte-ownership percentages. A retained
path proves at least one compiled translation unit; an absent path does not
prove exclusion, and an anchored function can still contain vendor changes.

## Third-party path and function anchors

| Retained build-tree family | Paths | Anchored paths | Anchored functions | Inventory disposition |
|---|---:|---:|---:|---|
| LVGL `lvgl_v9.3` | 78 | 74 | 344 | Official development interval plus Ambiq/Even fork boundaries already recorded |
| Packetcraft/Ambiq Cordio | 36 | 32 | 114 | r20.05–r20.05c public compatibility interval; exact vendor tree unresolved |
| EasyLogger | 3 | 3 | 8 | 2.2.99-compatible bounded source already selected/integrated in stages |
| littlefs | 2 | 2 | 37 | v2.10.1-equivalent source already pinned/integrated in stages |
| TLSF | 2 | 1 | 19 | v3.1-compatible source already pinned/integrated |
| TinyFrame | 1 | 1 | 7 | Compatible upstream interval and G2 framing delta already recorded |
| AndersKaloer/Ring-Buffer | 1 | 1 | 1 | Exact bounded cluster already production-integrated |
| **Total** | **123** | **114** | **530** | No new embedded-path family |

The baseline map's nine third-party paths without a Ghidra function reference are four LVGL
units (`lv_keyboard.c`, `lv_spinbox.c`, `lv_font_fmt_txt.c`, `lv_arc.c`), four
Cordio units (`l2c_main.c`, `l2c_master.c`, `smpr_act.c`, `wsf_timer.c`), and
`tlsf_init.c`. Their path strings and pointer cells are authenticated, but the
current decompiler text does not consume those cells. The follow-up
[discovery-gap audit](apollo-embedded-source-path-recovery.md) independently
recovers three WSF-timer functions; the other eight remain missed-code
candidates rather than inferred function ownership.

## Project/first-party anchors

| Build-tree root | Paths | Anchored paths | Anchored functions |
|---|---:|---:|---:|
| `platform` | 103 | 92 | 551 |
| `app` | 98 | 81 | 470 |
| `driver` | 20 | 17 | 140 |
| `framework` | 7 | 7 | 62 |
| `product` | 4 | 2 | 6 |
| `utils` | 1 | 1 | 1 |
| `kernel` | 1 | 0 | 0 |
| **Total** | **234** | **200** | **1,230** |

Among the 1,760 path-anchored functions, 69.886364% are project/first-party
and 30.113636% are retained-third-party anchors. Relative to all 7,370
discovered functions, those are 16.689281% and 7.191316%, with 76.119403%
unanchored. These ratios are a triage signal only and must not replace the
exact package byte-ownership ledger.

## Reproduction and authentication

The fail-closed analyzer is
[`../../tools/analyze_apollo_embedded_source_paths.py`](../../tools/analyze_apollo_embedded_source_paths.py).
It authenticates the 3,523,396-byte official OTA payload at SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`,
enforces the closed path/root counts, and optionally authenticates all corpus
members through the canonical `SHA256SUMS` hash
`3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f`.

```sh
python3 tools/analyze_apollo_embedded_source_paths.py \
  --ghidra-corpus /path/to/full64-j64-auth
```

The complete pretty-printed JSON from the current authenticated corpus is
808,013 bytes and hashes to
`1f0521ba33e02954e779944d4ee1c3b04d3f7cd4219e20b62973075ede8288e1`.
It is generated on demand rather than checked in because it repeats all 357
paths and 1,760 function records. The focused guard is
[`../../tests/test_analyze_apollo_embedded_source_paths.py`](../../tests/test_analyze_apollo_embedded_source_paths.py).

## Consequences for the reconstruction queue

1. Use the 530 third-party anchors to seed source/body comparison inside the
   already selected upstream histories, starting with the bounded LVGL and
   Cordio intervals.
2. Treat the 1,230 first-party anchors as naming and module-boundary evidence
   for clean-room recreation, not as upstream matches.
3. Keep the baseline 43 no-decompiler-anchor markers explicit. The follow-up
   audit recovers seven independently witnessed functions across two paths;
   the other 41 paths remain missed-code candidates and are not assigned from
   adjacency alone.
4. Analyze the 5,610 unanchored functions through call topology, constants,
   upstream binary matching, and data/code classification. This set includes
   upstream libraries that do not retain `__FILE__`, compiler runtime, and
   first-party code, so it is not an “original source” count.

This census improves attribution and prioritization without changing any
production bytes or the current exact controlled/opaque package percentages.
