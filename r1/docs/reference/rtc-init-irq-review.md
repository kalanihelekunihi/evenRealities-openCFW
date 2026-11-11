# R1 RTC initialization through tick dispatch

The existing compiled Nordic RTC driver matches the locked application in
432 controlled initialization-to-interrupt sequences. Each sequence executes
the actual SDK `nrfx_rtc_init`, tick enable, RTC enable and RTC2 IRQ handler,
and compares them with stock at `0x7AD6C`, `0x7AE4C`, `0x7AD20` and `0x31750`.
No firmware source or build selection changes were needed.

The matrix combines four initial state bytes (0, 1, 2, 255), three prescalers
(0, 1, 4095), three priorities (0, 6, 7), both reliable flags, three latency
bytes (0, 65, 255), and two callback targets. Ordered RTC/NVIC register
accesses, driver metadata at register writes, return status, callback identity
and event argument, and final modeled registers/metadata all match.

Both implementations install the handler before checking the state. A
nonzero state returns error 8 without programming the prescaler or NVIC, but
the replacement handler receives the later enabled tick. Fresh initialization
programs IRQ 36 priority/enable, prescaler, reliable/latency bytes and state;
tick enable clears its event with readback before enabling event/interrupt
bits. RTC enable starts the counter and advances state to 2. REA independently
exposes the handler-before-state ordering in the stock initializer.

This extends the [dispatcher review](rtc-irq-review.md), whose handler slots
were seeded directly. Here initialization installs the tested handler. The
register model still does not execute physical NVIC exception delivery or
validate full startup vector placement. Stock logging is held quiescent by
returning zero from its mode getter. Private stack, complete fault behavior,
timing and byte identity remain unproven. Only the RTC2/index-zero instance
is covered. No source qualification or workflow gate credit is claimed.

[rtc-init-irq-review.json](rtc-init-irq-review.json) binds the stock hash,
unchanged SDK object, existing successful build report, matrix, REA result
and ignored probe artifacts under `build/goal-r1-rtc-init/`.
