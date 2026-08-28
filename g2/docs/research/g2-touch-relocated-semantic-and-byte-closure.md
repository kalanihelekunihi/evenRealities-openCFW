# G2 touch relocated semantic batches and physical-byte closure

This device-free tranche assigns conservative provider/semantic batches to all
223 previously opaque relocated CFG entries and gives every byte in the mixed
code/pool span a deterministic physical type. It does not claim that batched
functions have recovered source or exact historical private symbols.

## Semantic/provider batches

| Batch | Entries | Disposition |
|---|---:|---|
| Application/startup | 99 | Behavior recovery still required; new clean-room code may be MIT |
| Mixed CAPSENSE/CAT2 | 55 | Provider cannot yet be selected safely; EULA-or-Apache boundary |
| CAT2 PDL cluster | 54 | Apache-2.0 upstream provider candidate, not concrete source closure |
| Em_EEPROM cluster | 10 | Infineon-EULA external boundary; do not copy into MIT code |
| Runtime | 4 | Exact ABI/control-flow candidates under the selected runtime license |
| System/DFU handoff | 1 | Provider unresolved |
| **Total** | **223** | Every row has an explicit bounded disposition |

The four exact runtime candidates are the `0x76ac` exit wrapper, `0x76e4`
init-array walker, `0x7740` non-returning exit loop, and `0x7744` empty runtime
startup stub. No other formerly opaque row receives a concrete symbol name.

All 223 rows set `concrete_project_source=false`. In particular, an
Apache-2.0 provider candidate is not counted as code already present in the
project, and an EULA boundary remains external/private behavior.

The broad batches are intentionally weaker than individual symbol attribution:

- entries below `0x2998` remain application/startup behavior recovery;
- `0x2998..0x4b13` is a mixed CAPSENSE/MSCLP/CAT2 region and is not forced into
  either license family;
- `0x4b68..0x58ef` is bounded by established Em_EEPROM checksum/read/write
  anchors;
- `0x58f0..0x73bf` is bounded by SROM/GPIO/clock/SCB/system PDL anchors; and
- runtime names require exact ABI/control-flow evidence.

## Additional entry and case evidence

Three odd linked pointers in the shipped configuration block add startup/PDL
entry seeds at payload offsets `0x0108`, `0x0134`, and `0x6ec0`. Nine residual
runs begin with standard push-LR prologues immediately after a decoded return or
typed pool boundary. Direct-call closure from those seeds expands the function
candidate set from 286 to 301.

Three authenticated linked switch tables add 23 unique case targets:

- nine I2C command entries at payload `0x7dc4`;
- eight device-event entries at `0x81fc`; and
- twenty SROM-status entries at `0x821c`.

Case targets contribute CFG bytes but are not falsely promoted to standalone
functions.

## Final physical-byte partition

| Category | Bytes |
|---|---:|
| CFG instruction candidate | 27,674 |
| Switch-case instruction candidate | 482 |
| Referenced literal data | 1,964 |
| Bounded residual data | 60 |
| Legacy Thumb NOP padding (`0x46c0`) | 126 |
| Thumb NOP padding (`0xbf00`) | 8 |
| Zero halfwords, alignment-versus-data unresolved | 46 |
| Two `BX LR` runtime return tails | 4 |
| **Total** | **30,364** |

All physical bytes are typed, but “typed” is not synonymous with semantically
resolved. The 46 zero bytes deliberately retain alignment-versus-data
ambiguity, and CFG bytes do not imply source recovery.

The prior 1,584-byte residual set is accounted exactly:

- 782 CFG bytes;
- 482 switch-case CFG bytes;
- 76 newly referenced literal bytes;
- 60 bounded data bytes;
- 134 NOP-padding bytes;
- 46 zero bytes; and
- 4 return-tail bytes.

The earlier 72 CFG/literal overlap bytes occur in four exact pools at
`0x01b8..0x01d7`, `0x13dc..0x13f7`, `0x4b40..0x4b43`, and
`0x76cc..0x76d3`. Each is a direct PC-relative literal target located between
bounded function bodies, so literal-data precedence resolves the overlap
without inventing executable behavior.

## Licensing and limitations

The analyzer and manifests are MIT-licensed. Provider code keeps its upstream
license. CAPSENSE and Em_EEPROM remain EULA-isolated evidence/boundaries;
compiler runtime candidates require the selected runtime’s license.

Physical byte opacity is closed, but behavior/source opacity is not: 223 rows
still need exact public signatures or independent behavior recovery. The mixed
CAPSENSE/CAT2 batch should be subdivided only with stronger caller/register or
public-source evidence.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 g2/tools/analyze_g2_touch_relocated_semantics.py --write-manifests --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest g2.tests.test_analyze_g2_touch_relocated_semantics
```
