# Native callee bindings independent of compiled source availability

`tools/build/qualify_sources.py` now seeds its R1 application binding map from
the complete function frontier, independently of which source units a scoped
qualification run compiles. Previously, only anchors on those compilation
units entered the map. A caller could therefore lack a binding for a known
native callee whose source remains unavailable. Four-byte branch-only bodies
also correctly fail pattern recovery because they have no fixed instruction
bytes outside the relocated branch. That matching rule has not been relaxed.

[The machine-readable review](frontier-bindings-review.json) retains test,
qualification, source/object preservation and hybrid receipts.

## Binding policy and evidence

Application entries must be even and lie within the locked application image.
Other images, malformed entries and out-of-range/odd entries do not enter this
map. Duplicate names retain all their addresses so the existing binding step
continues to reject ambiguity. Thumb bit one is applied only to the resulting
call binding. Complete compiled/linked bytes must still equal stock before any
caller region is selected. The matcher and its minimum fixed-byte requirements
are unchanged.

Two missing callee entries, `0x4a5bc` and `0x496fc`, were added as entry-only
frontier evidence. Their recorded size is zero, source paths are empty, and
instruction/image-completeness flags remain false. Existing stock caller
branches identify these targets; local Thumb disassembly and REA bytes confirm
their instruction prefixes against the locked artifact. No body extent,
implementation, source ownership or source-built bytes are claimed for either
callee. The other three forwarding targets already existed in the frontier.

This lets the ordinary explicit-binding path link the previously converted
C callers at their native addresses. It does not infer implementations for
unresolved services or treat binding availability as source completeness.

## Verification

Six new binding-policy tests pass, covering unimplemented/entry-only providers,
duplicate-name ambiguity, repeated identical entries, image isolation, invalid
addresses and valid image bounds. All eleven existing source-build tests pass.
Three end-to-end qualification negative controls also pass: a wrong target, a
missing target and an ambiguous name each exclude the affected callback while
the other five remain qualified. The wrong-address case is rejected by full
linked-byte equality, without weakening the binding or matcher rules.

The scoped qualifier compiles the existing event-callback unit and examines only
the six C conversions. All six are selected. The two-byte empty callback was
already source-owned; five new regions totaling 22 bytes are added:

| Caller | Bytes | Native callee |
|---|---:|---|
| `0x42108` | 4 | `0x49068` |
| `0x42122` | 6 | `0x496fc` |
| `0x421c0` | 4 | `0x4a5bc` |
| `0x423d4` | 4 | `0x4a4b4` |
| `0x42bbe` | 4 | `0x7c52c` |

Each recovered binding is checked against that target before plan publication.
No other assembly function in the same unit enters this scoped selection. The
previous 3,264 full-state callback replays are reused only after verifying the
current event-callback object is identical to the tested object.

## Build and source-plan publication

A fresh 618-unit R1 build passes (544 application, 74 bootloader), with both
relocatable compositions successful, no failures or duplicate strong symbols,
and unchanged import sets: 167 application and 34 bootloader imports. All 618
objects, firmware sources and the source manifest are unchanged from the prior
build. `make sources-check` also passes.

The proposed plan preserves every existing unit and region and adds only the
five qualified caller regions. A fresh hybrid built with that proposed plan
matches the complete locked application before canonical publication. Canonical
plan bytes equal the tested proposed plan, and each new region's source owner
and symbol are explicitly checked.

Exact source-built coverage is now 4,295 bytes, with 641,865 executable
pull-through bytes and 248 resource bytes. Application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
All six converted caller entries are marked instruction-identical and
image-integrated; callee entry-only flags remain false. Full source-only
linking, callee implementations, and physical hardware behavior remain open.

Reports: `build/sources-goal-r1-frontier-bindings/report.json` and
`build/hybrid-goal-r1-frontier-bindings/build-report.json`. Scoped qualification,
negative controls and pre-publication plan are under
`build/goal-r1-frontier-bindings/`; durable receipts are in the JSON review above.
