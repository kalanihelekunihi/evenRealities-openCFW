# Goodix native I/O dispatch in C

The [native calculation-dispatch review](goodix-algorithm-calculate-c-review.md) now supplies `GH3X2X_AlgoCalculate` in C, sharing the canonical started/frame/init owners. Its five engine executors remain explicit unfinished providers; this closes only the outer dispatcher.

The I/O dispatcher behind the registered frame hook now implements the recovered stock policy in `r1/src/application/goodix/native_io_dispatch.c`. Its header leaves a declaration at the vendor template replacement site in the generated hook unit. C handles the post-algorithm function-ID reload, result readiness gates, seven callback routes, live pointer reloads, pairwise unsigned reductions and logging arguments. The algorithm itself remains an external provider.

## Isolated source owner, 2026-11-11

The dispatcher and its private preparer moved from the generated hook unit
into `native_io_dispatch.c`, with one manifest unit and the same Goodix Clang
profile. The generated unit's other function bodies match their prior object
bytes. The isolated object SHA-256 is
`c87d25a22c540f214e2b7582a35cfbe644105a5fcc691f5cfc45e67bfbfb36b4`.
Its 492 paired dispatcher and 432 real callback integration cases pass using
the production object, including the native frame, live registers, ordered
RAM accesses and output. The results are under ignored
`build/goal-r1-goodix-io-stepper/isolated-results.json` and
`isolated-integrated-results.json`. The fresh 1,046-unit source build and
strict links pass at `build/sources-r1-io-isolated-fixed-20261111/report.json`,
`build/r1-link-io-isolated-fixed-20261111/report.json` and
`build/r1-boot-link-io-isolated-fixed-20261111/report.json`. The application
uses 693,752 of 696,320 flash bytes. The fixed-frame transfer adapter still
contains inline assembly; this isolation makes its eventual C replacement
reviewable without recompiling the other generated hook bodies.

An ignored pure C prefix probe under `build/r1-goodix-io-pure-c-20261111/`
kept a 208-byte scratch array live across `GH3X2X_AlgoCalculate`. Cortex-M4
replay confirmed the first provider received the stock function word and
`entry SP-216`, with the same single four-byte frame read. Earlier direct C
probes used `entry SP-232`. This prefix stops at the first provider: it does
not establish the dispatcher routes, active saved registers, outgoing stack
arguments, alias ordering, or final return. The production transfer adapter
remains the passing implementation for those checks.

A fixed-frame transfer adapter preserves the native 216-byte outer frame: saved R4/R5/R6/LR plus 200 scratch bytes. A private C preparer returns before each provider call; the adapter restores native SP and the required live register state, or restores the caller frame for a tail transfer. Outgoing words are written to native scratch in stock order, including before later reads that may alias those words. No C plan survives across provider calls. This adapter retains 188 bytes of assembly; the policy preparer is 596 compiled C bytes under the recorded profile. This is not a claim of assembly-free code or byte identity.

An ignored C-only stage-splitting probe at
`build/r1-goodix-io-tail-c-20261111/receipt.json` compiled with the R1 Clang
target. A 208-byte scratch array with a `musttail` transfer makes both
provider stages enter at caller SP minus 216; a separate 200-byte scratch
probe makes Clang save R4/R5/R6/LR, matching the stock frame's *shape*.
Neither probe is a dispatcher replacement. The first clears scratch between
provider calls, and the second fills R5/R6 from C locals rather than
preserving the incoming register contents. The full 492-case provider and
alias fixture has not been run on a combined stage design. The next C design
must preserve live callee-saved contents, outgoing stack aliases and return
paths as well as the frame depth.

A further ignored full-policy C probe, using the same 180-byte log buffer and
corrected minimum reductions, still misses the first provider boundary. The
Clang source profile enters `GH3X2X_AlgoCalculate` at caller SP minus 232;
GCC 15 at `-O2` with R7–R9 reserved enters at minus 224. The stock and the
minimal 208-byte C prefix enter at minus 216. The existing strict 492-case
fixture rejects the full-policy Clang object on its first algorithm-provider
SP assertion. Receipts and candidate sources are under ignored
`build/r1-goodix-io-pure-c-20261111/`. Thus neither direct full C function
can replace the production adapter without a different frame/control design.

The earlier direct-C probe used 232 bytes (264 for Og), while the template supplied no frame. The new adapter closes that first-provider counterexample and the bounded dispatch fixtures below. A callback-only SP comparison would be insufficient; the tests also compare active saved-register state, outgoing arguments, scratch snapshots and RAM access order.

Verification against `build/sources-goal-r1-goodix-io-stepper/report.json`:

- 492 paired stock/C cases compare the full recorded tuple: provider order/arguments/SP, live R4–R11, interrupt masks, ordered RAM accesses, output state, the 216-byte frame and actual return bits. Cases include exact IDs versus combinations, status bytes, zero/high-bit results, optional callbacks/loggers, callback mutations, raw/result/stack aliases and selector bytes. Providers clobber 80 bytes of private stack to verify the preparation plan is not live during calls. Paired RAM accesses are compared as ordered four-byte words; invalid pointers/fault contexts and concurrent memory access are outside this proof.
- 432 paired cases execute the seven actual C stream-cache callbacks against stock callbacks, checking final 240-byte cache contents, append saturation, signed clamping and six-word arguments. Only the algorithm is modeled; loggers are disabled in this integration fixture and covered by the separate unit fixture. Callback code addresses differ, so slot identities/arguments/output data are compared.
- Wrong raw reduction, deferred outgoing-argument stores and omitted tail-frame restoration variants are rejected.
- All 576 units compile without failures or duplicate strong symbols. Import sets remain 167 application and 34 bootloader. All 575 unrelated objects and 15 other hook functions are byte unchanged. The new twelve-byte extrema array is NOBITS/aligned four and belongs at native `0x2002fd1c` within the recovered zero-initialized interval; final source-only placement remains a linker requirement. The selector at `0x20006c34` remains an opaque read-only recovered byte.

The strict fixture corrected an earlier analysis error: raw words 4/5 use **minimum**, not maximum. All three stored pair reductions are minima, ordered pairs 0/1, 4/5, 2/3, and the pointer callback receives output addresses +0/+8/+4. The rejected maximum counterexample is retained in the receipt. The prior unintegrated probe was only tested to its first provider call and never validated this policy.

A manual entry supplement records the 336-byte dispatcher code at `0x6a320..0x6a46f`; its adjacent 64-byte literal data is separate evidence. The native frame hook's tail target establishes its identity. This adds no accepted global inventory/pseudocode coverage or G2 gate credit.

Four Clang and four GCC9 qualification candidates compile and select nothing. The same 492 unit cases and 432 real-callback integration cases also pass with the GCC9 dispatcher object (the cache callbacks retain their normal Clang build). The dispatcher is a bounded source candidate, outside the exact source plan. The canonical hybrid remains equal to locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, with 3,945 source-built bytes, 642,215 fallback bytes and 248 resource bytes. Physical sampling, real algorithms/logging, invalid-pointer exception state, full source-only linking and global source completeness remain unproven.

[Machine-readable evidence](goodix-io-dispatch-c-review.json) binds source/generator changes, original metadata, counterexamples, probes, audits, qualification and hybrid output. Experiments remain under ignored `build/goal-r1-goodix-io-stepper/`.
