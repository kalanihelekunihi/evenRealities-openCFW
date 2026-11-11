/* SPDX-License-Identifier: MIT
 * Locked first-vector handlers: 0x417c2e, 0x416026, 0x432938 and SysTick
 * 0x41b428. The three loops are real nonreturning stock behavior. SysTick is
 * the FreeRTOS port tick (xPortSysTickHandler): raise BASEPRI to the syscall
 * priority, advance the tick and pend PendSV on a switch, restore BASEPRI.
 */
#include <stdint.h>

#include "apollo510.h"

extern uint32_t opencfw_bl_tick_increment(void);

__attribute__((noreturn)) void opencfw_boot_nmi_loop(void)
{
    for (;;) {
    }
}

__attribute__((noreturn)) void opencfw_boot_fault_loop(void)
{
    for (;;) {
    }
}

__attribute__((noreturn)) void opencfw_boot_reserved_loop(void)
{
    for (;;) {
    }
}

/* CMSIS 5.9 cmsis_gcc.h only provides __get/__set_BASEPRI for v7-M/v8-M
 * Mainline, not the v8.1-M Cortex-M55, so the register moves are spelled out. */
static inline uint32_t basepri_read(void)
{
    uint32_t value;

    __asm__ volatile("mrs %0, basepri" : "=r"(value));
    return value;
}

static inline void basepri_write(uint32_t value)
{
    __asm__ volatile("msr basepri, %0" : : "r"(value) : "memory");
}

void opencfw_boot_systick_entry(void)
{
    const uint32_t saved_basepri = basepri_read();

    basepri_write(48u);
    __DSB();
    __ISB();
    if (opencfw_bl_tick_increment() != 0u)
        SCB->ICSR = SCB_ICSR_PENDSVSET_Msk;
    basepri_write(saved_basepri);
    __DSB();
    __ISB();
}
