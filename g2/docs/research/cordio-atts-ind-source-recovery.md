# Cordio ATT server indication/notification source audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `atts_ind.c` translation unit is completely partitioned at
`[0x005338AC,0x00533EF4)`, 1,608 bytes, SHA-256
`2d446a918ca02515e09115b012395e9a74edee087101a4c7d95cd8846e3ce669`.
Thirteen linked functions contribute 1,552 code bytes; two six-byte category
gaps and one 44-byte literal pool contribute the remaining 56 bytes. The
logical function concatenation hashes to
`d52b3d12ae2978a4589b75f52e5d937aed7929c61ad42a2c376f8efa27a7bb13`.

The linked inventory includes all pending-handle helpers and callbacks, packet
setup, the connection/message/control callbacks, the common sender,
`attsProcValueCnf`, `AttsIndInit`, and the ordinary-copy indication and
notification wrappers. Only `AttsHandleValueIndZeroCpy` and
`AttsHandleValueNtfZeroCpy` are dead-stripped. The common worker still retains
its zero-copy branch because it is shared, but the image has no zero-copy entry
wrapper or caller. This is an active indication/notification implementation,
not the optional-path exclusion seen in `atts_sign.c`.

Twenty-two direct calls land on exact entries. Three registered pointers are
the callbacks in `attsIndFcnIf`. A fourth raw entry-valued word at `0x00791AD0`
belongs to the compressed IAR initialized-data stream; after boot decoding it
populates method 15 of the live ATT PDU processor table in SRAM. No stored
strict-interior pointer or direct BL into an interior survives. Stock remains
cut forward; no production bytes changed.

## EATT ABI and dispatch

Stock is the r20 EATT-aware architecture. `AttsIndInit [0x00533E40,
0x00533E90)` initializes nine 64-byte server CCBs: three connections by three
bearers. Connection groups have stride `0xC0`; each bearer CCB stores its timer
at `+0`, main ATT CCB at `+0x10`, connection ID at `+0x24`, slot at `+0x25`,
outstanding indication handle at `+0x26`, pending indication handle at `+0x28`,
and ten pending notification handles beginning at `+0x2A`.

`attsCb` is `0x2006E5F0`. Initialization stores the interface address at
`attsCb+0x260` and initializes all nine timer handler IDs/connection params.
The interface at `[0x007852C0,0x007852D0)` is:

```text
attEmptyDataCback, attsIndCtrlCback, attsIndMsgCback, attsIndConnCback
```

Its SHA-256 is
`ed91ad349eae91a91c25376f92691628507d111b23ecbf1dc620ad520137279f`.
The live processor table is the 72-byte initialized SRAM object at
`0x2000045C`; its method-15 cell is `0x20000498` and contains `0x00533DD9`.
The matching raw word at `0x00791AD0` is a literal in the compressed
initializer stream, not the runtime table address.

The common sender locks around CCB/MTU/timeout discovery, enforces client
change-awareness and MTU bounds, allocates the API/PDU buffers, and posts event
`0x21`. Packet setup sends through the selected bearer, starts the indication
timer for opcode `0x1D`, and either executes or queues the notification
callback. Value confirmation stops the timer, promotes a service-change peer
to change-aware when appropriate, and completes the pending callback when flow
control permits. Connection close stops all three bearer timers and drains all
pending callbacks with the translated HCI status.

## Source lineage

Packetcraft r19.02 and AmbiqSuite R2.4.2/R2.5.1 use a separate legacy
single-bearer indication control block. Stock instead has the r20 per-bearer
CCB layout, slot-aware callbacks, three-by-three initialization, encoded timer
parameters, and CSF change-awareness flow. Those structural facts exclude the
r19 family independently of surrounding ATT modules.

Packetcraft r20.05 through r20.05c is invariant at Git blob
`803f1fefb245314a8332d6fbc210306afd2ff3ec`, 21,163 bytes, SHA-256
`d79922dbfcc00e4b8b68c13c7bfc604f88b173fc431daba89c70c24331495567`.
The selected public pin is commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. The official later AmbiqSuite
R4.4.1 import is byte-identical and corroborates the same family. The file is
Apache-2.0. These bytes are an exact public definition oracle, not proof that
the later import commit historically generated G2 or that a compiler object is
byte-identical.

The retained source path begins at `0x006DC994` and is referenced by the sole
path cell at `0x00533EA8`.

## Reproduction

The source inventory, function bytes, category gaps, literal pool, callback
interface, PDU dispatch cell, calls, source path, global references, and
pointer/interior scans are guarded by:

```sh
python3 tools/analyze_g2_cordio_atts_ind.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_ind
```

The next bounded ATT server target is `atts_main.c`, which owns `attsCb`, the
PDU processor table containing the value-confirmation entry, and the common
data/control/message routing used by this unit.
