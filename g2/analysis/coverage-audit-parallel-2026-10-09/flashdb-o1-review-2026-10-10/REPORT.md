# Independent O1 synthetic/emulator diagnosis review

PASS for finite causal diagnosis. Independently replayed12instruction-slice controls (3requests×4hook modes),6synthetic-provider full executions (3requests×hook on/off), and14O1 projections against sealed stock receipts. Twenty-five checks passed. Unchanged ELF/object and baseline bytes independently verified. Blocked actual-provider work was neither executed nor extended; providers here are explicitly synthetic test seams.

## Causal claim accepted

For requested=recorded8, no-hook and code-only slice modes loadABC400. Valid-memory-write-hook and both modes leave R1=key20020000. Requests3/12 succeed in all modes. No-op write callback changes no guest data; paired controls vary instrumentation only. Thus the observed failure causally depends on valid-memory-write instrumentation in this environment, not optimizer source semantics or necessary provider PC redirection.

Separately linked unchanged candidate-O1.o plus synthetic source-owned find/read reproduce hook-on failure and hook-off success without code/provider-redirection hooks. Find fills an88byte record and deliberately clobbers caller-savedR1 under normal ABI rules. Read only records arguments and injected error; it does not read flash. Separate compilation prevents provider visibility from altering the original candidate. Confounded single-translation-unit success is appropriately retained and excluded from the causal proof. Synthetic status/write seams are not actual FlashDB implementations.

Hook-off14get/blob projections match sealed baseline exactly, including return/output/trace and termination/SP. This supersedes the previous 'unexplained' finite read failure with an instrumentation-dependent diagnosis. It does not prove all O1 builds, source revisions, other backends or actual provider behavior. Exact Unicorn internal defect and version portability remain unisolated; no general bug claim follows.

## Write-guard tradeoff

Removing UC_HOOK_MEM_WRITE removes per-store range enforcement. Owner recovery compares all1MiB RAM outside output[20040000,20040014) and stack[200FEF00,200FF004) after execution, retains output/BUF/HDR checks, and checks code PCs against recognized bodies/boundaries. This catches lasting unauthorized RAM changes, including hook-provider writes, but cannot detect transient out-of-range writes restored before return, writes storing an identical value, or reads from unvalidated mapped areas. Stack scratch contents are allowed; no exact maximum stack watermark is recovered. These properties differ from the earlier per-write guard and must not be called unchanged instrumentation coverage.

Owner final-RAM guard omits mapped firmware[438000,798000), candidate[100000,110000) and return-sentinel[800000,801000). Audit recover-guarded.py additionally snapshots and compares all three regions, without introducing the problematic write hook. All14cases pass (recovery-guarded-log.txt). This closes lasting executable/sentinel mutation for those cases, but still does not supply a transient store trace or general memory safety. A separate backend or instrumented execution outside this defective hook configuration would be needed for equivalent per-store evidence.

## Remaining boundary

The finite O1 anomaly is sufficiently diagnosed for these receipts; no additional repeated constructor/configuration/provider fixture is needed to restate this result. Preserve original failure and unchanged candidate. O1 raw enum ABI discrepancy remains a separate deliberately invalid-provider projection. Broad optimization-independent source identity, complete FlashDB, physical flash delivery, canonical source admission and byte equality remain unproved. Actual-provider phase stays pending access resolution.

Artifacts: replay-bundle.json exact controls/recovery, checks.json, three replay scripts, recover-guarded.py and recovery-guarded-log.txt. Owner report: g2/analysis/flashdb-o1-read-diagnosis-20261010-implementation/REPORT.md. No Git, source/payload, canonical ledger, device or shared GUI changes.
