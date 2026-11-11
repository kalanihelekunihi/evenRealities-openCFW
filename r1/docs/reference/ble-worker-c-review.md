# R1 BLE worker in C

The BLE worker at `0x91f54` and timer callbacks at `0x4e008` and `0x4d2e8` now have ordinary C implementations in `r1/src/application/runtime/native_ble_io_worker.c`. The current objective accepts open-toolchain builds without byte identity or a paid compiler.

The worker publishes its 8-by-4 queue before checking allocation, initializes the peer/BLE layers, participates in startup group 4, schedules both callbacks, and services live watchdog state. Dispatch preserves stop/fast/restart advertising precedence, independent transmit-power requests, SDK polling before and after valid events, DFU logging gates, and the existing C suspend and allocation-fault paths. Callbacks reuse the existing connection-handle and service-thread owners. The watchdog word is zero in authenticated cold RW at `0x20006564`; this does not establish final linker placement.

All 4,102 stock/C comparisons pass: all 512 relevant flag combinations across three logging sequences with and without live state mutation, invalid wait results, all 512 three-read log-mode sequences for role synchronization, both callbacks, and allocation failure. Existing C park/fault helpers execute; external RTOS, SDK and lower hardware policies are modeled. Eight compiled defects are rejected. REA byte receipts match the pinned stock image. This is behavioral evidence, not a decompiler equivalence claim.

The normal build compiles 743 application and 82 bootloader units with no duplicate strong symbols. Of 824 prior objects, 822 are identical; only two generated bootloader objects change. The worker import closes and seven lower policy dependencies become explicit, bringing application imports to 77. They remain unresolved rather than receiving success stubs: peer commit, BLE configuration, connection-event handling, advertising stop/restart, peripheral watchdog planning and transmit-power planning.

R1 manifest validation passes (825 units, 611 sources). A final application link, radio behavior, physical timing and device boot remain unverified. Probe sources and results are under `build/goal-r1-ble-worker-c/`; hashes and import details are in [the review receipt](ble-worker-c-review.json).
