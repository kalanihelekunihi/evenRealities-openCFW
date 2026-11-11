# C NV class startup initializer

`r1_storage_manager_initialize_731a0` now supplies the manager's NV startup call in C. REA authenticates the complete 116-byte instruction body plus twelve literal bytes. It binds the existing KV port, invokes its initializer, clears the registered-class count and requests control operation 3 into an initialized base word. The port is reloaded after initialization, so replacement callbacks take effect.

The initializer iterates the existing seven live handle owners in the stock order. For each cached class it rejects payload sizes at least 232, increments the wrapping 16-bit count and rejects counts at least eight, clears key byte seven, hashes all eight key bytes with the actual hash131 implementation, writes the hash and live base, then advances. It calls the separate store bootstrap at `0x73220` after all registrations. Provider statuses and incidental void R0 residue are not consumed.

The dirty-scan unit's former private table is now the one shared const `r1_nv_handle_owners` table. No classes or handles are duplicated. All five existing function bodies, strings, pointer-table bytes/order, alignments and normalized relocation targets remain unchanged. Only the table's local/global naming changes. One new two-byte owner holds the registered count at stock `0x20006970`; native RW/ZI startup on poison with guards and an independent RW decoder verify its cold zero value. Final RAM placement remains unproved.

**3,840 stock/C comparisons** pass across payload limits, each failure position, count wrap/overflow, base values, port rebinding, live handle replacement, ignored control failures and interrupt masks. **128 additional comparisons** run the actual port record, binder and control callback, including missing-storage `0xa5a5a5a5` fallback. The port initializer and final bootstrap are modeled in that fixture. Both fixtures execute the real hash131 and shared allocation-fault primitive; assertion cases verify BASEPRI=64 and the attempted zero store at `0xffffffff`.

**2,048 stock/C dirty-scan regressions** pass over every dirty-bit mask, all logging modes and live handle replacement. Modeled service calls use real Thumb return stubs. Six compiled defects are rejected: wrong payload/count limits, wrong key terminator, wrong hash length, wrong base field and omitted final class.

All **112 reachable native instruction bytes** execute in the direct fixture. Four remaining bytes are the two self-branches after failing assertion stores; the fault accesses are observed. Normal returns restore SP and saved integer/FP registers; caller-stack guards and interrupt masks are checked. Private frame/output-pointer aliases, scratch results, APSR, concurrency and physical fault-handler behavior are excluded.

The normal build compiles **857 units**, with no duplicate strong symbols and both relocatable compositions passing. All **845 other prior nongenerated objects** remain identical. Direct/integrated startup objects and the shared-table probe object match the normal build. The manifest adds one unit; source-plan selections are unchanged and R1 source validation passes.

The initializer import closes and `r1_nv_store_bootstrap_73220` becomes explicit. Imports remain **65 application / 22 bootloader**, with a changed application import set. The lower store bootstrap, physical flash operations, full application linking and boot remain unverified.

[Machine receipt](nv-startup-c-review.json) binds code-generation audit, source providers, REA evidence, normal reports and ignored probes under `build/goal-r1-nv-startup-c/`.
