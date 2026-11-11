# App-timer counter backend

The normal R1 composition now supplies `app_timer_cnt_get` and
`app_timer_cnt_diff_compute` through the read-only RTC1 adapter in
`r1/src/application/rtos/app_timer_counter.c`. The [counter closure review](app-timer-counter-c-review.md)
records the build, SDK-oracle comparison, RTC setup/unit checks and actual
peer-manager integration tests.

The pinned FreeRTOS lifecycle provider does not define these APIs. The pinned
app_timer header specifies RTC1, and the classic SDK implementation supplies a
24-bit wrapped difference. The selected R1 RTC1 prescaler and the consumer's
FREERTOS APP_TIMER_TICKS conversion both use 1024-Hz units. The adapter reads
that existing peripheral; it does not alias CMSIS/kernel ticks or start another
RTC owner. Compile-time guards reject the tested incompatible configurations.

The former unresolved-dependency investigation did not establish a stock counter
entry address. That identity remains unclaimed: this closure is an SDK-contract
port for the open source build. Physical timing/radio delivery and complete
application integration still need validation.
