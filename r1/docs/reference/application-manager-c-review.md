# C application manager startup and watchdog loop

The launch lifecycle now has a C provider for `r1_application_manager_thread`, stock `0x45d7c`. This fills the coordinator between the existing launch thread, SoftDevice/clock setup, worker startup and watchdog loop. The five still-unimplemented lower services remain explicit imports. No executable stock target or substitute no-op supplies them.

REA bytes authenticate the entire 208-byte window, including the 154-byte instruction body and its message/context/name literals. The active Ghidra procedure inventory lacks this entry; direct Thumb control-flow review and the previously authenticated startup-thread callback identify it. The review derives this pseudocode:

1. Emit the typed start message; feed the hardware watchdog; initialize SoftDevice resources and the default clock, EAT, storage, EP and tasks in that order.
2. Feed the watchdog; create the CMSIS sync event object with NULL attributes and publish its handle. A null result follows the existing BASEPRI-64/invalid-store allocation-fault path.
3. Feed the watchdog; execute the worker suspension barrier; feed again. Register `manager` with interval 10,000, keep its returned token, publish ready=1 and start logging.
4. Repeatedly wait for thread flags with mask `0x00ffffff`, options zero and timeout 500. Dispatch only unsigned results 1 through `0x7fffffff`. On every completed wait, poll the console, feed the saved watchdog token and check watchdog records.

The clock call supplies NULL configuration and a defined NULL incidental context. The concrete snapshot supplies the registered backend context, while the concrete default init/update ignore that context. Incoming scratch-register words are outside the coordinator contract. Existing event-flag and lifecycle owners are reused. One new initialized byte owns stock ready field `0x2000653c`; native RW/ZI startup executes on poison with guards and an independent RW decoder confirms its cold zero value. Final RAM placement is not established.

**720 stock/C comparisons** pass across allocation failure/success, zero and nonzero watchdog tokens, unsigned event-result boundaries, multiple loop cycles, live event-handle/ready mutations and both interrupt-mask states. They verify ordered calls, explicit arguments, state publication and the real shared fault primitive's attempted zero store to `0xffffffff`. **384 additional comparisons** execute the actual C suspension barrier and worker acknowledgment handshakes across normal/factory configuration, successful/missing acknowledgments and live event-handle changes. RTOS, logging, configuration and other helper services are modeled with real Thumb return stubs.

All **152 reachable native instruction bytes** execute. The remaining two-byte self-branch follows the failing allocation-fault store; the fixture observes the fault access. The nonreturning loop is observed at the next wait boundary after bounded iterations. Caller stack guards, saved FP registers and interrupt masks are checked. Private frames, incidental integer registers, APSR and physical fault-handler behavior are excluded.

Six compiled defects are rejected: wrong wait mask, missing ready publication, accepting error event values, wrong watchdog token, wrong registration interval and missing hardware feed. The normal build compiles **856 units**, with no duplicate strong symbols and both relocatable compositions passing. All **845 prior nongenerated objects** remain identical, including the launch object after its shared-header declaration change. The manifest adds exactly one unit using the existing launch profile/CMSIS include; source-plan selections are unchanged. R1 source validation passes.

The former worker import closes; these five concrete dependencies become visible:

| Stock entry | Explicit import |
| --- | --- |
| `0x915a8` | `r1_structured_log_typed` |
| `0x4ef8c` | `r1_eat_core_init` |
| `0x731a0` | `r1_storage_manager_initialize_731a0` |
| `0x91504` | `r1_manager_logging_start_91504` |
| `0x46004` | `r1_manager_event_dispatch_46004` |

Application imports therefore change from 61 to **65**; bootloader linker imports remain **22**. The lower implementations, physical scheduling/RTOS waits, hardware watchdog behavior, full application linking and boot remain unfinished. Compilation and bounded execution do not prove a bootable firmware image.

[Machine receipt](application-manager-c-review.json) binds sources, normal reports, REA bytes, initialization evidence and ignored fixtures under `build/goal-r1-application-manager-c/`.
