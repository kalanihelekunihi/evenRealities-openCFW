# Ambiq Cordio HCI event-port recovery

Status date: 2026-08-25  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Stock G2 contains 79 of the 80 definitions in Ambiq's `hci_evt.c`. The linked
translation unit occupies `[0x00569D4C,0x0056B7EC)`: 6,816 physical bytes,
including 6,718 bytes of executable bodies and 98 bytes of alignment, inline
literals, logger categories, and the final literal pool. The only source-only
definition is `hciEvtGetStats`.

The closure is unusually strong despite the source being proprietary:

- an 85-entry parser table at `[0x006C910C,0x006C9260)` contains 74 non-null
  Thumb pointers to 69 unique parser bodies;
- the parallel 85-byte callback-size table is at
  `[0x006E3720,0x006E3775)`;
- six report processors and the command-status, command-complete, and main
  event dispatchers have ten direct `BL` ingress sites in total;
- every linked source definition is therefore rooted by a table entry or a
  direct call;
- an aligned whole-image scan finds those 74 parser cells and no pointer into
  the strict interior of any recovered body.

The complete per-function line, source-span hash, stock interval, and stock
body hash ledger is
[`ambiq-cordio-hci-evt-function-map.tsv`](../../tools/manifests/ambiq-cordio-hci-evt-function-map.tsv).

## Clean-room implementation and production routing

The proprietary file is used only as an inventory and behavioral oracle. A
separately authored GPL-3.0-only decoder now implements all 80 APIs from the
Bluetooth HCI wire format and the public Cordio callback ABI. It bounds every
read, rejects malformed lengths, accounts unknown events, preserves connection
and CIS lifecycle callbacks, and covers command, advertising, privacy, PHY,
CTE/IQ, CIS/ISO, codec, and BIG event families.

All 79 linked entries are production-owned: 78 guarded wide branches plus the
authenticated two-byte `hciEvtParseLeScanTimeout` no-op as an exact in-place
copy replace all 6,718 stock body bytes. The overlay contributes 23,590
compiled bytes, 30 alignment bytes, and 52 strict relocations; the source-only
`hciEvtGetStats` also target-compiles. Host behavior tests, exact 80-symbol
Cortex-M55 compilation, 161 manifest regions, deterministic packaging, and
the `(5863, 2, 5, 6)` flash-plan contract are green.

## Exact stock boundaries

| Object | Interval | Bytes | SHA-256 |
|---|---:|---:|---|
| Linked physical TU | `[0x00569D4C,0x0056B7EC)` | 6,816 | `4d7dfa091432416e0eab04bedee540929d97fd640295906f64ce36ea71d85b2d` |
| Concatenated bodies | 79 spans | 6,718 | `4fc280002f216e5ee787f8b98f126a9f4ab2af8d7f17e0fc8796d28b6b44b9f6` |
| Concatenated non-code gaps | 5 spans | 98 | `d382d6b4650a892647a6eceb5ef21dbfcfb01b5fcd96b6a3a5ce35ea0b8d313d` |
| Parser table | `[0x006C910C,0x006C9260)` | 340 | `b61db5479706fbe355d1173a5636c7ed8c4cb2e91f48bf3ab96add02a6e3fb60` |
| Callback-size table | `[0x006E3720,0x006E3775)` | 85 | `72451d4e8b3cd63e6a1bf880cd3a651083250b66a00485064a8f222538213ef8` |

The body gaps are `[0x0056A902,0x0056A908)`,
`[0x0056ABCE,0x0056ABD4)`, `[0x0056B13E,0x0056B150)`, and
`[0x0056B37C,0x0056B390)`. The owned tail is
`[0x0056B7BC,0x0056B7EC)`; the next translation unit begins exactly at
`0x0056B7EC`.

The retained Windows path begins at `0x006E0518`. Its only raw pointer cells
are `0x0056B37C` and `0x0056B7E4`, which independently keep both the
command-complete literal pool and final TU pool attached to `hci_evt.c`.

## Dispatch and ABI

The transport calls `hciEvtProcessMsg` directly at `0x00530CCE`. The main
dispatcher separates command-status, command-complete, completed-packet,
LE-meta, disconnection, encryption, hardware-error, authentication-timeout,
and vendor events. Ordinary callback events use the callback-size table to
allocate a temporary event object, initialize its four-byte WSF header, invoke
the indexed parser, deliver it to the selected callback, and release it.
Security command completions select the security callback; ordinary controller
events select the event callback. Connection and CIS close bookkeeping occurs
after the corresponding disconnect callback.

Advertising, extended-advertising, periodic-advertising, direct-advertising,
connection-IQ, and connectionless-IQ reports use dedicated processors because
one controller event can produce multiple application callback objects. The
85-entry parser ABI also covers CTE, CIS/CIG, ISO data paths, codec queries,
BIG creation/termination/synchronization, and BIG-info reports.

Two global addresses require precise ownership:

| Address | Object | Evidence |
|---:|---|---|
| `0x20073870` | `hciCb` | dispatchers load callback fields from `+8` and `+12`; seven literal references |
| `0x20073BC0` | `hciEvtStats` | the main dispatcher updates counters; sole literal at `0x0056B7D4` |

The labels are not interchangeable. The sole `hciEvtStats` literal belongs to
the `hciEvtProcessMsg` tail. No subsequent code body exists before the next TU,
and there is no direct caller or stored entry for `hciEvtGetStats`; the getter
is therefore source-only/dead-stripped.

## Source-family discriminator and license boundary

AmbiqSuite R2.5.1 provides a 67-entry table and 62-definition source family.
Stock instead has 85 parser and callback-size entries, including the later
CTE/ISO/BIG event surface. Its retained diagnostic line values `1625`, `1629`,
`1680`, and `2831` agree with the later official AmbiqSuite R4.4.1 source
layout. The selected reconstruction oracle is:

```text
commit  4264b9309e03064ffad13a0468d5d0c1110c5288
blob    d2b2648587b2c8e89852f9d99555b35148e4d6ca
bytes   105,064
sha256  5bee4484a94968be22cf59b60aa1d40441a824f26fe657edc58ca3e190037f24
```

That commit is a later official neuralSPOT import and is exact corroboration,
not the resolved historical G2-producing commit. Unlike the Packetcraft stack
files surrounding it, Ambiq's `sources/hci/ambiq/hci_evt.c` is governed by the
proprietary Arm Cordio software license. No source or source-derived patch is
copied into openCFW. The repository retains only clean-room facts: names,
addresses, hashes, table values, ABI, control-flow relationships, and behavior
needed for an independent implementation.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_hci_evt.py --json
make cordio-hci-evt-closure
```

Canonical artifacts are overlay `404,200` bytes / SHA-256 `6a00a8b1...e478`,
Apollo component `3,927,596` bytes / `ef9de7e2...4970`, and package `4,706,090`
bytes / `7868cccb...4d9d`. No hardware was accessed.
