/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 interrupt-state primitives and
 * display-task attribute accessor at 0x00473934...0x00473951.
 */

#ifndef OPEN_CFW_LV_RUNTIME_PRIMASK_READ
static __attribute__((always_inline)) inline unsigned int
open_cfw_lv_runtime_primask_read_target(void)
{
    unsigned int value;

    __asm__ volatile(
        "mrs %0, primask"
        : "=r"(value)
        :
        : "memory"
    );
    return value;
}

#define OPEN_CFW_LV_RUNTIME_PRIMASK_READ() \
    open_cfw_lv_runtime_primask_read_target()
#endif

#ifndef OPEN_CFW_LV_RUNTIME_IRQ_ENABLE
#define OPEN_CFW_LV_RUNTIME_IRQ_ENABLE() \
    __asm__ volatile("cpsie i" : : : "memory")
#endif

#ifndef OPEN_CFW_LV_RUNTIME_IRQ_DISABLE
#define OPEN_CFW_LV_RUNTIME_IRQ_DISABLE() \
    __asm__ volatile("cpsid i" : : : "memory")
#endif

#ifndef OPEN_CFW_LV_RUNTIME_DISPLAY_TASK_ATTRIBUTES
#define OPEN_CFW_LV_RUNTIME_DISPLAY_TASK_ATTRIBUTES \
    ((const void *)0x00776A3CU)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_lv_irq_enable(void)
{
    unsigned int previous = OPEN_CFW_LV_RUNTIME_PRIMASK_READ();

    OPEN_CFW_LV_RUNTIME_IRQ_ENABLE();
    return previous;
}

__attribute__((used, noinline))
unsigned int open_cfw_lv_irq_disable(void)
{
    unsigned int previous = OPEN_CFW_LV_RUNTIME_PRIMASK_READ();

    OPEN_CFW_LV_RUNTIME_IRQ_DISABLE();
    return previous;
}

__attribute__((used, noinline))
const void *open_cfw_lv_display_task_attributes(void)
{
    return OPEN_CFW_LV_RUNTIME_DISPLAY_TASK_ATTRIBUTES;
}

#undef OPEN_CFW_LV_RUNTIME_DISPLAY_TASK_ATTRIBUTES
#undef OPEN_CFW_LV_RUNTIME_IRQ_DISABLE
#undef OPEN_CFW_LV_RUNTIME_IRQ_ENABLE
#undef OPEN_CFW_LV_RUNTIME_PRIMASK_READ
