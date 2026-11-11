# Goodix I/O dispatcher: recovered policy and frame counterexample

The native I/O dispatcher at `0x6a320` is a remaining hardware-data-path dependency behind the checked frame wrapper. It first loads the function ID at frame offset zero and calls `GH3X2X_AlgoCalculate`. It then reloads the ID, so callback/algorithm mutations must be observed. Dispatch uses exact IDs, not independent bitmap tests.

The pinned template currently only calls the algorithm. A C policy probe now expresses the recovered dispatch, but is **not integrated**: an executed first-call counterexample shows native reserves 216 bytes, the current template reserves zero and the probe reserves 232. The algorithm argument and single four-byte frame-ID read agree in all three. Matching these inputs does not repair the observable stack contract. Clang O2/Os/Oz and GCC9 Os use 232 bytes; Clang Og uses 264. The strict first-call fixture executes all five probes; these are not full dispatcher tests.

The native callback table is at `0x20007b8c`, eight four-byte words:

| Function ID | Slot | Arguments and gate | Provider SP |
| --- | --- | --- | --- |
| `1` | 6 | Raw pointer from frame+20, then raw word 0; only callback must be nonnull | caller SP, tail |
| `2` | 0 | Result pointer from frame+60; byte 0 must equal 1, callback nonnull, word at +4 nonzero; pass words +4/+8/+12/+16 | caller SP, tail |
| `4` | 7 | Same gate; pass result words +4/+8/+12/+16/+20/+24 | caller SP−216 |
| `8` | 1 | Callback nonnull; pass first two raw words from pointer frame+20 | caller SP, tail |
| `0x40` | 2 | Same six-word result gate/arguments as ID 4 | caller SP−216 |
| `0x2000` | 4 or 5 | Compute extrema below; choose slot 4 for selector zero, slot 5 otherwise; pass extrema pointers in order +0/+8/+4 | caller SP−216 |

Slot 3 is not read by this dispatcher. IDs `0x80`, `0x200`, `0x400`, combinations and other unlisted values perform no dispatch after the algorithm call. Null metadata/raw pointers are not guarded before required native loads; a reconstruction must not silently add a different fault policy.

For `0x2000`, the raw pointer is read from frame+20. Native loads paired raw words in order 0/1, 4/5, 2/3. It stores unsigned min(0,1), min(4,5), min(2,3) into three words at `0x2002fd1c`, in that order. The selector is the byte at `0x20006c34`; its higher-level owner is not established here. The pointer callback can mutate state before logging.

Logging samples `g_pSnprintfUserIn` at `0x20007b04`; if nonnull, it clears only 180 bytes starting at native SP+20. It reloads the raw pointer, loads raw words 2–5, then 1, then 0, and reloads the formatting pointer before calling it. Arguments are buffer, size 180, the stock six-integer format and raw words 0–5. It calls the platform-log seam at `0x2a9d2` afterward. The print pointer at `0x20007b00` is sampled later; its raw arguments load words 3–5 before 0–2. These reloads and store/load ordering matter for mutation and alias fixtures.

The 216-byte frame consists of saved R4/R5/R6/LR (16 bytes) and 200 scratch bytes. Scratch +0..19 holds outgoing arguments; +20..199 is the formatting buffer. Nothing initializes this scratch before the first algorithm call. Four- or fewer-word tail providers enter after frame restoration. Six-word callbacks and pointer callbacks use the live frame. Simply accepting a larger C frame, normalizing SP or zeroing scratch would not prove the native contract.

The ignored probe directory contains a compiling C policy candidate and a strict native/template/five-probe frame fixture. The fixture stops at the first algorithm-provider entry; it does not validate the candidate's callback/logging behavior. No firmware source, manifest, source plan or byte-coverage credit changed in this analysis round. Physical sampling, full dispatch, alias/fault behavior and source completeness remain unproven. This evidence identifies the next implementation problem: preserve the native frame and provider transfers while moving the full policy into C.

## Split-frame C probe, 2026-11-11

A later ignored probe under `build/r1-goodix-frame-c-20261111/` moves the
temporary 40-byte plan into a completed helper call, leaving a 200-byte
scratch array live in the outer C function. The current R1 Clang profile
then emits `push {r4,r5,r6,lr}` plus `sub sp,#200`: the first algorithm
provider enters 216 bytes below caller SP, with the same input word, one
four-byte frame read, and saved-register stack area as stock. The focused
stock/C first-provider receipt is `compare-first-provider.json`.

This does **not** replace the production adapter. At that provider entry,
the C probe has repurposed live R5 for `frame+20` and R6 for scratch SP,
whereas stock leaves both incoming register values live. The probe's
`match_saved_registers` check fails even though its frame depth, input and
stack-save bytes match. A complete C replacement must also preserve that
register handoff and the later callback and formatting transfers; matching
only the 216-byte stack depth is insufficient.

[Machine-readable evidence](goodix-io-dispatch-analysis.json). Probes: `build/goal-r1-goodix-io-dispatch/`; authoritative raw disassembly: `build/goal-r1-goodix-frame-hook/io-assembly.txt`. Existing REA grouped listing is bound in the receipt; it includes tail-target bodies and is not a global inventory proof.

Correction from the later strict implementation fixture: the raw 4/5 pair also
uses minimum, not maximum. The earlier unintegrated C probe was not a policy
validation. The [C dispatcher review](goodix-io-dispatch-c-review.md) preserves
the counterexample and verifies the corrected operation.
