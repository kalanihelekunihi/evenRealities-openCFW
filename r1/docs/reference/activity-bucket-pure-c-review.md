# Activity ten-minute bucket helper in C

The helper at `0x5ac74` now uses the canonical eight-byte C calendar type. It initializes all bytes, fetches the UTC offset, calls the existing converter without changing timestamp bits, ignores its status, reads minute before hour, and returns the byte-truncated value of `hour*6 + minute/10`. Partial outputs and out-of-range byte behavior remain native.

REA matches all 50 stock instruction bytes; every byte executes across 68,161 comparisons. These cover all 65,536 hour/minute byte combinations plus 2,625 timestamp, offset, partial-write and status controls, checked with an independent bucket oracle. Six compiled defects are rejected.

Another 936 comparisons execute the real C RTC getter and calendar adapter/forward converter. A further 2,594 execute the existing activity-storage caller with those providers, matching packed cache updates and diagnostics across timestamp wrap, offset extremes and duration crossings. Only logging is modeled. The parent's assembly bytes, relocations and diagnostic strings are unchanged; its section is aligned to four bytes in the probe. Its final-image alignment and C conversion remain separate work.

The serial normal build compiles 862 units with 63 application and 22 bootloader imports, no failures or duplicate strong symbols. The final object equals the probe. The other 851 prior nongenerated objects, manifest, cache layout, source plan and persistent state remain unchanged; R1 source checking passes.

The two identified direct calls consume R0 and reload their own arguments. Restored caller-scratch R2/R3, private frame location and APSR are excluded; indirect or nonstandard ABI consumers are not exhaustively proven. Saved integer/FP state, SP, masks, FPSCR and guards are checked. Full application linking, startup/scatter integration, concurrency, physical clock/sensors and boot remain unverified.

See the [receipt](activity-bucket-pure-c-review.json) for hashes. Probes and the direct-call scan are under `build/goal-r1-activity-bucket-pure-c/`.
