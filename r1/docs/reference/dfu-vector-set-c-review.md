# R1 DFU bootloader vector handoff in C

The linked `native_dfu_vector_restore.c` unit now supplies
`nrf_dfu_svci_vector_table_set`, corresponding to stock entry `0x78590`.
The upstream SDK unit was excluded to avoid duplicating the reconstructed
restore function, leaving the set provider unresolved. Both linked providers
now live in the existing reconstructed unit; no new compilation unit was added.

Stock reads the word at `0xff8`, falling back to UICR `0x10001014` only when
that word is `0xffffffff`. If both are erased it logs the missing bootloader
and returns 4. Otherwise it retains the selected value across logging, passes
it unchanged to SVC19, logs any failure and returns the full status. The C code
preserves this policy, including zero, unaligned and other non-sentinel values;
it adds no inferred validation or fallback. Architectural supervisor-call
assembly remains in the existing helper.

REA/Ghidra read the stock body, literals and strings. The production object
passed 2,912 paired stock/C cases with an independent trace oracle: primary and
fallback boundaries, full-width SVC statuses, all eight constant log modes,
changing log-mode sequences, provider changes to both address words, and both
PRIMASK settings. Checks cover ordered address reads, short-circuited mode
queries, log classes/text/arguments, SVC19 arguments/status, return value,
restored SP/callee registers and interrupt masks. Five deliberate fallback,
missing-status, reread-address, failure-gate and log-class errors were rejected.

Stock provider/SVC depth is 24 bytes; C depth is 8. Provider frames, live callee
register values, nonargument caller-clobbered values, private spills and APSR
are not equated. Logs and SVC19 are modeled. No real SoftDevice vector change,
exception frame, bootloader entry or physical DFU operation is proven.

The full R1 build compiles and composes 590 units without known failures or
duplicate strong symbols. Application imports fall from 164 to 163; bootloader
imports remain 34. The other 589 objects are unchanged. All prior allocated
sections and relocations in the changed unit remain unchanged, protecting the
existing restore implementation and data.

Exact-body qualification selected nothing. The source plan is unchanged, and
the hybrid application retains locked SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`:
4,245 source-built, 641,915 binary-pull-through and 248 resource bytes.
Compilation and bounded behavior do not establish a complete source link or a
byte-identical source rebuild.

The [receipt](dfu-vector-set-c-review.json) records exact inputs and results.
Ignored reproduction scripts are under `build/goal-r1-dfu-vector-set-c/`;
current reports are `build/sources-goal-r1-dfu-vector-set-c/report.json` and
`build/hybrid-goal-r1-dfu-vector-set-c/build-report.json`.

The handwritten SVC wrapper in this historical review is superseded by the
[pinned Nordic C API](dfu-sdm-c-review.md), tested for both set and restore paths.
