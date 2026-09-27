# Procedure and gates

This is a procedure specification. All phases below are future work; preparation
does not authorize starting them. Gate reports must be backed by files and
checks, not by changing a boolean in `state.json`.

## P0 — Preparation (this reset)

Organize the repository, preserve the existing working tree, identify the
reference artifact from existing metadata, and prepare prompts and contracts.
Do not decompile, produce C, create implementation chunks, rebuild firmware,
or run worker prompts. A hash check of existing files is an identity check,
not a new decompilation result.

## P1 — Authenticate and inventory the whole artifact

When the user requests execution, the coordinator first establishes an isolated
campaign with a unique ID under `g2/build/pseudocode-first/<campaign>/`.
Build and verify the campaign's record/coverage validator before dispatching
decompilation work. Use existing parsers only after inspecting what they read,
write, and assume; never use an old build target simply because its name sounds
appropriate. Do not resume saved incremental-reconstruction sessions.

Authenticate the original bundle against `target.json`. A missing whole bundle
blocks P1 even when all six extracted payloads match. Bind the actual local
bundle path and hash in an identity receipt; never select a reconstructed
bundle solely because it has the same version. Preserve the input read-only.

Parse the outer container and recursively enumerate the six payloads, record
tables, nested images, secondary/backup programs, loaders, and embedded
accelerator instruction streams. Validate bounds and checksums. Preserve a
reversible map from package offset to payload offset to loaded address for
each address space and image. Verify decompressed/relocated representations
against their source spans. Never treat a package offset as a runtime address.

| Payload ID | Existing reference payload | Inventory concerns to check |
| --- | --- | --- |
| `apollo_main` | `ota_s200_firmware_ota.bin` | headers, vectors, application code, libraries, resources and any embedded executable payloads |
| `apollo_bootloader` | `ota_s200_bootloader.bin` | container layout, reset/exception paths, boot code, tables and external resident calls |
| `ble_em9305` | `firmware_ble_em9305.bin` | ARC address spaces, record metadata, application code and external ROM interfaces |
| `codec` | `firmware_codec.bin` | FWPK/BINH nesting, every boot stage and image variant, C-SKY code, DSP/NPU programs and model data |
| `touch` | `firmware_touch.bin` | wrapper, Cortex-M code, vectors, configuration and resident ABI |
| `case` | `firmware_box.bin` | wrapper, STM32 code, vectors, tables and runtime initialization |

These are inventory prompts, not an assertion that the old address maps are
complete. Confirm architecture, endianness, ISA mode, load mapping, and decoder
support from evidence for each executable image. Reconcile existing corpora by
input hashes, tool settings, body ranges, and actual file presence before reuse.
Source candidates and upstream libraries are leads, never the oracle.

**G1 / TARGET_AND_INVENTORY:** whole bundle and payload hashes match; all
container spans are accounted for; every nested image has an explicit mapping;
an initial byte ledger and architecture-specific analysis plan exist. Uncertain
code/data spans may remain explicitly unknown at G1 and must be resolved in P2.
No C task decomposition is created here.

## P2 — Complete pseudocode recovery across the whole artifact

Create canonical analysis projects per architecture/address space from the
authenticated inputs. Pin decompiler version, processor specifications and
their hashes, scripts, options, timeout settings, and project input hashes.
Keep the raw output unchanged and the reviewed pseudocode in separate files.

Parallel work here is **analysis coverage**, not C module planning. Assign
bounded, non-overlapping function/body or image ranges for exporting, repairing,
and reviewing pseudocode. A worker can read callers/callees outside its assigned
write scope and report new discoveries to the coordinator. One owner updates
the global inventory and shared analysis facts. Workers use private project
copies and output directories; do not share writable decompiler databases.

Cover startup, vectors, interrupts, error paths, library/runtime code, unreachable
but shipped code, veneers, thunks, split bodies, switch targets, callbacks,
indirect branches, copied-to-RAM code and embedded accelerator programs. Failed
decompiler output needs repair or instruction-backed manual pseudocode with an
independent review. Unsupported ISA features block coverage; they do not become
“data” to make a report pass.

Pseudocode must express operations and control flow with explicit widths,
signedness, calling convention, memory effects, flags and special registers
where relevant. Keep uncertain names provisional. Resolve behavioral ambiguity,
including indirect target sets or proved runtime dispatch rules. A comment
such as “calls helper,” an opaque intrinsic without defined semantics, or an
unexplained `unaff_*` value is not complete pseudocode.

Describe all non-code content: typed tables, constants, strings, fonts, models,
assets, padding, checksums and container fields. Record exact values and source
provenance where needed; do not invent behavior for data. A faithful literal
data representation may be necessary for byte identity, but opaque executable
bytes encoded as arrays, `.incbin`, assembly words, or a translator are not C
source reconstruction. Unknown data meaning that affects code behavior blocks
review. Known but difficult asset/source generation work is explicitly carried
forward to the post-freeze data reconstruction queue.

**G2 / PSEUDOCODE_COMPLETE:** for every image, independently reconcile discovered
entries, references, vectors, code regions, and the byte ledger. Every executable
span has reviewed pseudocode, every payload and package byte has a justified
classification, and no failed/partial/unknown executable region or unresolved
behavior remains. Report the distinct coverage measures in `CONTRACTS.md`.
Preexisting function counts and “decompiler succeeded” are not completeness
proofs. Completeness is a reviewed claim tied to this exact artifact and analysis
model; later counterevidence invalidates it.

## P3 — Independent review and immutable corpus freeze

A different worker reviews each analysis unit against the original bytes and
instruction-level evidence. The coordinator reconciles seams: shared tails,
overlapping functions, callbacks, global state, data references, and cross-image
interfaces. Review the global denominator as well as individual function text.
All six payloads must pass together. A completed component cannot advance to C
while another component is incomplete.

Generate a deterministic corpus index and SHA-256 manifest covering raw exports,
reviewed pseudocode, function records, byte ledgers, data descriptions, call and
reference graphs, shared analysis types, tool receipts, and review decisions.
Preserve qualified external ROM interfaces separately from artifact coverage.
Freeze with a versioned receipt containing the official artifact hash, corpus
hash, six component summaries, validator output, and independent review IDs.

**G3 / CORPUS_FROZEN:** G1/G2 evidence is present and validated, the global review
passes, and an immutable freeze receipt exists. Workers cannot self-certify
this gate. No empty template, old queue, old corpus count, or manually toggled
flag may open it. This is the first point at which C decomposition is allowed.

If missed code, incorrect mappings, or unresolved semantics are discovered after
freeze, invalidate G3, park dependent C assignments, repair/review the corpus,
and issue a new freeze version. Reuse unaffected evidence only after comparing
its full input and dependency hashes.

## P4 — Derive implementation chunks and freeze C contracts

Now use the complete corpus to establish data ownership, ABI/layout contracts,
module seams, and a dependency graph. Group strongly connected functions and
shared state when that avoids artificial interfaces. Separate toolchain,
linker/startup, deterministic data generation, and container serialization work
from ordinary C modules. Link every task back to frozen function/body IDs and
data ranges. Do not reuse arbitrary AM/CD/etc. range batches from the old queue.

A single contract owner publishes headers, exact widths/layouts/calling
conventions, external ROM contracts, symbol/address requirements, linker regions,
and compiler profiles. Parallel workers receive immutable contract snapshots.
Contract changes return to that owner and invalidate affected tasks; workers
must not independently “fix” shared headers or expected bytes.

Recover compiler/assembler/linker versions, optimization and ABI flags, library
variants, ordering, alignment, startup behavior and padding requirements using
bounded, evidence-based experiments. Matching behavior does not guarantee
matching bytes. If original compiler output or non-reproducible signing inputs
cannot be recreated, report that exact blocker; do not silently relax the goal.
Architecture-required assembly must be explicitly scoped and disclosed. It
cannot disguise unrecovered code; a strict all-C claim remains unmet if assembly
is required. Keep any exception separate for the user to decide.

**G4 / IMPLEMENTATION_READY:** validated G3, exhaustive ownership with no gaps
or conflicting writers, pinned shared contracts, resolvable task dependencies,
and bounded acceptance checks for every task. Start with a small calibration
batch (for example two workers), review its outputs, then increase concurrency
only within the environment's capacity. Workers use `gpt-6-luna`, effort `low`.
If a unit repeatedly needs missing context, split or improve its contract;
never silently change the requested model or reasoning effort.

## P5 — Parallel C reconstruction and serial integration

Implement explicit C semantics from the frozen pseudocode and corroborating
instructions. Use independently identified upstream source when it actually
matches the required behavior/configuration; do not force a convenient version
into an exact-match claim. Review legacy candidates against the same contract
before reusing them. Compile in private directories against the locked headers
and toolchain. Validate corner cases, memory/ABI effects, ordered I/O, callbacks
and errors with evidence independent of the new C. State what each test proves.

Return C, data generators/source assets, narrow checks, relocatable object
receipts and a compact result. The coordinator alone integrates accepted units
into a stable snapshot and runs component-level linking/layout checks. Final
linked bytes, including relocations, matter more than pre-link object bytes.
Workers cannot change reference pins, build manifests, global queues, or the
freeze receipt. Partial results remain partial; unchanged blockers are parked
until relevant prerequisites change.

**G5 / SOURCE_COMPLETE:** every executable span is produced by reviewed source,
all required data/assets/metadata have reviewed deterministic source inputs,
all symbols and dependencies resolve, and linked component checks pass. No
stock executable extraction, retained provider, dummy return, trap, opaque
opcode representation, prebuilt library supplying recovered code, or donor
patching is in the build dependency graph.

## P6 — Exact full-bundle reproduction

Build in a clean isolated workspace with only admitted source, assets,
dependency source, pinned tools and configuration. The compiler/packager must
not read the original firmware or historical generated binaries. Keep the
oracle accessible only to a separate comparison step; capture the build input
manifest and actual dependencies, not merely a claim that no blob was used.

Reproduce payloads and every container field: entry order, names, offsets,
lengths, endian encoding, timestamps, compression, padding, checksums and any
authentication fields discovered in P1. Authentication/signature bytes must
have an explicit provenance and reproducibility decision. Copying an opaque
signed envelope can prove repackaging, but cannot prove that the entire package
was generated from source. Record an unavailable signing input as a blocker if
generation requires it; never imply it can be recovered from pseudocode.

Compare each payload and the whole output to the immutable official oracle
using direct byte comparison, sizes, SHA-256, and offset-level mismatch reports.
Resolve codegen, ordering or serialization differences instead of re-pinning
the expected hash or patching the result with donor bytes. Perform two clean
builds and compare them to each other and the target.

**G6 / IDENTICAL_SOURCE_BUILD:** G5 and all input-provenance checks pass; both
clean runs reproduce all six payloads and the complete 4,301,227-byte bundle
with SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`
and byte comparison reports equality. Keep the build recipe, dependency locks,
source-to-range ownership, comparison receipts, and limitations together.
Hardware operation and publication are separate activities, not part of these
preparation or reconstruction instructions.
