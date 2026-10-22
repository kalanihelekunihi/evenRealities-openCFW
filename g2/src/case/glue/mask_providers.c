#include <stdint.h>

/* CASE stock 0x080000f4..0x080000fc. */
/* Stock 0x080000F4 (ulSetInterruptMaskFromISR) */
uint32_t case_mask_save(void)
{
    uint32_t before;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(before) : : "memory");
    return before;
}

/* CASE stock 0x080000fc..0x08000102. */
/* Stock 0x080000FC (vClearInterruptMaskFromISR) */
void case_mask_restore(uint32_t before)
{
    __asm__ volatile("msr primask, %0" : : "r"(before) : "memory");
}
