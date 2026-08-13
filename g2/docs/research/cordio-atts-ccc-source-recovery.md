# Cordio ATT client-characteristic-configuration source recovery

Status date: 2026-08-08  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete linked `atts_ccc.c` translation unit is bounded at
`[0x0052BB64,0x0052C6C0)`: all fourteen upstream functions contribute 2,770
code bytes and the remaining 138 bytes are inline strings, alignment, and the
trailing literal table. No source API is dead-stripped. The whole 2,908-byte
interval has SHA-256
`965f8260bed0ed9852331f2fe950aecaae33a0f1f9fc1b8af514af193be39ce1`.

All definitions have an exact Apache-2.0 Packetcraft route. Stock adds local
connection validation and expanded diagnostics, so this is an exact
definition/behavior/ABI pin rather than a pristine whole-object claim. Every
byte remains cut forward and package ownership is unchanged.

## Upstream and release pin

AmbiqSuite R2.4.2/R2.5.1 and Packetcraft r19.02 share Git blob
`9e4e421200609e591ef8588efcfc503d35584489`, SHA-256
`880f7107c27bbb04fe15da83197d366b4b6fd1e840fade24b29b36b785b1f35b`.
Packetcraft r20.05 through r20.05c use the same fourteen definitions with a
reformatted Apache header:

- selected commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`;
- Git blob `3f230970d8b04ebce8307f8efda3b9ff6baa956a`;
- SHA-256 `d13076dd02de256340f0c1d8a963bcc2b6a48cbc7e386f3e4344c6fa66526f00`.

The function bodies alone do not distinguish the releases. The compiled
callback does: stock emits `ATTS_CCC_STATE_IND = 0x14`, while r19 and pristine
AmbiqSuite 2.5.1 use `0x10`. The value shifted to `0x14` in Packetcraft
r20.05, independently selecting an r20-compatible ATT header family.

## Complete stock map

| Function | Stock interval | Bytes | Ingress |
|---|---:|---:|---:|
| `attsCccCback` | `0x52BB64..0x52BB8A` | 38 | 2 BL |
| `attsCccAllocTbl` | `0x52BB8A..0x52BCEA` | 352 | 1 BL |
| `attsCccGetTbl` | `0x52BCEA..0x52BE26` | 316 | 4 BL |
| `attsCccFreeTbl` | `0x52BE34..0x52BF8E` | 346 | 1 BL |
| `attsCccReadValue` | `0x52BF8E..0x52BFF0` | 98 | 1 BL |
| `attsCccWriteValue` | `0x52BFF0..0x52C09E` | 174 | 1 BL |
| `attsCccMainCback` | `0x52C0AC..0x52C224` | 376 | registered callback |
| `AttsCccRegister` | `0x52C224..0x52C23C` | 24 | 1 BL |
| `AttsCccInitTable` | `0x52C244..0x52C3C4` | 384 | 4 BL |
| `AttsCccClearTable` | `0x52C3D0..0x52C5F2` | 546 | 1 BL |
| `AttsCccGet` | `0x52C5F2..0x52C60E` | 28 | 2 BL |
| `AttsCccSet` | `0x52C60E..0x52C628` | 26 | 1 BL |
| `AttsCccEnabled` | `0x52C628..0x52C660` | 56 | 2 BL |
| `AttsGetCccTableLen` | `0x52C664..0x52C66A` | 6 | 2 BL |

The fourteen bodies concatenate to SHA-256
`9f221e670e7ba1314147cf258de57d1ea51955e9d728e7b0002f97a6e60e1b96`.
Exact body hashes, source-span hashes, and all 23 direct BL sites are in
`tools/manifests/packetcraft-cordio-atts-ccc-function-map.tsv`.

`attsCccMainCback` is registered through the intentional Thumb pointer at
`0x0052C6A4` (`0x0052C0AD`) and has eight indirect consumers. The exhaustive
aligned-pointer and control-flow audit found no other stored entry/interior
pointer and no exterior branch into a function interior.

## ABI and product configuration

The 24-byte `attsCccCb` at `0x20073B00` is:

```text
+0x00/+0x04/+0x08  pCccTbl[3]
+0x0C              settings-table pointer
+0x10              application callback
+0x14              uint8 settings count
```

This proves `DM_CONN_MAX=3`. The registration call passes six settings at
`0x007518C0` and application callback `0x004B7533`. Each six-byte setting is
`{uint16 handle, uint16 valueRange, uint8 securityLevel, pad}`:

```text
(0x0013,2,0), (0x0825,1,0), (0x0845,1,0),
(0x0865,1,0), (0x0885,1,0), (0x08A5,1,0)
```

Read/write dispatch scans this table, returns ATT errors `0x0A` or `0x11`
for missing handle/table, and permits CCC values 0, 1, or 2 only when the
enabled bit intersects `valueRange`; invalid values return `0x80`. Writes
notify only on change. Stock's callback event has a deliberately uninitialized
status byte, matching the observed ABI rather than a safer invented value.

## Lorelei result and reproducibility

The repository owns
`research/readiness/atts-ccc/` (5,669 bytes, SHA-256
`357e999ceae62d08aa74b1d12a02e4db845da1b7293347ff791c33e7872b6ee6`).
Its fifteen inner hashes cover the conservative five-anchor/1,944-byte probe,
two ARM GCC profiles, seven provider seams, and two zero-unresolved closure
links. The subsequent local authenticated closure expands that evidence to
all fourteen linked functions / 2,770 bytes.

The artifact excludes firmware, upstream source, decompilation, objects,
ELFs, and caches. Run the fail-closed checks from `openCFW`:

```sh
python3 tools/analyze_g2_cordio_atts_ccc.py --json
python3 tools/verify_research_corpus.py --json
```

Production promotion still requires modeling the product validation/logger
seam, exact provider relocations, IAR code generation, and placement.
`attc_disc.c` is now closed separately; `dm_adv_leg.c` is the next fast
bounded public-source target.
