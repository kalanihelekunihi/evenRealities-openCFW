# RTC open bridge replaced by direct C

Current implementation: [ordinary C operation ABI](rtc-open-pure-c-review.md). The historical scratch-register contract described below has been retired for the C firmware target.

The `r1_native_rtc_open` candidate at stock entry `0x56318` now has one direct C body in `r1/src/application/board/native_rtc_lifecycle.c`. Its ten-byte executed assembly bridge and private `rtc_open_body` worker are retired. The lifecycle module has no naked functions or nonempty assembly instruction strings. Fixed R2/R3 declarations and two empty compiler constraints remain: this is compiler-specific C, not portable ISO C.

Stock saves R2/R3 in its 24-byte frame and restores them on every return. First-open initialization overwrites those words with its eight-byte configuration, so provider mutations must also reach the returned registers. The C local union preserves both paths. Recorded Clang uses eight local bytes and sixteen saved bytes; scoped GCC9 uses sixteen local bytes and eight saved bytes. Private save slots differ. Both place the configuration at caller SP minus 24 and call the comparison, initialization, returning error, tick-enable and enable providers at that same depth. The caller name is loaded before the live record name; the opened byte is read after comparison.

REA read the complete 132-byte envelope (118 instruction bytes, two padding bytes and twelve literal bytes) and the eight default bytes at `0x9a638`. The raw application hash is checked by the executable fixture. These observations do not establish REA procedure analysis for this entry.

Recorded Clang and scoped GCC9 each passed **819 paired cases / 1,638 executions** against stock: 810 open cases and nine registry-registration cases. Cases vary name comparison, opened state, returned initialization status, comparison mutations, full configuration mutations and five full-width R2/R3 seed pairs. Checks include provider order, configuration contents and address, open-provider stack depth, R0/R2/R3, R1/R12, shared record state, final callee-saved registers and interrupt masks. Registry operation roles are checked; exact registration-provider stack depth is excluded.

The fixture rejects zeroing output R2, returning the wrong configuration word through R3, and the previous bridge plus private C worker, whose nested provider depth differs. An earlier GCC candidate with a sixteen-byte total frame was also rejected. SDK, comparison, returning error and registry providers are modeled. Active provider saved-register values, flags, return-address bits, faults and physical devices remain outside this proof.

All 576 normal source units compile and compose without new failures or duplicate strong symbols. Application/bootloader imports remain 164/34. All 575 other objects and six other lifecycle functions are unchanged against the preceding epoch-C report. Four generic and four scoped GCC9 qualification profiles compile, but select no exact regions. GCC qualification alone adds `-Wno-unused-parameter` for Nordic SVC headers; normal manifest flags are unchanged.

The canonical hybrid still matches the locked application hash with 3,961 source-built bytes, 642,199 executable fallback bytes and 248 resource bytes. Source completeness remains false. Compilation and bounded behavioral agreement do not admit this function to the exact source plan or establish hardware operation.

Machine-readable evidence: [rtc-open-c-review.json](rtc-open-c-review.json). Reproducible local probes and negative controls are under ignored `build/goal-r1-rtc-open-c/`; the current normal report is `build/sources-goal-r1-rtc-open-c-final/report.json` and the canonical report is `build/hybrid-goal-r1-rtc-open-c/build-report.json`.
