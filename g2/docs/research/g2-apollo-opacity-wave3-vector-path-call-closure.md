# Apollo opacity wave 3: vector-path call closure

Status: software-only, research admission; no hardware operation or production
routing.

## Reconciliation

Wave 2 ended at 1,440 unclassified parent-census functions / 193,152 official
opaque bytes. Before selecting wave 3, the analyzer discovers another
zero-opaque-byte IAR runtime row in that residual: the aligned `memcpy` entry at
`0x00439C04`, which lies inside the already source-recreated and redirected
`__aeabi_memcpy` span. Removing that already owned row leaves 1,439 actionable
functions / 193,152 bytes.

The largest is `[0x00517E18,0x00519280)`, with a 5,224-byte official envelope
and 5,170 decoded corpus bytes.

## Complete bounded closure

Following only calls into the actionable no-evidence residual yields a finite
closure:

| Depth | Functions | Bytes | Entries |
|---:|---:|---:|---|
| 0 | 1 | 5,224 | `0x00517E18` |
| 1 | 7 | 1,498 | `0x005177A4`, `0x0051785C`, `0x00522622`, `0x00522F50`, `0x00522FB4`, `0x00523284`, `0x00524218` |
| 2 | 2 | 124 | `0x00514D2C`, `0x005242CC` |
| 3 | 1 | 684 | `0x00514504` |
| 4 | 3 | 110 | `0x00514070`, `0x0051416C`, `0x00514178` |
| 5 | 1 | 32 | `0x00514050` |
| **Total** | **15** | **7,672** | complete unresolved closure |

No actionable no-evidence target remains beyond depth five. External edges are
exhaustively partitioned as follows:

- wave 1: `0x005226B2`;
- wave 2: `0x00514AEC`, `0x0051565C`, `0x00516B34`, `0x0052266E`, and
  `0x005639E8`;
- source-recreated IAR runtime: `sqrtf` at `0x004397A8` and aligned `memcpy`
  at `0x00439C04`;
- parent-classified LVGL: `0x004B127C`; and
- zero-opaque-byte parent heap boundaries: `0x00484180`, `0x004841D8`, and
  `0x0048429E`.

This proves a closed graph boundary without assigning semantics to calls that
the evidence cannot name precisely.

## Provider and license disposition

The closure manipulates path geometry, command records, masks, and storage.
The checked-in Nema provenance authenticates NemaGFX 1.4.12 as the stock lower
bound/exact packaged candidate and NemaVG 1.1.8 as the co-packaged candidate.
It also provides a closed map of eleven resolved stock symbols. None of the
fifteen wave-3 addresses appears in that map.

The package's public Apollo5 archive carries GCC DWARF, while stock is IAR
generated. The original IAR-built NemaGFX/NemaVG archive or exact private
source state remains unavailable. All fifteen addresses also carry explicit
negative FreeType evidence: no FreeType anchor, string, or call-community
support.

Nema is consequently candidate family context only. The records claim no
upstream function identity, source body, or license and remain
`typed-external-provider-unavailable`. Production routing remains prohibited
until exact source/provider, ABI/configuration, license, relocation, and
placement evidence closes the boundary.

## Accounting

| State | Functions | Bytes |
|---|---:|---:|
| Wave-2 residual | 1,440 | 193,152 |
| Existing IAR aligned-`memcpy` reconciliation | 1 | 0 |
| Before wave 3 | 1,439 | 193,152 |
| Newly typed | 15 | 7,672 |
| After wave 3 | 1,424 | 185,480 |

The next largest envelope is 5,076 bytes at `0x0043A698`. The analyzer pins
the inherited waves, official image, corpus, Nema provenance, body/envelope
hashes, closure depths, complete call topology, and every terminal partition.
It performs no signing, flashing, probing, or other hardware access.
