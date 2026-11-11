# R1 event veneers converted from assembly to C

Six functions in `r1/src/application/board/native_event_callbacks.c` now use
ordinary C bodies instead of naked inline assembly. The remaining assembly
callbacks in that file are unchanged. [The machine-readable review](event-veneers-c-review.json)
retains compiler/object hashes, REA bytes, replay results, qualification and
hybrid provenance.

| Entry | C behavior | Native provider |
|---|---|---|
| `0x42108` | Forward both words | `0x49068` |
| `0x421c0` | Forward both words | `0x4a5bc` |
| `0x423d4` | Forward both words | `0x4a4b4` |
| `0x42bbe` | Forward both words | `0x7c52c` |
| `0x42122` | Forward low payload byte and full length | `0x496fc` |
| `0x428b2` | Empty callback | Return |

The service symbols remain unresolved interfaces; no provider body was guessed
or reimplemented. Only services without existing C definitions were given the
visible two-word call declarations. Compiler output preserves the entire
incoming register state at the service entry, including R2/R3 beyond those
visible arguments. The byte-truncating wrapper changes only R0's upper bits.

## Object and execution checks

All 106 allocated sections in the event callback object retain identical bytes,
alignments and semantic relocation tuples. This includes the converted functions,
all unchanged functions/data and unwind sections. ARM attributes, strong symbols
and import sets are unchanged. Removed local assembler labels alter object
metadata, so whole-object hashes differ; no allocated-code change is hidden by
that statement.

The six entries pass 3,264 paired native/C replays, ending at the actual stock
service entry, its bound C counterpart, or the no-op return. Checks compare
R0–R12, SP, LR, APSR, PRIMASK, BASEPRI, CONTROL, FPSCR and S0–S31. Seed cases
vary full-word payload/length values, flags, masks, privilege state and randomized
integer/floating-register contents. Payload truncation is also checked against
its explicit expected value. There are no RAM writes and stack guards remain
unchanged. No stack frame is introduced.

Three compiled negative controls are rejected: truncating a forwarded length,
omitting the required payload-byte truncation and truncating a payload that
must retain all 32 bits. Provider implementations are not executed. This proves
the tested adapter state transitions and pre-change object preservation, not
physical service behavior or full firmware source completeness.

## Exact source-plan admission

The scoped `tools/build/qualify_sources.py` run compiles the whole source unit
but examines only the six converted functions. Other assembly functions are
excluded from qualification. Only the two-byte empty callback at `0x428b2`
passes stock qualification and is appended to the canonical source plan. The
five relocated forwarding functions remain unselected under the tested bindings,
with `anchored_relocation_pattern_not_exact` recorded. Their object-preservation
and replay evidence are kept separate from stock byte qualification.

The proposed merged plan was built and its complete application compared with
the locked artifact before canonical publication. Its source-owned `0x428b2`
region is explicitly checked. The canonical plan bytes equal that tested plan.
The no-op frontier entry is marked instruction-identical and image-integrated;
the other five entries remain behavior candidates.

A fresh hybrid has 4,273 source-built bytes, 641,887 executable pull-through bytes
and 248 resource bytes, and retains locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The newly admitted body is empty C, not an opcode array or retained executable
blob. No larger source-completeness claim follows from those two qualified bytes.

## Build audit

`make sources-check` passes. All 618 units compile (544 application, 74
bootloader); both relocatable compositions pass with no failures or duplicate
strong symbols. The other 617 objects are identical. The manifest and import
sets are unchanged: 167 application imports and 34 bootloader imports remain.

Reports: `build/sources-goal-r1-event-veneers-c/report.json` and
`build/hybrid-goal-r1-event-veneers-c/build-report.json`. The qualification,
merged-plan preview, pre-change source and full-state fixtures remain under
`build/goal-r1-event-veneers-c/`; durable receipts are in the JSON review above.

The subsequent [frontier binding repair](frontier-bindings-review.md) fixes the
scoped native-callee map. All six converted callbacks now pass qualification;
the five forwarding bodies add 22 further source-built bytes, for 4,295 total.
Two entry-only target rows carry no callee source or extent claim. All firmware
source/object bytes remain unchanged by that subsequent qualification repair.
