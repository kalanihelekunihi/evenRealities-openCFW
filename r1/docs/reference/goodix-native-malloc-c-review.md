# Native Goodix public allocation and exhaustion policy in C

`native_heap_malloc.c` implements the public zeroing allocator, its non-returning exhaustion path, the shared sensor-memory fatal routine and the manager-flags bridge. Existing pool, sensor-watchdog and manager-lifecycle owners are reused. No persistent state is added.

Allocation preserves the unsigned request bits, minimum eight-byte payload, four-byte rounding and eight-byte header. It tries the native bins before wilderness allocation, updates native metadata, and clears exactly the clamped payload length. It retains stock arithmetic rather than adding a negative-size guard.

Failure queries free space, publishes status `(0,1,0,0)`, logs the original info/free values, reloads and feeds the sensor-task watchdog, signals manager event `0x200`, then repeats `osDelay(1000)`. The manager bridge reads the existing lifecycle thread slot; null returns zero, otherwise it forwards thread/flags and the full RTOS result. Logging callbacks can change the watchdog, and watchdog callbacks can change the manager slot before its read. The path is not replaced by a trap or a null return.

Checks pass for 5,032 public allocation comparisons, including 1,204 exhaustion cases, plus 408 terminal-policy and 160 bridge comparisons. A further 1,000 mixed initialization/allocation/release operations execute only reconstructed C on the source side, with no stock allocator fallback. Metadata and payload-clear write width/order/value and complete pool images match. Ten compiled defects are rejected.

The entries account for 212 stock instruction bytes; 208 execute. Four bytes following non-returning fatal calls are excluded as unreachable while that policy remains non-returning. Failure observation stops after three repeated delay calls. External status publication, typed logging, watchdog feed, RTOS flags and delay are modeled. This checks the call sequence and live state, not a physical manager reset or watchdog/scheduler timing.

Returning paths check saved integer/FP registers, SP, masks, FPSCR and guards. Terminal paths check guards, FP/masks and stable delay-loop stack depth; private frame depth, active private register assignments, caller scratch and APSR are excluded. Selected bounded and high signed-bit requests are tested. Near-wrap huge clears outside mapped RAM, concurrency, reallocation/deinitialization, final linking, startup and boot remain unverified.

The normal serial build compiles all 867 units with no duplicate strong symbols and unchanged imports (62 application, 22 bootloader). The tested object equals its normal-build object. All 856 prior nongenerated objects remain identical; two differing generated objects are recorded separately. The manifest adds one unit. Source plan and cache layout remain unchanged.

The [machine-readable receipt](goodix-native-malloc-c-review.json) records hashes and checks. Probes are under `build/goal-r1-goodix-native-malloc-c/`; the final normal report is `build/sources-goal-r1-goodix-native-malloc-flags-c/report.json`.
