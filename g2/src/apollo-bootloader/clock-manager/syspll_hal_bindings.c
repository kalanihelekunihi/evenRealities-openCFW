/* AmbiqSuite HAL entry point that the upstream am_hal_syspll.c needs and that
 * the bootloader does not yet build from upstream (am_hal_sysctrl.c). The body
 * is the stock bootloader's and matches the SDK source line for line. Delete
 * it when am_hal_sysctrl.c joins the bootloader build. */
#include "am_mcu_apollo.h"

static uint32_t critical_save(void)
{
    uint32_t previous;
    __asm volatile("mrs %0, primask\n\tcpsid i"
                   : "=r"(previous) :: "memory");
    return previous;
}

static void critical_restore(uint32_t previous)
{
    __asm volatile("msr primask, %0" :: "r"(previous) : "memory");
}

/* Stock 0x41AC92: HALSTATE PLL_FREFSEL (0x40008858 bit 6) under PRIMASK. */
void am_hal_sysctrl_clkmuxrst_pll_fref_update(MCUCTRL_PLLCTL0_FREFSEL_Enum eFref)
{
    const uint32_t previous = critical_save();
    volatile uint32_t *const halstate =
        (volatile uint32_t *)(uintptr_t)0x40008858u;
    *halstate = (*halstate & 0xffffffbfu) | (((uint32_t)eFref & 1u) << 6);
    critical_restore(previous);
}

