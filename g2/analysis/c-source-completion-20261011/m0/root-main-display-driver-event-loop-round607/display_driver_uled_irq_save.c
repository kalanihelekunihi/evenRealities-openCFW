/* Apollo interrupt save/disable provider 0x473940. Candidate. */
#include <stdint.h>
uint32_t display_driver_uled_irq_save_473940(void) {
    uint32_t prior_mask;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(prior_mask) :: "memory");
    return prior_mask;
}
