# Independent review: waves 066 and 067

## Verdict

The fixed wave 066 implementation is acceptable as a bounded, conservative raw-Thumb provenance analysis for the sampled operand records. I independently reproduced the earlier transparent-cycle counterexample against the fixed checker and got the expected `{1, 3}` set for both M0 entry choices; the earlier rejected implementation's `{3}` result was unsound. The replacement traverses the complete same-register predecessor graph before caching, retains an unknown function-entry seed, and turns changing-definition cycles into unknown. No new concrete under-approximation was found within the reviewed local model and sampled scope.

Wave 067 supports the narrow classification that the two remaining examples are dynamic free-list-cursor accesses in the 12 tested valid allocator/free traces. It does not prove a universal set of effective addresses or physical allocator behavior.

## Reproduction

All executions ran with `/tmp/iar-c-runtime-venv/bin/python` against a disposable copy under `/tmp/case-wave066-independent.qlMBxw`; output files and the source tree's pinned results were left unchanged. The Unicorn runs were offline Cortex-M0 emulations.

- `case-wave066-raw-thumb-model-qualification/check.py`: `COMPLETED_EXTENDED_RAW_THUMB_CFG_REVIEW 364 / 366`.
- `verify_controls.py`: `PASS 20`. This includes the exact SCC-cache counterexample (target PC `0x08000016`, R4; inference `{1,3}`) and two executions with R0=0 and R0=1. Unicorn's target R4 values were included in the inferred set.
- `verify_switch_tables.py`: `PASS_REAL_NATIVE_SOURCE_SWITCH_HELPER_TABLE_PAIRS 1 19`; one actual compact table, 16 ordinary selector values plus 255, 256, and `UINT32_MAX`, with native-helper/source-helper destination and saved-register agreement.
- `case-wave067-dynamic-heap-base-frontier/verify.py`: `PASS_12_REAL_ALLOCATE_FREE_DYNAMIC_CURSOR_GRAPHS`; three allocations and frees per scenario across four request sizes and three free orders. Native/source return pointers and RAM below the heap footer matched at every free boundary.

The independently regenerated wave 066 `verification.json`, `controls.json`, and wave 067 `verification.json` are byte-semantically identical to the producer results. Switch verification's table/case comparisons and fixture ELF hash are identical; its recorded `link_command` differs only in the disposable output path.

## Wave 066 assessment

The old 060 baseline left 106 sample records at 70 operand PCs unresolved. Wave 064's triage inventory exactly matches those records (its cause buckets overlap). The current 066 sample multiset resolves 104 of those 106 records; only `0x0800afda` and `0x0800afe6`, both for target `0x20000198`, remain unresolved. Current totals are 364/366 sample records resolved and 291/293 unique PCs with all corresponding samples resolved.

The repaired cache logic at `check.py:51-73` addresses the demonstrated SCC failure: identity-preserving predecessor cycles are traversed as a whole and visited once, while all external definitions and entry-unknowns are unioned before caching. The M0 negative controls at `verify_controls.py` also exercise both branch-entry states of that case. The fixed logic is conservative for the reviewed operations: call-clobbered registers become unknown; unsupported destinations, non-ROM loads, and changing cycles do not become constants. The 20-control suite includes supported raw semantics for extension/reversal, SP-relative effects, STM/LDM, call effects, branches, and the targeted cycle regression. Reserved/unpredictable control words are only required to yield unknown and are not treated as valid execution tests.

The switch-table verifier is grounded in raw bytes: the real `BL` at `0x08000940` reaches helper `0x08009190`; the inline count/offset table at `0x08000944` is excluded from the instruction stream and all ten derived case targets lie in the enclosing function's decoded extent. The helper is a non-returning dispatch (`BX`), and native/source fixtures agree for all 19 tested selector inputs. The test copies authenticated table bytes into fixture RAM and stops at the computed case target; it is not a production loader or a case-body equivalence test.

The updated output labels are materially clearer than the earlier target-row aggregate. `target_keys_with_at_least_one_confirmed_sample: 51` means each of the 51 target keys has at least one confirmed sample; it does **not** mean 366/366 samples or all samples under every key are confirmed. The sample booleans and the 364/366 count are the meaningful closure measures.

## Wave 067 assessment

Raw native flow at `0x0800afcc` initializes cursor R1 from the global head slot `0x20000194`; `0x0800afda` reads `[R1+4]`, and `0x0800afe6` stores `[R1+4]`. The actual source counterpart at `g2/components/case/startup_candidate_20261011/application_boot_heap_insert_candidate.c:7-25` walks and updates that cursor. In the exercised valid traces, AFDA reads both `0x20000198` and `0x20001c8c`; AFE6 writes `0x20001c8c`. This refutes a universal fixed-address claim for the head-only literal and supports the dynamic-cursor interpretation in the exercised free-list states.

The 12 fixtures start from zeroed RAM, use the real native allocator/free routines and the linked real source ELF routines, and compare all RAM below `0x20002888` at free boundaries (stack excluded). They do not explore arbitrary prior heap layouts, corrupt or invalid frees, asynchronous heap mutation, IRQ/reentrancy, or hardware. The source-vs-native event assertion compares matching phase/kind/address/value events, not source instruction PCs; full boundary-RAM equality is the stronger differential check here. AFDA/AFE6 may access other addresses in other valid heap states, so the observed sets are examples, not exhaustive address domains.

## Scope limits and remaining uncertainty

This is not a proof of the entire firmware CFG or all possible control transfers. The analysis starts from the existing Ghidra function extents, filters authenticated strings and the one recognized compact table, requires a syntactic entry-to-site path, and keeps both sides of conditional branches without reasoning about flags. Indirect control transfers are treated as exits except for the recognized table helper; this is suitable for these bounded sampled paths but does not prove that no computed transfer can re-enter a sampled extent. The checker does not establish object bounds/lifetime, whole-program code/data separation, runtime branch feasibility, exception behavior, ISR interleavings, or hardware execution. Physical IRQ/model gaps remain real.

Therefore the fixed wave 066 count is usable as a reviewed per-sample analysis result with the explicit two unresolved samples; it is not global admission, complete-source proof, physical acceptance, or firmware-wide control-flow certification. Wave 067 narrows the two remaining sites' interpretation under actual source/native traces while retaining their global runtime-address uncertainty.
