# GoMore energy-model provider boundary

## Decision

Nine formerly unclassified functions / 2,360 executable bytes form the original closed GoMore
energy-model dispatcher/estimator boundary. All nine are now source-admitted. The complete mode
dispatcher, both estimator families, table-driven estimator, interpolation/projection/nonlinear
helpers, state reset, formulas, and all 81 table values compile from transparent C. The static
census retains the original attribution disposition as historical evidence, while the generated
function-ownership ledger records current admission.
The historical evidence summarizer still emits its original
`vendor_source_required_not_redistributable` attribution field; that field describes provenance at
the census stage and is not the current executable-source disposition.

## Callgraph evidence

The now source-admitted energy output producer `0x0005F56C` calls dispatcher `0x0002F488` at exactly
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

All child callers remain inside this graph except `0x00090E68`, which is also called by
source-admitted `0x0005F56C` and still-gated `0x000715D4`. The closure directly reuses source-admitted
interpolation/energy helpers at `0x0002F614`, `0x00061720`, `0x00068238`, and `0x0007316C`.
Those entries and Arm toolchain math routines are excluded from this supplemental census. The
adjacent resting-energy, substrate-fraction, and zone-accumulation leaves at `0x00068728`,
`0x00067D48`, `0x0002F108`, and `0x000763D8` are also now source-admitted as
`gomore_primitives_daily_resting_kcal`, `gomore_primitives_substrate_fat_fraction`,
`gomore_primitives_energy_zone_thresholds`, and `gomore_primitives_energy_zone_accumulate`; they
are not members of the nine-function private dispatcher/estimator closure tabulated below.

The two-byte address hole `0x00088D4C..<0x00088D4E` is not part of Ghidra's function body for
`0x00088BD0`. Its exact body is therefore pinned as two executable segments, preventing adjacent
bytes from being absorbed into the provider census.

## Exact census

| Entry | Executable bytes | Boundary role |
| --- | ---: | --- |
| `0x0002F488` | 336 | source-admitted as `gomore_primitives_energy_dispatch` |
| `0x000304D8` | 76 | energy-model output transform; source-admitted as `gomore_primitives_scaled_product` |
| `0x0005A448` | 340 | source-admitted as `gomore_primitives_energy_estimator_family_b` |
| `0x0005D3F8` | 220 | energy-model result projection; source-admitted as `gomore_primitives_energy_projection` |
| `0x00075D88` | 132 | energy-model nonlinear scale helper; source-admitted as `gomore_primitives_energy_nonlinear_scale` |
| `0x0007DA30` | 632 | source-admitted as `gomore_primitives_energy_table_estimator` with exact typed tables |
| `0x00088BD0` | 426 | source-admitted as `gomore_primitives_energy_estimator_family_a` |
| `0x00088DB4` | 168 | source-admitted as `gomore_primitives_energy_interpolate_pair` |
| `0x00090E68` | 30 | energy-model state reset helper; source-admitted as `gomore_primitives_energy_state_reset` |

The former largest unknown at `0x0007DA30` has SHA-256
`4a1eeec9e1e5b6b5563e814c2f17e74d9adb8f1af90fe46a85e6bf95c59aed6a`. The static summarizer
verifies the application image, all nine exact bodies and inbound callsite sets, the dispatcher
root, aggregate count, and provider disposition:

```sh
python3 tools/evidence/summarize_r1_gomore_energy_model.py
```

It emits no algorithm source and performs no live sensor access.

## Integration rule

The complete nine-function closure compiles independently and contains no opaque firmware bytes
or vendor source. Toolchain double division is represented directly in C, while `exp` and logarithm operations remain explicit typed providers;
the recovered 27-mode tables are ordinary inspectable C constants rather than binary blobs.
The enclosing 2,102-byte producer is `gomore_primitives_energy_update`: its stock 92-byte state is
an offset-checked C type, its internal pointer-backed reference is a direct float, and its eleven
outputs are a named C structure. All three producer variants and modes zero through five are
covered without executable blobs or opaque tables.
