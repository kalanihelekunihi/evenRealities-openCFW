# R1 RTOS candidate configuration

`FreeRTOSConfig.h` is derived from the preserved historical seed at
`r1/config-recovered/FreeRTOSConfig.h`. It removes the obsolete manual
`xTaskDelayUntil` declaration and its incorrect 10.0.0-kernel rationale.
The pinned 10.5.1 kernel owns the real declaration. The archived seed is
unchanged.

Evidence-supported values include 1024 Hz ticks, 56 priorities, 256-word
idle/timer stacks, both static and dynamic allocation, stack-overflow mode 2,
and the Nordic RTC port. See the configuration seed's confidence tables and
`r1/docs/correlation/FREERTOS-KERNEL-VERSION-CORRELATION.md`.

Other values remain candidates, including heap size, task-name width,
queue registry, trace options and timer priority/queue length. Passing a
compile check does not admit those values as recovered stock configuration.

The first compile audit disproved the assumption that these candidate settings
produce a 112-byte `StaticTask_t`: they produce 92 bytes. The stock callback
instructions establish a 112-byte control reservation before each 256-word
stack, and the two allocations are 0x470 bytes apart. They do not establish
which fields or padding occupy the reservation. R1's source-owned callbacks
therefore retain a transparent 112-byte reservation containing the candidate
upstream type, with an assertion that the type fits. They neither change
kernel options to force a size nor claim the stock type is 92 bytes.

Exact stock TCB configuration, fields and dynamic allocation extent remain
unresolved. A compiler-generated layout probe records the candidate type size
in the build report on every run.

## Native port critical assertion contract

`native_port_assert.h` is forced into only the separately compiled authenticated
Nordic `port_cmsis.c` translation unit. It preserves stock's BASEPRI=64,
zero-write at 0xFFFFFFFF and terminal loop for failed assertions. This does not
change other kernel/SDK assertion policies or tune TCB options. The linker
selects the two critical functions and their shared nesting state; scheduler
startup and the rest of the port remain separate integration work.

All 1,040 critical comparisons pass, including 104 exact unmapped assertion
writes, nested/overflow counts, active-exception checks and BASEPRI transitions.
The structured logger also passes 6,656 comparisons with these actual critical
functions executing. Physical exception registers and instruction identity
remain unproven. The frontier records the native variant's report and object
explicitly; the older assertion-disabled port object is not promoted by these
receipts.

The newer stock-supported scheduler and task-wait providers use scoped native
interfaces rather than this baseline's complete `StaticTask_t` layout. The
wait/mutex interface authenticates a104-byte accessed prefix:32-byte task name,
stack-depth word at+84, base priority+96 and held-mutex count+100. The extra
word stores a depth, so `configRECORD_STACK_HIGH_ADDRESS` is not inferred.
Tail bytes104..111 and complete112-byte task construction remain gated. See
`task_wait_contract.h` and `research/source-build/rtos-task-wait/` receipts.
The pinned debugger-priority declaration now supplies the native RAM word55;
this does not admit the full scheduler-start routine or change the baseline
kernel configuration globally.

Native task construction now has its own112-byte source record and verified
factory/initializer contracts in `components/board/native_task_construction.h`
and `research/source-build/native-task-construction/`. This advances the earlier
constructor-size gate through an explicit R1 representation, including32-byte
names and stack-depth words+84. It does not alter this baseline's `StaticTask_t`
or infer the upstream end-of-stack option. The4-byte notification value, state
byte108 and allocation mode109 are initialized/checked; word92 remains opaque
and other task-runtime semantics, CMSIS wrapping and scheduler execution are
independent gates.

`thread_contract.h` now applies the112-byte R1 type only while compiling the
selected unchanged CMSIS thread-creation body. Typed native constructor names
and the common task tag avoid incompatible-pointer adapters. Baseline
`StaticTask_t` and weak idle/timer memory callbacks remain separate candidates;
this scoped representation does not validate their layouts or startup behavior.
The actual five application creation callbacks now compose through this provider,
while task execution/cleanup and scheduler startup remain independently gated.

`task_termination_contract.h` exposes the authenticated112-byte task record to
unchanged kernel termination/state/reclamation bodies, using a one-entry
notification array at108 and allocation mode at109. This is the same layout
as native construction, with upstream array spelling. Pending deletions own
0x20007820; existing scheduler globals keep their current owners. No baseline
`StaticTask_t`, task-name size or static allocation callback is changed.

The termination contract also supplies existing ready-list, top-ready-priority
and tick state to unchanged idle reclamation/expected-idle-time bodies.
`xTickCount` continues to use the existing provider-owned word at 0x20007828.
No duplicate kernel state is introduced. Native cleanup is an explicitly
bounded inlined region; source function calling convention does not establish
a standalone native function boundary.

`idle_contract.h` scopes the native `configUSE_IDLE_HOOK=1` setting to the
unchanged selected idle task. The native call at0x85034 proves that hook is
active; the baseline disabled-hook candidate is untouched. The selected body
uses preemption1, idle-yield1, tickless1 and threshold2, all checked at compile
time and against native control flow. Cleanup/expected-time bindings use their
actual C providers. The hook uses a typed void adapter to the existing uint32
watchdog feed thunk. Tick suppression retains its external provider gate.

`sleep_kernel_contract.h` binds existing scheduler/list state to unchanged
sleep-status and tick-step bodies; it introduces no new kernel storage.
`tickless_port_contract.h` scopes RTC1/simple-debug configuration, native
returning error logging and FPU preparation to the selected Nordic RTC sleep
body. FPU preparation runs only for nonzero expected idle time, as native
control flow requires. Native clock setup, physical counter/wake behavior and
context switching retain separate gates.

`startup_task_contract.h` binds selected kernel startup and the unchanged
source-owned static-memory callbacks to the native112-byte TCB. It introduces
the idle handle once in the scheduler translation unit; callback compilation
shares only its extern declaration. `startup_timer_contract.h` scopes timer
priority53 and registry0, uses original pinned timer message typedefs, and
owns native timer handles/lists/pointers. Static queue/storage and two1136-byte
TCB/stack reservations are placed at authenticated addresses by the verifier.
The baseline `StaticTask_t` remains92 bytes. Port startup and timer runtime are
still separate source providers; creation receipts do not establish execution.

`port_start_contract.h` binds private startup state to the existing words at
0x20007810/14/18. It requires raw priority2, kernel priority15, CPUID0x410fc241,
RTC prescaler31 and IRQ17; it does not change the baseline configuration.
The SDK body probes writable priority bits directly, and an0xe0 readback yields
ucMaxSysCallPriority0. This is preserved independently of BASEPRI64 masking.
First-task transfer remains a provider boundary; the integrated graph stops
before that body and does not establish physical scheduler execution.

`context_contract.h` exposes the full native TCB to the unchanged selected task
switcher and upstream stack macros, reusing existing current-task, ready-list,
yield and suspend storage. The SDK GCC C port compiles unchanged with the
baseline raw priorities2/15 and three priority bits, yielding PendSV mask64 and
first-task mask480 (BASEPRI lowbytee0). `native_context_vectors.c` owns only
initial-SP, SVC and PendSV records; the SDK's uint32 `__isr_vector` declaration
is preserved and placed in flash. It does not define missing vector slots.
Kernel stack-overflow callback implementation and actual exception return stay
separate providers/evidence gates.


The scoped `message_queue_contract.h` admits native80-byte `StaticQueue_t`,
24-byte `osMessageQueueAttr_t` and registry0 for unchanged CMSIS queue wrappers.
Capacity uses the authenticated dummy-array offset56 plus one word (native60).
The baseline registry configuration is unchanged. The shared
`timer_isr_queue_contract.h` also supplies the authenticated priority-validator
call to the selected queue ISR receive provider; it does not add a second
validator or duplicate port/kernel state.


`synchronization_contract.h` admits80-byte static semaphore storage and
16-byte CMSIS mutex attributes, using the existing scoped registry0 wrapper
configuration. `mutex_kernel_contract.h` shares the canonical public queue
providers while selecting unchanged private mutex/wait helpers and native
80-byte queue fields. `mutex_tasks_contract.h` exposes the authenticated
104-byte accessed TCB prefix (held count at100, base priority at96); full
112-byte construction and notification/allocation tail retain their separate
provider contracts. No new kernel state owner or baseline configuration
change is introduced.


`notification_wrapper_contract.h` scopes thread/event flags to one native
notification slot; the31/24-bit flag bounds are selected unchanged from the
pinned CMSIS source. `notification_task_contract.h` reuses the established
112-byte TCB with upstream one-element arrays at104/108, existing shared
kernel words/lists and explicit native priority-validation macro. No second
notification state, scheduler counter or termination-state owner is emitted.
These interfaces are staged behind isolated/composed graph admission gates.


`event_group_contract.h` checks the32-byte event-group/32-bit bitset variant;
selected event bodies retain pinned control-bit logic. `timer_pend_contract.h`
shares the existing timer queue and original16-byte callback command layout.
`unordered_event_contract.h` shares the native104-byte accessed task prefix
and binds scheduler suspension to0x20007850, avoiding linkage to a private
canonical symbol or a duplicate state word. These source stages remain behind
the composed notification/event/deferred-callback admission gate.
