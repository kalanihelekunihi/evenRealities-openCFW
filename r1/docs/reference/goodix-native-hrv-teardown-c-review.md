# Native HRV context teardown in C

The [HRV initializer review](goodix-hrv-initialize-c-review.md) now shares this canonical owner and exercises the entire C constructor/allocator/teardown lifecycle. No owner or destructor source changes were required.

`native_hrv_teardown.c` implements the HRV context destructor, its public thunk alias, the frame-status adapter and the release-cell helper. One canonical four-byte HRV context owner is added for future initialization to share. The portable context model remains unchanged; its native symbol hints are superseded.

The destructor releases eleven nullable pointer cells in stock order, clearing each nonzero cell only after release. It reloads the context owner before every field, releases two further buffers without clearing their cells, then reloads and releases the context itself before clearing its owner. A late null owner returns `0x10000005`; the frame adapter maps nonzero status to `-1`. The initial context must be valid: an early null-return guard would change the observed accesses.

All 168 stock instruction bytes execute in 49,152 field-mask comparisons, 120 live-owner/result mutation comparisons and 18 helper checks. Callback snapshots check clear-after-release timing. Four initial-null cases compare unmapped access addresses in the emulator; they do not establish physical MCU fault behavior.

Another 1,440 comparisons use actual C initialization/allocation/release providers. Typed contexts are prepared with roots before or after children, optional unrelated live guard allocations and different nullable fields. Heap images, context owner, call order and write width/order/value match. No stock code executes on the source side. Ten compiled defects are rejected.

The contexts are fixture preparation, not recovered HRV initialization or computation. Direct tests model the release boundary; heap integration executes it. Saved integer/FP registers, SP, masks, FPSCR and guards are checked. Caller scratch, private frames, APSR, concurrency, physical memory, complete algorithm lifecycle, final linking/startup and boot remain unverified.

The normal serial build compiles 869 units with no duplicate strong symbols and unchanged imports (62 application, 22 bootloader). The tested object equals its normal-build object. All 858 prior nongenerated objects remain identical; two differing generated objects are recorded separately. The manifest adds one unit. Source plan and cache layout remain unchanged.

The SDK allocator-deinit declaration alone did not identify a supported stock implementation. No speculative pool reset is added. Observed direct pool-cell references cover initialization and control lookup, with indirect-reference limitations retained.

The [machine-readable receipt](goodix-native-hrv-teardown-c-review.json) contains hashes and checks. Probes are under `build/goal-r1-goodix-native-hrv-teardown-c/`; the normal report is `build/sources-goal-r1-goodix-native-hrv-teardown-c/report.json`.
