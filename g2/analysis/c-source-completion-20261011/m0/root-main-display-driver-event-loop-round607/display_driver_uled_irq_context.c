/* Apollo S200 IRQ_Context at 0x44900e. */
#include <stdint.h>

extern uint32_t display_driver_uled_scheduler_state_4558a4(void);

uint32_t display_driver_uled_irq_context_44900e(void) {
    uint32_t ipsr, primask, basepri;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr != 0u) return 1u;
    if (display_driver_uled_scheduler_state_4558a4() == 1u) return 0u;
    __asm__ volatile("mrs %0, primask" : "=r"(primask));
    if (primask != 0u) return 1u;
    __asm__ volatile("mrs %0, basepri" : "=r"(basepri));
    return basepri != 0u ? 1u : 0u;
}
