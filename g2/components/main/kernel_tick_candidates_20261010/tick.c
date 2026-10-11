#include <stdint.h>

/* Stock literal pool: 0x4557ac -> 0x20074a34; 0x456064/68 -> state words. */
#define TICK_WORD (*(volatile uint32_t *)0x20074a34u)
#define SCHEDULER_ACTIVE (*(volatile uint32_t *)0x20074a3cu)
#define SCHEDULER_SUSPENDED (*(volatile uint32_t *)0x20074a58u)

uint32_t g2_kernel_candidate_scheduler_state(void) {
    if (SCHEDULER_ACTIVE == 0u) return 1u;
    if (SCHEDULER_SUSPENDED == 0u) return 2u;
    return 0u;
}

/* Explicit ARM MRS: these are the stock 0x449012/26/2e architectural reads. */
uint32_t g2_kernel_candidate_is_irq(void) {
    uint32_t value;
    __asm__ volatile ("mrs %0, ipsr" : "=r"(value));
    if (value != 0u) return 1u;
    if (g2_kernel_candidate_scheduler_state() == 1u) return 0u;
    __asm__ volatile ("mrs %0, primask" : "=r"(value));
    if (value != 0u) return 1u;
    __asm__ volatile ("mrs %0, basepri" : "=r"(value));
    return value != 0u;
}

uint32_t g2_kernel_candidate_get_tick(void) { return TICK_WORD; }
uint32_t g2_kernel_candidate_get_tick_from_isr(void) { return TICK_WORD; }
uint32_t g2_kernel_candidate_os_get_tick(void) {
    return g2_kernel_candidate_is_irq() ?
        g2_kernel_candidate_get_tick_from_isr() : g2_kernel_candidate_get_tick();
}

/* FlashDB's observed tick import has the same no-argument CMSIS contract. */
uint32_t g2_flashdb_candidate_tick(void) {
    return g2_kernel_candidate_os_get_tick();
}
