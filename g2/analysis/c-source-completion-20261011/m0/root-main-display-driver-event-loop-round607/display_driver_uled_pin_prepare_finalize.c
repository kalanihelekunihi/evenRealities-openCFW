/* Apollo type-4 prepare finalizer 0x4c3ef4 and bounded wait 0x4c387e.
 * Candidate C bodies; delay remains a lower provider import.
 */
#include <stdint.h>
extern uint32_t display_driver_uled_irq_save_473940(void);
extern void display_driver_uled_delay_4807a0(uint32_t);

void display_driver_uled_pin_prepare_wait_4c387e(volatile uint8_t *flag,
                                                   uint32_t *remaining) {
    while (*remaining != 0u && *flag != 0u) {
        display_driver_uled_delay_4807a0(10u);
        *remaining -= 1u;
    }
}

void display_driver_uled_pin_prepare_finalize_4c3ef4(uint32_t *remaining) {
    volatile uint8_t *flag=(volatile uint8_t *)(uintptr_t)0x20074f57u;
    if (*flag != 0u) {
        display_driver_uled_pin_prepare_wait_4c387e(flag,remaining);
        uint32_t prior_mask=display_driver_uled_irq_save_473940();
        *(volatile uint8_t *)(uintptr_t)0x20074f59u=1u;
        *flag=0u;
        *(volatile uint32_t *)(uintptr_t)0x20074264u=0u;
        __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    }
}
