/* Apollo type-2 bus-status read 0x480c56 and prepare finalize 0x4c3d70.
 * Candidate; status register and global cells retain observed addresses.
 */
#include <stdint.h>
extern void display_driver_uled_pin_prepare_wait_4c387e(volatile uint8_t *,uint32_t *);
extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_pin_bus_status_480c56(uint8_t *out) {
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)0x4002012cu;
    if ((*status & 0x100u) != 0u) *out=2u;
    else if ((*status & 1u) != 0u) *out=1u;
    else *out=0u;
    return 0u;
}

void display_driver_uled_pin_prepare_type2_finalize_4c3d70(uint32_t *remaining) {
    volatile uint8_t *flag=(volatile uint8_t *)(uintptr_t)0x20074f56u;
    if (*flag != 0u) {
        display_driver_uled_pin_prepare_wait_4c387e(flag,remaining);
        uint32_t prior_mask=display_driver_uled_irq_save_473940();
        *flag=0u;
        *(volatile uint32_t *)(uintptr_t)0x20074260u=0u;
        __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    }
}
