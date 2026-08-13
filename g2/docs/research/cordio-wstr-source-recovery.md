# Cordio WSF string-helper source recovery

## Outcome

The G2 stock image contains two adjacent functions from Cordio `wstr.c`:
`WStrReverseCpy` and `WStrReverse`. Both have exact Apache-2.0 Packetcraft
definition routes, closed direct/pointer/interior ingress, host-tested source,
and a checksum-verified Lorelei compiler matrix. Together they account for two
functions / 118 authenticated code bytes. They remain production-excluded.

The third upstream API, `WstrnCpy`, is dead-stripped with high confidence.
Every Packetcraft consumer of that function belongs to WDXS, and the separate
EFS/WDXS census proves that family absent. In contrast, the linked reverse
helpers have SEC/ATT/SMP consumers. This partial-TU result positively
corroborates the EFS exclusion.

## Stock map and behavior

| Function | Stock span | Bytes | SHA-256 | Direct `BL` sites |
|---|---:|---:|---|---:|
| `WStrReverseCpy` | `[0x0056D8C4,0x0056D8F0)` | 44 | `249d9f2b…e6b94` | 39 |
| `WStrReverse` | `[0x0056D8F0,0x0056D93A)` | 74 | `dd319dbd…e20a7` | 2 |

The contiguous 118-byte span has SHA-256 `61177a46…cef2`. Both are leaf
functions: no callees, globals, literals, locks, or indirect calls. Whole-image
scans find no stored even/Thumb entry or interior pointers and no external
interior branch. All external direct branches land on one of the two entries.

`WStrReverseCpy(dst, src, uint16_t len)` uses a signed 16-bit loop counter and
writes `dst[len-1-i] = src[i]` byte by byte. Copy order is observable for
overlap and is preserved. `WStrReverse(buf, uint8_t len)` swaps the outer byte
pairs through `floor(len/2)`; lengths zero/one are no-ops and an odd center
byte is untouched.

## Upstream identity and licensing

Packetcraft r19.02 commit
`86372d84ef0386d8834ed036e613c8f2ded1ff16`, source blob
`581cf30505aa65b690e558628ea2647b12d1cab0`, and r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, blob
`26db5a8e893cdd8a9f6400f769f13cebeb0141a9`, contain byte-identical
Apache-2.0 definitions for both functions. This is the maintained public
source route. The definitions do not distinguish r19.02 from r20.05c.

AmbiqSuite R2.5.1 contains the same three definitions in source SHA-256
`7b226d9e…6452`, Git blob
`b9c68bda8d046e5f5c0ff7e513756532002a379e`; its header is SHA-256
`dadd6ccf…cd3`, blob `e0febd1b339a359739e48e969d9bf984fd13f41d`.
Those files carry ARM confidential/proprietary terms and are identity oracles
only. They are byte-identical in Ambiq R2.4.2 through at least R4.4.1, so this
module also cannot select an Ambiq point release. No proprietary text is
copied into the repository candidate.

## Lorelei matrix and candidate

Lorelei compiled 13 profiles × two linked functions = 26 comparisons in
2.152592560 seconds. Every module and closure had zero undefined symbols.
There were zero raw and zero strict-normalized matches. `-O1` was the best
common GCC lane: 38 bytes versus stock 44 for reverse-copy, 70 versus stock 74
for in-place reverse, for ten bytes of aggregate absolute size difference.
The remaining shape delta is consistent with GCC/IAR instruction selection
and is not treated as a match.

The artifact is
`research/readiness/wstr/`, 12,605 bytes,
SHA-256 `20ed13bb…f253`; its 20 inner checks cover the full matrix, exact source
identity, call census, closure, and timing without proprietary source, stock
bytes, objects, ELFs, or disassembly.

`components/shared/cordio/runtime_cordio_wstr_candidate.c/.h` exposes only
the two linked definitions. Focused host tests cover zero, one, odd, and even
length behavior and an ARM freestanding `-Werror` compile gate. The candidate
is absent from all production inputs pending exact IAR placement/relocations
and target validation.

## Reproduce

```sh
python3 tools/analyze_g2_cordio_wstr.py --json
python3 -m unittest -v \
  tests/test_analyze_g2_cordio_wstr.py \
  tests/test_runtime_cordio_wstr_candidate.py \
  tests/test_verify_research_corpus.py
```
