/* SPDX-License-Identifier: MIT */
/* Recovered watchdog control: one read and one write, clearing enable bit. */
#include <stdint.h>
void open_cfw_gx8002_watchdog_stop(void)
{
    volatile uint32_t *control = (volatile uint32_t *)(uintptr_t)0xA0700000U;
    uint32_t value = *control;
#ifdef OPEN_CFW_GX8002_WATCHDOG_HOST_TEST
    value &= ~UINT32_C(1);
#else
    /* GCC csky_split_and selects 32-bit ANDNI before BCLRI. The low-register
     * read/write constraint selects the understood 16-bit instruction needed
     * by this fixed entry's 12-byte envelope. No memory or flags are changed.
     */
    __asm__("bclri %0, 0" : "+a" (value));
#endif
    *control = value;
}
