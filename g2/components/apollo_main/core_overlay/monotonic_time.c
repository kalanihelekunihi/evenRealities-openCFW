/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Wrap-extending monotonic-seconds helper matched to stock entry 0x0047DC74.
 */

typedef __UINTPTR_TYPE__ open_cfw_monotonic_uintptr;

typedef unsigned int (*open_cfw_monotonic_tick_function)(void);

struct open_cfw_aeabi_divmod_result;

void open_cfw_aeabi_uldivmod_core(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
);
unsigned int open_cfw_lv_irq_disable(void);

#ifndef OPEN_CFW_MONOTONIC_TICK_GET
#define OPEN_CFW_MONOTONIC_TICK_GET() \
    (((open_cfw_monotonic_tick_function) \
        (open_cfw_monotonic_uintptr)0x00454EFFU)())
#endif
#ifndef OPEN_CFW_MONOTONIC_LAST_TICK
#define OPEN_CFW_MONOTONIC_LAST_TICK \
    (*(volatile unsigned int *)(void *)0x20074AC8U)
#endif
#ifndef OPEN_CFW_MONOTONIC_WRAP_COUNT
#define OPEN_CFW_MONOTONIC_WRAP_COUNT \
    (*(volatile unsigned int *)(void *)0x20074AC4U)
#endif
#ifndef OPEN_CFW_MONOTONIC_IRQ_DISABLE
#define OPEN_CFW_MONOTONIC_IRQ_DISABLE() open_cfw_lv_irq_disable()
#endif
#ifndef OPEN_CFW_MONOTONIC_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_monotonic_irq_restore_target(unsigned int primask)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(primask)
        : "memory"
    );
}

#define OPEN_CFW_MONOTONIC_IRQ_RESTORE(primask) \
    open_cfw_monotonic_irq_restore_target(primask)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_monotonic_seconds(void)
{
    unsigned int result[4];
    unsigned int primask;
    unsigned int tick;
    unsigned int wraps;

    primask = OPEN_CFW_MONOTONIC_IRQ_DISABLE();
    tick = OPEN_CFW_MONOTONIC_TICK_GET();
    if (tick < OPEN_CFW_MONOTONIC_LAST_TICK) {
        OPEN_CFW_MONOTONIC_WRAP_COUNT += 1U;
    }
    OPEN_CFW_MONOTONIC_LAST_TICK = tick;
    wraps = OPEN_CFW_MONOTONIC_WRAP_COUNT;
    OPEN_CFW_MONOTONIC_IRQ_RESTORE(primask);

    open_cfw_aeabi_uldivmod_core(
        tick,
        wraps,
        1000U,
        0U,
        (struct open_cfw_aeabi_divmod_result *)(void *)result
    );
    return result[0];
}

#undef OPEN_CFW_MONOTONIC_IRQ_RESTORE
#undef OPEN_CFW_MONOTONIC_IRQ_DISABLE
#undef OPEN_CFW_MONOTONIC_WRAP_COUNT
#undef OPEN_CFW_MONOTONIC_LAST_TICK
#undef OPEN_CFW_MONOTONIC_TICK_GET
