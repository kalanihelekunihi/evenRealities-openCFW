# Watchdog checker uses a C timestamp and void operation ABI

`native_watchdog_manager.c` no longer has fixed-register declarations or empty inline assembly. The checker initializes its timestamp word to zero and obtains the complete value through the registered sample operation. The architectural BASEPRI write remains a compiler intrinsic; its interrupt-masking effect is required by the stock fault path.

REA confirms that stock sample provider `0x6623e`, operation 1, calls the tick source and stores a complete 32-bit result. The matching C provider does the same. Thus incoming R3 is not an input to normal watchdog operation. This retires the scratch-register/partial-write contract from the [historical checker review](watchdog-check-c-review.md). Replacement sample providers that leave timestamp bytes unwritten are outside this proof; their fallback scratch now starts at zero. The void C operation provides no R3 return.

The [receipt](watchdog-pure-c-review.json) records 1,728 paired stock/C cases with the actual sample provider and modeled list helpers, plus 1,728 with actual stock/C list head/next helpers. Cases cover enabled/disabled state, zero-to-three nodes, flags, unsigned wrapping timestamps, intervals and incoming scratch seeds. Both returning and expiry paths occur. Checks compare provider order, record bytes, callee-saved registers, masks, expiry flag writes, BASEPRI 64 at fault publication and the attempted zero write to `0xffffffff`. Three defective variants with signed timeout comparison, wrong skip flag or wrong BASEPRI are rejected.

Tick source and lock calls remain modeled. Direct replay additionally models list helpers. Fault replay stops at the invalid-write attempt; it does not prove exception handling, physical reset or hardware recovery. No byte identity or full firmware completion is claimed.

The normal source report is `build/sources-goal-r1-watchdog-pure-c/report.json`: 727 units compile with no failures or duplicate strong symbols. Imports remain 178 application and 34 bootloader. Only the watchdog manager object changed; 726 objects are unchanged from the preceding RTC-open checkpoint. Both manifests pass `make sources-check`.
