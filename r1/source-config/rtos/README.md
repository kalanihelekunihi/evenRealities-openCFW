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
