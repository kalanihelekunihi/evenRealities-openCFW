# SpO2 and temperature state publishers in C

The publishers at `0x8a87e` and `0x8a896` now use ordinary C. Each initializes a full status word, checks its low byte against 2, and publishes one byte with the appropriate event id (`0x1003` or `0x1007`). The full backing word remains available during the synchronous call, including callback mutations. Both public entries return void.

REA matches all 48 stock instruction bytes; every byte executes across 4,608 comparisons covering every low byte, high status words, provider returns and byte/word/tail mutations. Seven compiled defects are rejected. Another 1,728 comparisons execute the actual service wrappers, publishers, event publisher, enqueue and memory movement with prepared contexts and modeled queue/flags APIs. Defined record fields, failed-send wakeup and live thread reloads match.

Two external direct transfers were identified, both service-wrapper tail calls. Caller-scratch R3 restoration and private frame locations are outside the C interface. Indirect and nonstandard ABI consumers are not exhaustively proven. The nested event publisher still has its own frame bridge; its uninitialized leading queue word is excluded from these comparisons.

The serial normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. The final object equals the probe. The other 851 prior nongenerated objects, manifest, cache layout, source plan and persistent state remain unchanged; R1 source checking passes. This state-publish unit contains no inline assembly.

Saved integer/FP state, SP, masks, FPSCR and caller guards are checked. Void return, other caller scratch and APSR are excluded. Physical scheduling/queue delivery, concurrency, complete application linking, startup/scatter integration, physical sensors and boot remain unverified.

See the [receipt](health-state-publish-pure-c-review.json) for hashes. Probes and the direct-transfer scan are under `build/goal-r1-health-state-publish-c/`.
