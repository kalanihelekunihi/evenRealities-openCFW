# GoMore energy-model provider boundary

## Decision

Nine formerly unclassified functions / 2,360 executable bytes form a closed GoMore energy-model
dispatcher/estimator boundary. Every entry is routed to `gomore_health_algorithm_candidate` with
disposition `vendor_source_required_not_redistributable`. OpenR1 does not reproduce the private
mode formulas, tables, interpolation, nonlinear scaling, thresholds, or state transitions. A
matching licensed GoMore provider is required.

## Callgraph evidence

The already gated energy output producer `0x0005F56C` calls dispatcher `0x0002F488` at exactly
`0x0005F6DC`, `0x0005F85A`, and `0x0005FA30`. No other function calls the dispatcher. Its mode byte
at private-state offset `0x08` selects two specialized estimator families or the table-driven
estimator at `0x0007DA30`.

Recursive traversal over unclassified direct descendants closes exactly nine functions:

```text
GoMore energy output producer 0x0005F56C
  -> mode dispatcher 0x0002F488
       -> estimator family A 0x00088BD0
       -> estimator family B 0x0005A448
       -> table-driven estimator 0x0007DA30
            -> interpolation, projection, scale, and output helpers
```

All child callers remain inside this graph except `0x00090E68`, which is also called by already
gated GoMore functions `0x0005F56C` and `0x000715D4`. The closure directly reuses already gated
GoMore interpolation/energy helpers at `0x0002F614`, `0x00061720`, `0x00068238`, and `0x0007316C`.
Those pre-existing provider entries and Arm toolchain math routines are excluded from this
supplemental census.

The two-byte address hole `0x00088D4C..<0x00088D4E` is not part of Ghidra's function body for
`0x00088BD0`. Its exact body is therefore pinned as two executable segments, preventing adjacent
bytes from being absorbed into the provider census.

## Exact census

| Entry | Executable bytes | Boundary role |
| --- | ---: | --- |
| `0x0002F488` | 336 | energy-model mode dispatcher |
| `0x000304D8` | 76 | energy-model output transform |
| `0x0005A448` | 340 | energy-model estimator family B |
| `0x0005D3F8` | 220 | energy-model result projection |
| `0x00075D88` | 132 | energy-model nonlinear scale helper |
| `0x0007DA30` | 632 | table-driven energy estimator |
| `0x00088BD0` | 426 | energy-model estimator family A |
| `0x00088DB4` | 168 | energy-model interpolation helper |
| `0x00090E68` | 30 | energy-model state reset helper |

The former largest unknown at `0x0007DA30` has SHA-256
`4a1eeec9e1e5b6b5563e814c2f17e74d9adb8f1af90fe46a85e6bf95c59aed6a`. The static summarizer
verifies the application image, all nine exact bodies and inbound callsite sets, the dispatcher
root, aggregate count, and provider disposition:

```sh
python3 tools/summarize_r1_gomore_energy_model.py
```

It emits no algorithm source and performs no live sensor access.

## Integration rule

OpenR1 may expose R1-owned input/output adapters around an authenticated licensed GoMore provider.
When that provider is absent, energy-model behavior remains disabled. Decompiled formulas and
lookup tables are compatibility evidence only and are not an implementation specification.
