# Evidence and worker contracts

Records below are specifications for the future campaign. JSON examples in
`templates/` are unfilled examples, not passing reports or an implemented
validation system. The coordinator must implement and exercise validation
before workers rely on a gate. Empty arrays, `null`, and placeholders never
imply success.

## Identity and addresses

Every record includes `schema_version`, `campaign_id`, `target_sha256`, and
the hashes of its direct inputs. An analysis record also identifies component,
nested image and address space, ISA/mode, and the mapping from file offsets to
loaded addresses. Use half-open ranges `[start, end)` throughout; numbers in
records are integers, displayed addresses may be hexadecimal in prose.

Stable function IDs derive from component + image + address space + entry
address + ISA mode, not a guessed name. Record all discontiguous body ranges,
source-byte hashes, aliases, and shared tails. If functions overlap legitimately,
record shared ownership of one span; never sum overlapping bytes twice. Different
images can reuse runtime addresses without sharing identity.

Every external target states whether it is a shipped function, hardware/MMIO,
resident ROM, dynamic dispatch, or unresolved. An external ROM entry is not
shipped pseudocode coverage; its calling contract and observed effects still
need evidence. Unknown external behavior that changes recovered semantics
remains a blocker.

## Required campaign files

| Record | Minimum content |
| --- | --- |
| `identity.json` | original bundle path/size/hash, six payload hashes, parser/extraction receipts, target lock hash |
| `images.jsonl` | all nested images, source spans, transforms, architecture, address spaces, mappings, entry/vector facts |
| `coverage.jsonl` | exhaustive non-overlapping package/payload interval classification with evidence and review state |
| `functions.jsonl` | stable IDs, entries/body ranges, instruction hash, raw/reviewed pseudocode paths/hashes, prototype and calling convention, callees/references, unresolved items and review IDs |
| `data.jsonl` | range, type/layout/encoding, exact-value evidence, referencing functions, generation requirements and unknowns |
| `interfaces.jsonl` | shared analysis types/globals, cross-image and external contracts, evidence and unresolved facts |
| `reviews.jsonl` | distinct author/reviewer IDs, input hashes, checks, pass/revise/blocked decision, exact findings |
| `receipts/` | actual argv, tool/config/script hashes, input hashes, exit codes, output hashes, scope and time |
| `freeze.json` | immutable manifest hash, component summaries, global validator/review references, unresolved counts and decision |
| `tasks/` and `results/` | individual versioned task contracts and immutable attempt outputs |

All paths in durable records are campaign-relative or repository-relative with
the root explicitly stated. No undocumented dependency on another checkout or
an agent conversation. Preserve raw outputs; reviewed interpretation is separate.
Write records atomically using a temporary file and rename; never overwrite
another attempt. Shared ledger updates have one owner and are serialized.

Use an acyclic freeze recipe: the sorted snapshot manifest lists paths and
SHA-256 values for corpus content, excluding itself, the global freeze review
and `freeze.json`. The independent global review records that manifest's hash.
The coordinator's freeze receipt binds both manifest and global review hashes.
Later invalidation records refer to the immutable freeze ID/hash; they do not
rewrite it. A gate check must consult the coordinator's invalidation registry.

## Coverage is more than a function count

Maintain package and payload ledgers separately. At each layer, spans must
partition exactly `[0, file_size)` with no gaps or unexplained overlap. Child
images are references to parent spans, not extra bytes added to the denominator.
Compressed images have separate decoded ledgers linked to their source spans.

Allowed classification kinds are `code`, `data`, `container`, `padding`, and
`unknown`. Each has evidence, owner/reviewer, and a review state. Accelerator
instructions are executable code with their own address space. Classifying a
range as non-code requires evidence such as verified referencing code, a known
container schema, or a proved alignment pattern; a failed decode is insufficient.

For each image and all six payloads, report separately:

- bytes accounted for / total bytes;
- justified non-code bytes by kind and unknown bytes;
- unique executable bytes with reviewed pseudocode / classified executable bytes;
- discovered function bodies with reviewed pseudocode / discovered bodies;
- raw decompiler success, manual recovery, partial and failed counts;
- unresolved entries, control-flow edges/dispatch rules, mappings, semantic
  unknowns, and review findings;
- later, bytes produced by admitted source, linked bytes matching target, and
  whole-payload/package equality (never infer these from pseudocode coverage).

The discovered-functions denominator must be challenged using vectors, branch
and data references, executable region sweeps, callback tables and unexplained
gaps. A ledger that labels everything is not automatically correct. G3 requires
zero unresolved executable/semantic items, complete justified non-code coverage,
and independent review of the denominator.

## Pseudocode review record

For each function or executable region preserve:

1. Exact scope/identity and source bytes hash; raw tool export and diagnostics.
2. Typed pseudocode with explicit input/output/side effects, control flow,
   arithmetic width/overflow, signedness, memory aliasing, volatile/MMIO ordering,
   calling convention, flags and exceptional paths where relevant.
3. Evidence citations: input image + offset/address/range + instruction or data
   evidence file. Separate confirmed facts, inferred names/types, and unresolved
   semantics. Cosmetic unknown names are acceptable; behavioral placeholders
   and undefined decoder intrinsics are not.
4. Callees, callbacks, global/data references and any shared-body relationships.
5. Independent reviewer decision, findings, and the exact reviewed input hashes.

Hand-written pseudocode is allowed when automatic decompilation fails, but it
needs instruction coverage and independent review. Existing generated C is raw
evidence until it meets the same criteria. Do not compile pseudocode as a shortcut
to calling it a source implementation.

## Worker task and result

Compose the common prompt, one phase prompt, and one filled task record. The
task binds target/corpus/contract hashes, required gate receipts, exact scope,
allowed read roots, exclusive write paths, mandatory evidence excerpts, allowed
commands/tool limits, dependencies, acceptance checks and stop conditions.
The task must fit one coherent reasoning unit. For analysis use one routine or
a bounded set of simple related bodies; keep an oversized routine whole and
review its control-flow regions in separate analysis records if necessary.
After G3, use a small coherent C unit with already frozen interfaces. A small
worker assignment must not omit required behavior to fit a token budget.

Worker statuses: `ready_for_review`, `partial`, `blocked`, or `stale_input`.
Only the coordinator can record `accepted` after independent review. A result
contains changed paths, artifact hashes, proven findings, validation actually
run, remaining scope, blockers with wake conditions, contract-change requests,
and the next exact action. Use a concise checkpoint before yielding. Resumption
starts by checking all input hashes, not by replaying a long transcript.

Do not run unchanged blocked tasks repeatedly. Requeue only on a relevant
prerequisite change or a specifically justified new investigation. Never convert
`partial` to `accepted` because time ran out or the file compiles.

## Write ownership and future dispatch checks

Workers only write private attempt paths. One coordinator owns global inventory,
gate records, task leases, contract promotion and integration. Each dispatch
must check target and dependency hashes, required gate validity, exclusive scope,
unresolved template fields, worker model `gpt-6-luna`, and effort `low`.

The future dispatcher must reject P4/P5/P6 work without a valid G3 receipt, reject
C production without G4, and recheck gates after resumption. The partition prompt
itself is gated by G3; generic templates here are not instantiated C tasks.
This dispatcher is not implemented in the preparation commit. Prompt text is
guidance, not an enforcement mechanism; implement the checks before dispatch.

Avoid shared Git operations from workers. Do not stage, commit, reset, regenerate
global manifests, modify reference hashes or re-pin historical tests to make a
task pass. Preserve the dirty baseline and record actual input content hashes;
a Git commit ID alone does not describe this working tree.
