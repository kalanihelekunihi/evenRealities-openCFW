# Checkout rescan

Compared with the 21:50:48 UTC scan, foundation C/header files increased from 59 to 71: 12 additions for GPIO configuration/state/interrupt control, radio wrappers and WSF timer cancellation. All 59 earlier source hashes remain unchanged; changed earlier sources: 0; removed: 0. File counts include interfaces and compatibility headers, not just recovered firmware functions.

The cumulative comparison ledger increased from 4,166 to 5,174 distinct original instruction bytes (+1,008): GPIO configuration +156, state/radio idle +242, interrupt control/radio integration +480, and timer cancellation +130. This is bounded original/source execution evidence, not whole-image coverage or compiled byte equality.

Current saved timer comparison: PASS 2,624 cases/500 original instruction bytes. Its independent review records 13 representative reruns. Current GPIO and control regressions: PASS 16,108 and 6,648 cases. All three saved source manifests and ELF bindings were checked against disk; see snapshot.json for exact results. The saved aggregate completed 43 modules: 224 method tests, 218 passing, six method skips and one setup skip, zero failures/errors. No tests, builds or emulation were rerun for this scan.

Useful new behavior: timer cancellation unlinks a found timer and clears its started byte, but retains allocation and its next pointer; an absent timer retains its started flag. WSF critical sections use a wrapping byte nesting counter and do not restore an unrelated incoming PRIMASK. The recovered caller orders timer cancellation before radio GPIO shutdown. Asynchronous expiry/callback lifetime and full shutdown remain unproven.

New source paths are not ignored and remain untracked. The simulator ELF is ignored by `.gitignore:15` (`build/`). Committed-only and staged-only views therefore miss real source additions; ignore rules explain hidden build artifacts, not absent sources. The timer analysis currently has disassembly, comparison evidence and independent review, but its top-level narrative/provenance closeout remains unfinished.

Optimized tick remains BLOCKED by the preserved instrumentation-sensitive Unicorn execution limitation; the passing timer profile does not clear it. Zero fully source-complete firmware payloads and no source-built byte-identical bundle are established. Whole-image percentages were not remeasured.

This scan wrote only this report and its snapshot. It changed no firmware/source, staged or committed nothing, and preserved existing work.
