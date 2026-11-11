#include <stdint.h>

extern uint32_t r1_stream_tick_now(void);
extern uint32_t r1_stream_wake(void);

uint32_t r1_stream_timer_rearm_native(uint32_t timer)
{
    if (!timer) {
        __builtin_arm_wsr("basepri",64);
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
        for (;;) {}
    }
    uint32_t now=r1_stream_tick_now();
    *(volatile uint32_t *)(uintptr_t)(timer+4u)=now;
    return r1_stream_wake();
}
