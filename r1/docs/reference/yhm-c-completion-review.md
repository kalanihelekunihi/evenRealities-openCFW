# YHM completion callback boundary independently checked

The native YHM completion routine at `0x50558` was absent from the current
frontier map. REA confirms a separate twenty-six-byte instruction body: close
the bus cached at context offset four, then reload the callback word at offset
zero. If nonzero, restore the caller frame and tail-dispatch with argument zero;
otherwise return the close result word. The existing C
`r1_yhm_transport_complete` follows this policy and remains unchanged.
A manual provenance supplement now anchors that C symbol to the stock entry,
enabling independent qualification attempts rather than leaving the implementation
without a native entry anchor.

Ghidra labels the recovered return type void; the instruction path still leaves
the close/callback result in R0. The execution test checks the C uint32 boundary
against those actual words, without inferring a concrete external callback
prototype solely from decompiler output.

The probe passes 1,152 paired stock/C cases (2,304 executions). It executes the
actual native/C callback setter, completion body and registry close dispatcher.
Only the close method and callback targets are modeled. Cases cover null/two
device records, missing methods, null/two callback targets, callback clearing or
replacement during close, bus-cell mutation and full-width return words. With
no callback, registry results are one for a null device, six for a missing close
method, or the method's raw result. A live callback overrides that result.

The test compares ordered context accesses, method/callback selection and
arguments, raw returns, unchanged context fields and preserved registers/stack/
interrupt masks. Callback entry must see original caller SP/LR. A deliberately
hoisted callback load fails when close installs callback B after an earlier null
word: stock invokes B, while the variant skips it.

Official qualification attempts compile all five Clang configurations and all
four supported GCC 9 configurations. None selects the completion body. Clang
rediscovers only the three previously accepted YHM spans; GCC adds none. The
canonical source plan remains unchanged, with source-built accounting 3,815
bytes in the last verified hybrid. GCC 9 Oz is omitted because the prior run
established that it is unsupported.

[Machine evidence](yhm-c-completion-review.json) binds REA, the new frontier
anchor, execution probe, negative control, qualification attempts and source
hashes. The default compiled C completion body is thirty bytes, versus native
twenty-six instruction bytes. No byte identity is claimed for it.

Firmware C, manifest and normal build inputs are unchanged. Their hashes still
match `build/sources-goal-r1-yhm-callbacks/report.json`: 571 compiled R1 units,
197 application imports and 34 bootloader imports. `make sources-check` passes.
Concrete callback signatures, private frames/caller-clobbered registers/flags,
concurrency, physical completion/IRQ behavior, complete source-only byte identity
and G2 corpus gates remain unverified.
