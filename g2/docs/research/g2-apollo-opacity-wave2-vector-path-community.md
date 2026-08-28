# Apollo opacity wave 2: vector-path command community

Status: software-only, research admission; no hardware operation or production
routing.

## Selection and reconciliation

Wave 1 ended with 1,448 functions / 201,224 official opaque bytes. One of
those parent-census rows, `sqrtf` at `[0x004397A8,0x004397C4)`, contributes
zero official opaque bytes and is already source-recreated and redirected by
the IAR runtime tranche. Reconciliation therefore leaves 1,447 actionable
functions / 201,224 bytes before wave 2.

The largest remaining envelope is `[0x005156B8,0x00516B34)`: 5,244 official
bytes, with 5,178 decoded corpus bytes. Its complete authenticated body calls
six still-unclassified no-evidence functions directly. Wave 2 types the root
and all six of those callees:

| Entry | Envelope bytes | Corpus bytes | Bounded role |
|---|---:|---:|---|
| `0x005156B8` | 5,244 | 5,178 | vector-path command interpreter root |
| `0x00514AEC` | 138 | 138 | command-record allocation helper |
| `0x0051565C` | 16 | 16 | state-bit helper |
| `0x00516B34` | 170 | 170 | command-record builder |
| `0x005179D0` | 1,072 | 1,072 | vector-geometry helper |
| `0x0052266E` | 68 | 68 | command-state mask helper |
| `0x005639E8` | 1,364 | 1,334 | vector-segmentation helper |

This is a non-contiguous, one-hop call community, not a claim that every byte
in the address hull `[0x00514AEC,0x00563F3C)` belongs to the batch.

The remaining root calls are completely partitioned rather than ignored:

- `0x005226B2` is already typed by wave 1;
- `0x004397A8` is the already recreated IAR `sqrtf`; and
- `0x0050969C` is already in the parent census's first-party, low-confidence
  bucket and was never part of the no-evidence residual.

## Provider boundary

The bodies manipulate path opcodes, floating-point geometry, command records,
and command-state masks. The checked-in Ambiq/Nema provenance authenticates
AmbiqSuite 5.1.0, NemaGFX 1.4.12 as the stock lower bound/exact packaged
candidate, and NemaVG 1.1.8 as the co-packaged candidate. That audit resolves
eleven concrete stock symbols, but none of the seven wave-2 addresses is in
that resolved-symbol map.

This absence is material because the public Apollo5 Nema archive retains GCC
DWARF and is explicitly qualified only as a source/interface candidate for
IAR-generated stock. The original IAR-built NemaGFX/NemaVG archive or exact
private source commit remains unavailable. For the six wave-2 addresses that
its bounded scope includes, the FreeType census independently records no
FreeType anchor, string, or call-community evidence; it makes no claim about
the out-of-scope `0x005639E8` body.

Consequently, NemaGFX/NemaVG is recorded only as candidate family context.
No exact function name, source identity, license, or callable implementation is
claimed for any row. All seven dispositions are
`typed-external-provider-unavailable`. Production admission requires an exact
source/provider identity, ABI and configuration closure, and an honest
code-generation/relocation/placement recipe.

Nothing here is routed into production.

## Accounting

| State | Functions | Bytes |
|---|---:|---:|
| Wave-1 residual | 1,448 | 201,224 |
| Existing IAR `sqrtf` reconciliation | 1 | 0 |
| Before wave 2 | 1,447 | 201,224 |
| Newly typed | 7 | 8,072 |
| After wave 2 | 1,440 | 193,152 |

The next largest envelope is 5,224 bytes at `0x00517E18`. The analyzer pins
the official image, both corpus bundles, all inherited family manifests, the
Nema provenance record, every body/envelope hash, the static boundary table,
and the complete root-call partition. It performs no signing, flashing,
probing, or hardware access.
