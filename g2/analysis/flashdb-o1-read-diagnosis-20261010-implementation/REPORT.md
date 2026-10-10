# FlashDB O1 discrepancy: finite causal diagnosis

## Immediate result

The failed equal-length O1 read is recovered by removing Unicorn's **valid memory-write hook**. An isolated exact instruction slice and a full execution without provider-redirection hooks both distinguish hook-on failure from hook-off success. Candidate source and the original O1 object were not patched. This diagnoses the tested emulator/instrumentation interaction; it does not establish general O1 equivalence or complete FlashDB correctness.

The audit report ../coverage-audit-parallel-2026-10-09/flashdb-provider-review-2026-10-10/REPORT.md was read. Its provider-free control recommendation was followed with synthetic source-owned providers only. The blocked actual FlashDB provider phase was not taken over, rerouted or bypassed. No shared Ghidra operation was used.

## Evidence

1. **trace.json** reproduces the original O1 failure requested=recorded=8. The mock find writes value address0xABC400 at local KV+84. After ITcc with false condition, source LDR at0x100076 is skipped and R1 remains key0x20020000. The first failed receipt remains sealed in the predecessor; this directory adds the diagnostic trace.
2. **isolate-results.json** executes the exact unchanged O1 instruction sequence0x100060..0x10007E, provider-free, with requested3/8/12. Four modes vary only no hooks / code hook / no-op valid-memory-write hook / both. For request8, no-hook and code-only modes load ABC400; memory-write and both modes leave R1=20020000. Requests3/12 work in all modes. This isolates a valid-memory-write hook effect even without mock PC redirection. It also explains why earlier independent instruction slices without this hook passed. No-op callbacks mutate no guest register or memory.
3. **provider-owned-results.json** repeats the three inputs with the unchanged predecessor candidate-O1.o linked to separately compiled synthetic C providers. Actual source-owned find fills the88byte object, records value_len8/addressABC400, returns true and deliberately clobbers caller-saved R1 to20020000 under valid ABI rules. Actual synthetic read records its arguments and returns FDB_READ_ERR; it does not access flash. There are no code hooks or provider-redirection hooks. With the valid-write hook absent, all three addresses are ABC400. With it present, only request8 records20020000. Length/result remain8. This rules out mock return redirection as necessary to reproduce the anomaly.
4. **recovery-results.json** executes only the affected ten get_kv and four initialized get-blob cases with the unchanged O1 ELF, no valid-write hook, existing synthetic boundary mocks, and complete final RAM comparison outside declared stack/output areas. All14 new O1 projections match the sealed original stock traces/output exactly. Stock cases were not rerun, and their baseline file/hash is retained. This is bounded recovery evidence within the single emulator, not optimization-independent or all-input equivalence.

The provider-free control is an instrumentation test, not actual FlashDB find/read/status/write implementation. Only synthetic providers were compiled. Separately compiled provider-seams.c prevents optimizer visibility into their bodies from changing get_kv. candidate-O1.o is copied byte-identically from the sealed predecessor; linking only resolves provider calls. Disassemblies and compile/link receipts are retained.

## Controls and limitations

An initial provider-visible single-translation-unit control passed with or without the hook, but compiler interprocedural knowledge changed get_kv and its find provider left R1 holding the expected address. It did not isolate the unchanged-object behavior. That confounded control remains as provider-visible-control.* and provider-owned.c; the decisive control uses provider-seams.c and separately compiled candidate-O1.o. The first synthetic fill loop required __aeabi_memset at link time; volatile byte stores removed that test-seam dependency before accepted linking. Neither change touches the pinned get_kv body or original O1 object.

The backend is the existing Linux Unicorn2.1.4 environment. The exact internal Unicorn defect and portability to other versions/backends were not diagnosed; no external issue was filed. Hook-off recovery checks final RAM state but does not provide a trace of transient stores. Mapped-boundary/code checks and unchanged-buffer checks remain. Invalid or physical addresses, actual storage, logging completion, real locks/concurrency and production build were not tested. O1 raw enum ABI observations in the predecessor are separate and remain unchanged.

Thus the old statement “O1 read discrepancy remains unexplained” is superseded only for this finite case by the hook-on/off causal evidence. The original unmodified receipt is preserved. General O1 equivalence, actual FlashDB providers, physical delivery and byte-identical rebuild remain unproved. Independent review of this diagnosis is pending.

## Preservation

Original firmware bytes are unchanged; the locked header-bearing raw image identity and original range receipts are inherited from the sealed predecessor. candidate-receipt.json binds the unchanged diagnostic ELF; baseline-receipt.json binds sealed stock projections. Preservation verifies all prior sealed files,110 audit inputs and four checkpoints, with index stable during verification. No device, production source, Git index, submodule pin or shared Ghidra context was changed.
