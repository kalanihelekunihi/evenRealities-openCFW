/* SPDX-License-Identifier: MIT
 * Stock 0x41b670 tickless STIMER service and 0x41b6e2 vector wrapper.
 * Hardware timer cadence and actual ISR scheduling remain unqualified.
 */
#include <stdint.h>
#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))

extern uint32_t opencfw_bl_port_timer_read_counter(void);
extern uint32_t opencfw_bl_port_timer_compare_set(uint32_t compare_id,
                                                  uint32_t delta);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern uint32_t opencfw_bl_tick_increment(void);

static uint32_t native_udiv(uint32_t numerator, uint32_t denominator)
{
    uint32_t quotient;
    __asm__ volatile("udiv %0, %1, %2"
                     : "=r"(quotient) : "r"(numerator), "r"(denominator));
    return quotient;
}

/* Stock 0x41f4c0: the vector wrapper at 0x41b6e2 passes zero and observes
 * the raw STIMER status. Other callers may request status masked by INTEN. */
uint32_t opencfw_boot_stimer_irq_status(uint8_t masked)
{
    uint32_t status = WORD(UINT32_C(0x40008904));
    if (masked != 0u)
        status &= WORD(UINT32_C(0x40008900));
    return status;
}

void opencfw_boot_stimer_tickless_service(void)
{
    const uint32_t current = opencfw_bl_port_timer_read_counter();
    const uint32_t last = WORD(UINT32_C(0x20027120));
    const uint32_t elapsed = current - last - (current < last ? 1u : 0u);
    const uint32_t ticks = native_udiv(elapsed, WORD(UINT32_C(0x20027124)));
    const uint32_t remainder_quotient =
        native_udiv(elapsed, WORD(UINT32_C(0x20027124)));
    const uint32_t remainder = elapsed -
        WORD(UINT32_C(0x20027124)) * remainder_quotient;
    WORD(UINT32_C(0x20027120)) = current - remainder;
    (void)opencfw_bl_port_timer_compare_set(
        0u, WORD(UINT32_C(0x20027124)) - remainder);
    (void)opencfw_bl_mask_interrupts();
    uint32_t remaining_ticks = ticks;
    uint32_t reschedule = 0u;
    while (remaining_ticks-- != 0u)
        if (opencfw_bl_tick_increment() != 0u)
            reschedule = 1u;
    if (reschedule)
        WORD(UINT32_C(0xe000ed04)) = UINT32_C(0x10000000);
    __asm__ volatile("msr basepri, %0\n dsb sy\n isb sy" :: "r"(0u) : "memory");
}

void opencfw_boot_stimer_irq(void)
{
    if ((opencfw_boot_stimer_irq_status(0u) & 1u) != 0u) {
        WORD(UINT32_C(0x40008908)) = 1u;
        (void)WORD(UINT32_C(0x40008904));
        opencfw_boot_stimer_tickless_service();
    }
}
