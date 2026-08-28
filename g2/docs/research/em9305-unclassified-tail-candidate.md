# EM9305 890-byte residual-tail candidate

Status: exhaustive software-only partition; not production-routed

License: MIT

Hardware activity: none

## Result

The former 36-span / 890-byte `unclassified_insufficient_evidence` tail now
has a deterministic decision for every byte:

| Decision | Spans | Bytes | Treatment |
|---|---:|---:|---|
| Mechanically reconstructible | 21 | 260 | isolated MIT semantic primitives |
| Unsupported external/provider boundary | 15 | 630 | fail closed unless an explicit provider is supplied |
| **Total** | **36** | **890** | complete partition |

This decision map does not silently rewrite the existing ownership map.  Each
span remains `unclassified_insufficient_evidence` until independent source
provenance identifies its owner.  “External” is an integration decision based
on unresolved target/state semantics, not a new copyright attribution.

The candidate lives in:

- `components/shared/em9305/runtime_unclassified_tail_candidate.c`
- `components/shared/em9305/runtime_unclassified_tail_candidate.h`

It contains no stock absolute address in an executable primitive.  Future
reviewed ARC veneers must supply RAM or MMIO symbols explicitly.  The stock
addresses and hashes in the external evidence table are metadata only.

## Exhaustive decision map

### Reconstructible spans: 21 / 260 bytes

| Model | Stock starts | Evidence |
|---|---|---|
| No-op returns | `302D80`, `304EB4`, `313778`, `3137F4` | only `nop`/`j_s [blink]` entries |
| Scalar/structure accessors | `303E50`, `303F50`, `303F68`, `3047B0`, `3069B8`, `307C08`, `307DD8`, `30F368`, `310480`, `3108F4`, `311F84`, `3122F0`, `313760`, `31B2F8`, `32CAC4` | bounded byte/halfword/word load/store leaves, boolean normalization, or constant byte setters |
| Standard memory tail | `31369C` | `r1=0`, `r2=0x90`, tail branch to authenticated `memset` at `33301C` |
| MMIO read-modify-write | `30F710` | two identical bodies set bit 23 of the supplied 32-bit register |

The MIT API supplies null-checked byte, halfword, and word load/store
primitives; byte-offset load/store; exact `!= 0` and `== expected` boolean
normalization; a no-op; a generic set-bits operation; and a freestanding
zero-fill loop.  The same zero-fill primitive covers the independently
reachable 144-byte standard-memory tail without importing `memset`.

### Unsupported external spans: 15 / 630 bytes

| Stock start | Bytes | Boundary reason |
|---:|---:|---|
| `307D64` | 16 | registers unresolved code pointer `321150` |
| `30AE24` | 106 | registers six unresolved controller callbacks |
| `30B1AC` | 4 | veneer into controller body `306B70` |
| `30C094` | 4 | veneer into controller body `307158` |
| `30C228` | 146 | multi-stage controller parser over eight callees |
| `3100EC` | 4 | idle-hook veneer to unresolved `3119A8` |
| `314728` | 4 | veneer to unresolved shared target `30FAB4` |
| `314754` | 4 | veneer to unresolved shared target `30FAB4` |
| `3151CC` | 8 | two veneers to unresolved shared target `30FAB4` |
| `318200` | 90 | 912-stride controller connection-table lookup |
| `31A980` | 6 | zero-argument veneer to unresolved `30E7F8` |
| `31E8FC` | 66 | stride-24 callback dispatch/state advance |
| `3228A8` | 58 | stride-20 callback dispatch/state advance |
| `324AA0` | 8 | field-load veneer to unresolved `30E878` |
| `332CC0` | 106 | zero-fill entry shares a span with unresolved controller statistics logic |

These entries use a typed 15-ID provider boundary and a conservative
four-word OpenCFW invocation carrier.  With no provider, the result is
`OPEN_CFW_EM9305_TAIL_UNSUPPORTED_EXTERNAL`; provider failures are normalized
to a distinct failure status.  The boundary does not call a stock absolute
address or guess its ABI.

The `332CC0` range demonstrates why whole-span replacement remains disabled:
its first entry plainly zeroes 404 bytes via the authenticated `memset`, but
the remaining entry mutates a multi-field statistics structure.  The generic
zero-fill primitive establishes the standard part without claiming the
mixed span is replaceable.

## Reproduction

The read-only analyzer authenticates the official image, complete ARC
objdump, existing provenance map, every exact range and SHA-256, all 36
semantic instruction signatures, the 36/890 census, the 21/260 and 15/630
partition totals, external evidence descriptors, MIT markers, and candidate
API:

```sh
python3 tools/analyze_em9305_unclassified_tail_candidate.py --json
python3 -m unittest -v tests.test_em9305_unclassified_tail_candidate
```

The focused host suite exercises every primitive width, offset operations,
boolean normalization, bit preservation, 144- and 404-byte zero fills,
invalid arguments, all external descriptors, unsupported/provider behavior,
JSON output, and a freestanding object with no undefined runtime imports.

## Remaining integration blockers

1. Bind the 260 reconstructible bytes to reviewed EM9305 RAM/MMIO symbols and
   exact ARC calling conventions.
2. Independently identify or replace the unavailable controller registration,
   parser, dispatch, connection-table, and statistics semantics.
3. Resolve every veneer target and prove argument, delay-slot, and return
   preservation before supplying a provider.
4. Split mixed/interior entries—especially `332CC0`—without breaking direct
   callers.
5. Authenticate final link placement and every reference before production
   routing.

No upstream implementation island beyond the already-authenticated standard
`memset` semantic was positively identified in these 890 bytes.  The audit
therefore makes no unsupported upstream-source or license claim.
