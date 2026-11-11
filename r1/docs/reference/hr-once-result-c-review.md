# R1 one-shot HR result callback in C

The plausible-value helper at 0x499e0 and result callback at 0x499f0 now use C, closing the controller's result callback import. The existing HR handle array is reused; no state owner or assembly was added. The controller now shares the result declaration through a header without changing its object.

Plausibility accepts HR bytes 40 through 220. The callback logs all three sample bytes, then publishes an eight-byte topic-6 record only when the current HR is plausible and health mode is two. The record contains the HR byte with three zero padding bytes followed by the current timestamp. HR is captured before the timestamp provider runs. The callback unregisters the incoming HR handle and clears the shared once handle after either publication or rejection, regardless of event result. Length is ignored, matching stock.

Stock/C replay passes 2,790 cases: all possible HR bytes, health-mode/log combinations, direct helper calls, partial-path sample/handle mutations, zero and large handles/lengths, event failure and actual C controller/result sequences. Eight compiled defects are rejected. Checks cover callback identity, event bytes, provider arguments/order, call-time sample/state snapshots, guarded shared state/input buffers, preserved registers, SP and masks.

All 753 R1 units compile without failures or duplicate strong symbols. All 752 prior objects retain their hashes. The result callback import closes without new imports, leaving 135 application and 34 bootloader imports. The R1 manifest check passes. The global check currently flags the concurrent G2 resident_rom_thumb_set.S manifest gap; that work remains unchanged.

Stream registry, health mode, clock, logging and event delivery are modeled. The HRV producer is checked by identity, not executed. Tests require mapped non-null samples, including when length is zero. Private event addresses are normalized by contents; caller-clobbered registers and private stack are excluded. Physical sensors, asynchronous IRQ/scheduling, complete firmware linkage and hardware activation remain unproved.

See [machine-readable evidence](hr-once-result-c-review.json) and [REA publication/cleanup receipt](hr-once-result-c-rea.json).
