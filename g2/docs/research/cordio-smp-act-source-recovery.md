# Cordio `smp_act.c` source recovery

## Result

The stock G2 interval `[0x0056E5CC,0x0056F178)` is the complete Cordio
`ble-host/sources/stack/smp/smp_act.c` translation unit. It contains all 25
public source definitions: 2,924 code bytes and 64 bytes of inline strings,
alignment, and literals. No source function is dead-stripped.

The selected Apache-2.0 oracle is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`3c1ac36652243add46ba812e45e62555a5668ba3`, 27,952 bytes, SHA-256
`5149ca2e6feb98157b3a5fe7d2061c5eba1e09d3bc8f7d9ee666ec4478849f4f`.
The same blob appears in r20.05, r20.05a, and r20.05b. Packetcraft r19.02 and
AmbiqSuite 2.4.2/2.5.1 instead use blob
`63cdf81192c791f24a0ea97a0fa154b3e7651081`; that version lacks
`smpActSecReqTimeout` and the guarded secure-connections trace path. Both are
present in stock, independently selecting the r20 family.

The later public file is a semantic and provenance oracle, not a claim that
the IAR-generated stock object is byte-identical to a public compiler output.
Production continues to cut the object forward.

## Stock boundary and ingress

The physical object is 2,988 bytes, SHA-256
`b872ffd10869a0b17635f46054fb106161af819661ec5b6bbea597a55320e45d`.
Its 25 concatenated bodies hash to
`244fee09f0e392daff7b57a6ca8803bc60c784a01e27375ea3b63bfb0d3b19df`.
The only internal non-code gap is `[0x0056EC88,0x0056EC94)` containing the
`ERR`, `SMP`, and `HCI` categories. The 52-byte tail at
`[0x0056F144,0x0056F178)` owns logger literals plus pointers to
`pSmpCfg=0x200004B8`, `smpCb=0x20070AEC`, and the retained source path at
`0x006E1994`. The next unrelated function starts at `0x0056F178`.

Raw Thumb decoding finds 78 direct calls to exact function entries. Four
role action tables and two pairing/auth callback pairs contribute exactly 62
stored entry pointers. An exhaustive unaligned word scan finds no stored
strict-interior address. Thus every direct or stored ingress is closed without
depending on Ghidra's discovered-function set.

The four action tables are:

- responder SC `[0x006D0B64,0x006D0C40)`, 55 pointers;
- initiator SC `[0x006D1214,0x006D12E0)`, 51 pointers;
- responder legacy `[0x006D7E7C,0x006D7EE8)`, 27 pointers;
- initiator legacy `[0x006DBAC4,0x006DBB28)`, 25 pointers.

The callback pairs at `[0x00537F0C,0x00537F14)` and
`[0x005380FC,0x00538104)` both store `smpProcPairing` and `smpAuthReq`.

## ABI and behavior

The unit operates on the previously closed 76-byte `smpCcb_t`. Relevant
offsets are the response and wait timers at `+0x00/+0x10`, scratch pointer at
`+0x30`, initiator/security-request/flow flags at `+0x3A/+0x3B/+0x3C`,
connection ID/state/next command at `+0x3D/+0x3E/+0x3F`, authentication and
attempt state at `+0x40/+0x42/+0x43`, and secure-connections pointer at
`+0x48`. `smpCb` stores responder/master interfaces at `+0xE4/+0xE8`, handler
ID at `+0xEC`, pairing/auth callbacks at `+0xF0/+0xF4`, and LESC support at
`+0xF8`.

The common dispatcher drives both legacy and Secure Connections role tables,
manages response timeouts and cleanup, handles maximum-attempt lockout, and
routes pairing, confirmation, key distribution, and completion actions. The
stock security-request-timeout path uses internal cleanup event `0x1F`, which
agrees with the independently closed r20 message ABI.

## Reproducibility

`tools/analyze_g2_cordio_smp_act.py` pins the official image, manifests,
physical object, every body, inline data, retained path, action/callback
tables, all 78 direct calls, all 62 stored entries, and the absence of an
interior pointer. The complete body ledger is
`tools/manifests/packetcraft-cordio-smp-act-function-map.tsv`; release identity
is in `packetcraft-cordio-smp-act-provenance.tsv`.

This work changes identified provenance only: zero stock bytes are replaced
and zero source-owned production bytes are added.
