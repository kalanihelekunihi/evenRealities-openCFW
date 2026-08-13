# Cordio common ATT server processor source audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `atts_proc.c` object is bounded at
`[0x0056C550,0x0056CDC0)`, 2,160 bytes, SHA-256
`a68493f93b22a0f86bdc996e803e2f9c293a650fd413004c4959e7d83d1ef890`.
All nine source definitions link and contribute 2,106 code bytes; their
concatenation hashes to
`2e76008ae954f8d7f2bd9e866cee89f035c69ef3278ffb0d2d3e88ee34578e48`.
The remaining 54 bytes are a 12-byte logger-category gap and a 42-byte aligned
literal tail.

Twenty-six direct BL sites reach the UUID, attribute lookup, range lookup, and
permission helpers. The four request processors enter through methods 1, 2,
5, and 16 of the initialized SRAM `attsProcFcnTbl`, not through direct calls.
No stored strict-interior address or BL into an interior survives. Three raw
entry-valued words occur in the compressed initializer stream; method 16 is
reconstructed by back-reference and therefore has no independent raw literal.
Those stream words are not runtime function-pointer cells.

The retained source path begins at `0x006DCA54` and is referenced only at
`0x0056CDA8`. Stock remains cut forward; no production bytes changed.

## Dispatch, behavior, and ABI

The authenticated boot decoder reconstructs these live roots in the 18-entry
table at `0x2000045C`:

| method | live processor |
|---:|---|
| 1 | `attsProcMtuReq` (`0x0056C6FD`) |
| 2 | `attsProcFindInfoReq` (`0x0056C931`) |
| 5 | `attsProcReadReq` (`0x0056CAA9`) |
| 16 | `attsProcReadMultiVarReq` (`0x0056CBCB`) |

The helpers compare native 16/128-bit UUIDs (including 16-to-128 conversion),
walk the handle-sorted attribute groups, locate attributes in bounded ranges,
and enforce read/write, encryption, authentication, key-size, and optional
authorization-callback permissions.

MTU exchange is rejected on an EATT bearer; otherwise it clamps the peer MTU
to the ATT default/local limit and responds on the selected bearer. Find-info
enumerates homogeneous 16- or 128-bit UUID records up to the bearer MTU. Read
uses group or CCC callbacks when required and returns a bounded attribute
value. Read-multiple-variable iterates requested handles and prefixes each
returned value with its length. Error paths use the shared server error and
busy/discovery helpers. `attsCb=0x2006E5F0`; the server CCB's main pointer and
slot are at `+0x10` and `+0x25`.

## Source lineage

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import are byte-identical: Git blob
`455950e73bd19d0a6ee02e5bdfcd86149d0cb1cb`, 18,001 bytes, SHA-256
`b06af2dc72c57bb8742b5fbbf083dfdd2e5187768cb16db693e00463b8fcc502`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. The linked
read-multiple-variable method and EATT MTU feature gate exclude the smaller
r19/AmbiqSuite 2.x source. The file is Apache-2.0; neither public nor later
import commit is claimed as G2's resolved historical generating commit.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_atts_proc.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_proc
```

The next table-owned server tranche is `atts_read.c`, whose seven linked
definitions own five read/discovery method roots and their range helpers.
