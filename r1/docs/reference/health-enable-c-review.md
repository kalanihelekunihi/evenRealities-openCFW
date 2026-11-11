# R1 health-enable event and settings toggle in C

The health-enable handler at 0x496fc and its settings helper at 0x8f6f8 now use C. The registered service name aliases the handler. The existing event adapter keeps its native low-byte truncation before forwarding, while direct handler calls normalize the full incoming word to zero/nonzero. The callback declaration now matches the service's return type without changing its object.

The handler logs the original value, updates the engine setting, then toggles authorization slots zero and three in order. It returns the last authorization result. The eight-byte helper starts with zeros, reads the current record, treats byte 5 equal to zero as enabled, and applies only when the requested value differs. It changes only byte 5 to the truncated requested-value XOR one; the remaining record bytes and partial provider writes are preserved.

Stock/C replay passes 1,344 direct, actual-adapter and mixed-sequence cases. It covers full-word versus adapter-byte normalization, arbitrary disable bytes, partial readback, ignored provider status, dynamic logging, return propagation and record mutation between calls. Eight compiled defects are rejected. Checks compare provider order and full record contents, public return values, preserved registers, SP and masks. No new state owner or assembly was added.

All 750 R1 units compile without failures or duplicate strong symbols. All 749 prior objects retain their hashes. Relocatable composition has 138 application and 34 bootloader imports: the event-service import closes while two record read/apply providers become explicit. The R1 manifest check passes. The global check currently flags the concurrent G2 resident_rom_thumb_set.S manifest gap; that work remains untouched.

Record read/apply, authorization and logging are modeled boundaries. The tests do not prove algorithm record internals, asynchronous execution, physical sensor activation, complete firmware linkage or device behavior. Timing/raw-register assembly bridges reviewed during this pass remain because their native contracts require them. See [machine-readable evidence](health-enable-c-review.json) and [REA helper receipt](health-enable-c-rea.json).

The subsequent [native record review](gomore-record8-c-review.md) now closes both record providers and replays health enable with the actual C validation, selection and commit bodies.
