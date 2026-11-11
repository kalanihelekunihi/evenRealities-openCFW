# R1 periodic activity accumulator in C

Stock entry 0x48e68 now has a C implementation. It owns the recovered 24-byte state at 0x20006ebc, ending immediately before the separately owned activity-mode byte. Actual stock decompression confirms all 24 initializer bytes are zero.

Every non-null input updates the latest counter snapshot. Exact local-day equality rebases the baseline. Activity mode one or health mode zero also rebase and clear the pause flag. A non-two health mode starts a pause and rebases only after unsigned elapsed time exceeds 900 seconds.

In health mode two, the accumulator clears the pause flag and uses unsigned ten-minute buckets. Before offset 595 it clears the sent flag; from 595 onward it emits at most once per bucket. Counter rollback rebases and logs instead of publishing. Normal output publishes topic 11 with three truncated 16-bit deltas, bucket offset and timestamp in a 12-byte event. Baseline counters are reloaded after publishing so synchronous provider mutation is preserved.

The stock/C replay passes 822 direct and repeated-call cases: null samples, mode combinations, threshold equality, wrapped time, day resets, rollback, equal/increasing counters, aliased state samples, logging changes and provider mutation. A further 1,264 comparisons execute the actual C sensor output dispatcher and accumulator together. Comparisons cover call order, event contents, call-time state snapshots, full guarded state/input buffers, preserved registers, SP and masks. Nine compiled defects are rejected.

All 746 R1 units compile with zero failures or duplicate strong symbols. All 745 prior objects retain their hashes. Relocatable composition has 139 application and 34 bootloader imports; only the activity accumulator import is removed. Repository-wide source checks pass.

Clock, mode, logging and event providers are modeled in the new probes. Tests use synchronous mapped SRAM and aligned samples; private event addresses are normalized by contents. These checks do not establish asynchronous behavior, physical accelerometer input, event persistence or full firmware linkage. See [machine-readable evidence](activity-accumulator-c-review.json), [REA packet construction](activity-accumulator-c-rea.json) and [stock state initialization](activity-accumulator-initialization.json).

The subsequent [explicit refresh review](activity-explicit-c-review.md) now supplies the registered activity event using this same state owner and replays both C handlers in mixed sequences.
