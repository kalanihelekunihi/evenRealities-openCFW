# Cordio ATT UUID constant-object source audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

`att_uuid.c` is a data-only translation unit. The stock IAR linker retains
exactly 11 of its 152 exported two-byte UUID objects in one contiguous,
source-ordered block at `[0x0078F53A,0x0078F550)`. The 22 bytes are
`0118002803280229002a012a052aa62ac92a292b2a2b`, SHA-256
`abd74006e64d5b20f979480d581c692fe24b82bc85d6c3fc8b4ee8ffcfb735e3`.
The other 141 source objects are source-only/dead-stripped.

| object | address | UUID | whole-image pointer cells |
|---|---:|---:|---:|
| `attGattSvcUuid` | `0x0078F53A` | `0x1801` | 1 |
| `attPrimSvcUuid` | `0x0078F53C` | `0x2800` | 8 |
| `attChUuid` | `0x0078F53E` | `0x2803` | 23 |
| `attCliChCfgUuid` | `0x0078F540` | `0x2902` | 10 |
| `attDnChUuid` | `0x0078F542` | `0x2A00` | 1 |
| `attApChUuid` | `0x0078F544` | `0x2A01` | 1 |
| `attScChUuid` | `0x0078F546` | `0x2A05` | 3 |
| `attCarChUuid` | `0x0078F548` | `0x2AA6` | 1 |
| `attRpaoChUuid` | `0x0078F54A` | `0x2AC9` | 1 |
| `attGattCsfChUuid` | `0x0078F54C` | `0x2B29` | 1 |
| `attGattDbhChUuid` | `0x0078F54E` | `0x2B2A` | 4 |

These objects form the exact retained subsequence of the public source order.
The immediately preceding halfword at `0x0078F538` is unrelated value
`0x003D`. The three following UUIDs at `[0x0078F550,0x0078F556)` are local
constants owned by the separately closed `atts_read.c` object, not another
part of `att_uuid.c`. Common 16-bit UUID values occur elsewhere in flash as
application service-table data; numeric equality alone is therefore not
accepted as object identity.

The complete source inventory is pinned in
`tools/manifests/packetcraft-cordio-att-uuid-object-map.tsv`. It records the
source line and line hash, UUID value, link status, stock address, and exact
reference count for all 152 objects.

## Reference closure

An exhaustive unaligned four-byte scan of the authenticated image finds
exactly 54 values pointing to the 11 retained object entries. Every cell is
naturally four-byte aligned; no accidental unaligned window survives. The
ordered `(cell,target)` stream hashes to
`fc35bb83ea308315a67feaef930c61b9e5c81bebef7223b1847c664c71277aa1`.

The cells include ATT core/client/server literal pools, the discovery and
read paths, static GAP/GATT service databases, and constant attribute tables.
The analyzer enforces every cell and the per-object totals. This is the data
equivalent of function entry/caller closure: the packed block, its two
boundaries, and every accepted stored reference are all exact.

## Source lineage

Packetcraft r20.05 through r20.05c provides `att_uuid.c` Git blob
`52cda51039c7665b66711cb45093395b0d55da34`, 15,852 bytes, SHA-256
`084b088781df6ef09647f6a4251406d92ec1b1aab6c6a61ef93a4982f5b756b7`.
The later official AmbiqSuite R4.4.1 import is byte-identical. The selected
public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; both copies are Apache-2.0.

AmbiqSuite R2.5.1/Packetcraft r19.02 carries blob
`079c768f29f4cbe53951a3262e0d06200ce33134`, 15,714 bytes, SHA-256
`8cbe89e1e5623b9571f1d0d7bbaff463226214b9786df52b9296a41fc426d88f`.
It already contains all 11 stock-retained constants. R20 adds the
server-supported-features UUID and reorders two source-only services, but the
linker removes those discriminating objects. This TU therefore supports the
already-proven r20/R4 ATT family but cannot independently distinguish it from
r19. The historical generating commit remains unresolved.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_att_uuid.py --json
python3 -m unittest tests.test_analyze_g2_cordio_att_uuid
```

Identification is complete: 11 linked plus 141 source-only objects account
for all 152 definitions. No source-owned production bytes are added; the 22
stock bytes remain cut forward pending final source build and link integration.
