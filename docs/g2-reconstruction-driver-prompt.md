# Reusable G2 reconstruction driver prompt

The runner embeds the instructions below in new assignments and resumed attempts. Its per-item hard rules, result schema, and component playbook remain authoritative. Paths below are relative to the OpenCFW repository root. Fingerprint-based scheduling and validation caches are workflow guidance, not automatically implemented runner features.

---

Improve and advance the Even Realities G2 source reconstruction using the existing OpenCFW evidence and build system. Work in bounded, resumable steps that increase maintainable, reviewed C and reduce dependence on retained firmware. Optimize useful progress and retained knowledge, not log volume, function counts, or merely compilable decompiler output.

## Scope and authority

- Use the current user request to select the work mode. In **process-review mode**, inspect evidence and propose workflow/tooling changes only; do not decompile or modify firmware. In **reconstruction mode**, select one ready work item or a bounded coherent subcluster within it. In **tooling mode**, implement only the specified workflow improvement. If no mode is specified, begin with process review and a concrete recommendation.
- Read applicable repository instructions, the **Completion conditions** and **Build and evidence tracks** sections of `g2/docs/source-only-goal.md`, and the relevant component playbook. Do not ingest the entire historical goal/progress documents. Search by work ID, symbol, component, and address; read bounded excerpts.
- Preserve existing uncommitted work. Use the existing queue writer and lock protocol. Do not start additional agents unless authorized. No hardware operations, flashing, signing, publishing, or commits unless separately authorized.
- Preserve the reference/hybrid build's documented guarantees. Source-only completion requires reviewed source and maintainable source-authored data/assets, with no stock bytes supplying functionality. Distinguish semantic evidence, compilation, production integration, hardware qualification, and release authorization.

## 1. Restore state before investigating

Read the item's latest structured result/deferred record, relevant audit, and current source registration. Locate its prior attempts only as needed. Verify the identity of the input image, component/address space, exact body range sets, source/configuration, toolchain, and relevant dependencies. Include working-tree content hashes; HEAD alone is insufficient.

Write or update a compact, provider-independent checkpoint using existing runner state where supported. If the schema lacks needed fields, retain them in a clearly linked sidecar rather than assuming unsupported fields are consumed. Record:

- Item/scope ID, attempt ID, schema version, timestamp, input and dependency fingerprints.
- Proven facts with artifact paths, addresses, hashes, and confidence; inferred or unresolved facts separately.
- Recovered signatures, structure offsets, globals, call/callback relationships, and ABI assumptions relevant to this scope.
- Completed ranges and artifacts; exact remaining segments.
- Rejected hypotheses and failed experiments, why they failed, and what new evidence would justify retrying.
- Validation receipts: command, exit status, relevant input hashes, tool versions, output location/hash, and tested scope.
- Blockers with owner or work ID where known, relevant prerequisite fingerprint, and concrete wake condition.
- Next action and expected discriminating result; active background processes and lock/output ownership.

Save atomically after a meaningful result and before a long operation or session end. Keep immutable attempt receipts and a concise current checkpoint. Logs are evidence, not the sole handoff. A fresh session must be able to continue without the previous provider's conversation.

## 2. Select work that can change the outcome

Confirm that the selected ranges remain unresolved in fresh ownership artifacts. Prefer work that unlocks multiple dependent closures, well-bounded upstream/configuration recovery, or integration of already-verified candidates.

If an item is blocked and all relevant inputs are unchanged, preserve it as waiting and select another ready item. Do not rerun the same tests to produce another identical partial report. Use the runner's supported dependency mechanism; explicitly record prerequisites that have no queue ID. Escalate unknown IDs or cycles as scheduler issues. Continue independent subsegments when they can make measurable progress.

State the bounded objective, expected useful delta, evidence needed, and stop condition. Avoid open-ended compiler or upstream searches: each experiment must distinguish competing hypotheses. Check prior negative findings first.

### Persistence within reconstruction sessions

A bounded cluster limits scope, not effort to a single search or audit. Continue through locally answerable uncertainties until that cluster has reviewed C and meaningful narrow validation, or a concrete blocker prevents further progress. Unknown semantics, unresolved local callback bodies, missing type recovery, and identifying the upstream family are reconstruction work to perform within this session. Do not stop merely because the next investigation step is now known. Checkpoints are intermediate saves, not deliverables that replace source recovery.

Do not claim progress by generating guessed C. If uncertainty prevents implementation, pursue the exact callee, caller, structure, or upstream evidence needed to resolve it. If that evidence truly cannot be obtained, identify the missing artifact or capability, record what was attempted and why available routes cannot resolve it, and return blocked with a concrete wake condition. Hardware qualification being deferred does not prevent software reconstruction and narrow validation.

Existing uncommitted work must be preserved, but its presence elsewhere in the tree is not a reason to abandon an independently scoped implementation. If an existing candidate overlaps the exact range, establish its provenance and validation, then pursue the remaining permitted review/integration work instead of repeatedly recounting its existence. Partial results are appropriate for substantive incomplete implementation or an interrupted session; an audit-only return must explain the concrete impediment to continuing. Never invent a blocker to satisfy this rule.

## 3. Recover source at the right level

Prefer identified, licensed, pinned upstream source with recovered configuration and project-owned adapters. Search the existing inventories and corpora before repeating external discovery. Treat decompiler C as evidence requiring review, not authoritative source.

Recover shared types, data ownership, calling conventions, state machines, and interfaces before translating a cluster. Preserve split function bodies and architecture/address-space distinctions. Use disassembly or p-code to resolve ambiguities in widths, signedness, aliasing, stack/register artifacts, indirect calls, and volatile/MMIO behavior.

Aim for maintainable C modules. Use assembly only with a documented architecture/ABI necessity; separately track assembly used for exact-byte reproduction and its C follow-up. Do not spend unlimited effort matching incidental compiler placement when a permitted, tested semantic implementation and relocation strategy addresses the actual goal.

For data, assets, model parameters, and accelerator programs, require an understood source representation or qualified source-authored replacement. Stock byte arrays, trap stubs, retained-provider wrappers, and unrouted candidates never count as source-only completion.

## 4. Validate incrementally, integrate against a stable snapshot

Use private output directories for candidate compilation and narrow tests. Reuse valid evidence only when all relevant input fingerprints match. Invalidate on changed headers, types, analysis scripts/specifications, configuration, compiler flags, source, or dependencies—not only changed function bytes.

Use independent stock/oracle evidence where available. Test normal and error paths, boundaries, state transitions, callbacks, ABI/register effects, and ordered memory/peripheral interactions relevant to the function. Report what host tests cannot establish.

When locally ready, record a candidate receipt. Acquire the existing integration lock for shared mutations/builds; recheck the shared snapshot and integrate only compatible changes. Prefer one coherent batch over repeated whole-package builds for individual leaves. Run all required component and admission gates for the integrated result. Inspect ELF/source ownership and remaining stock calls as well as compilation success.

If another scope breaks a shared gate, preserve successful local evidence and record integration-pending status with the exact blocker. Never change unrelated pins merely to get a green result. Release locks reliably and preserve failure diagnostics.

## 5. Report durable progress honestly

Update the runner-compatible result with its existing statuses and required fields. Keep richer milestones in the checkpoint: investigated, semantics-reviewed, compile-verified, oracle-verified, integration-pending, and production-routed. Do not invent unsupported queue status values.

Report unique stock ranges newly source-owned separately from compiled C size, reviewed assembly, generated data, and candidates. Deduplicate overlapping ranges. A row is done only when its full existing definition of done and required gates are satisfied. Keep hardware and release status independent.

Write one concise evidence delta, with links to durable artifacts. Until documentation generation changes are implemented, honor the required audit/progress/goal updates, keeping each entry brief and linked rather than copying the same narrative. Preserve failed approaches and the next exact action for subsequent sessions.

End with: objective achieved or remaining; new proven facts; useful source/semantic delta; validation actually run; blockers and wake conditions; checkpoint path and next action. Include the runner's required `CA-STATUS` line when operating under it. Never claim a proposed tool, cache, scheduler behavior, or gate exists until it has been implemented and verified.
