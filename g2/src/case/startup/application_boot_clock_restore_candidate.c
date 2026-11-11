/* SPDX-License-Identifier: MIT
 * Native CASE 0x4eec boot clock source selection and fallback.
 */
#include <stdint.h>
extern uint32_t case_transfer_clock_config(uint32_t plan); /* 0x4f14 */
extern void case_clock_priority_config(uint32_t irq,uint32_t plan,uint32_t unused); /* 0x5024 -> 0x91ac */
/* Stock 0x08004FB0 (case_enable_interrupt_source) */
void case_boot_clock_fallback(void) /* 0x4fb0 */
{
    volatile uint32_t *osc=(volatile uint32_t *)(uintptr_t)0x40021040u;
    volatile uint32_t *config=(volatile uint32_t *)(uintptr_t)0x4002103cu;
    volatile uint32_t *system=(volatile uint32_t *)(uintptr_t)0x40010000u;
    *osc|=1u;
    (void)(*osc&1u);
    *config|=0x10000000u;
    (void)(*config&0x10000000u);
    case_clock_priority_config((uint32_t)-2,3u,0u);
    *system=(*system&~0x600u)|0x600u;
}
/* Stock 0x08004EEC (case_initialize_serial_block) */
void case_boot_clock_restore(void)
{
    /* Boot-test fix: stock sets FLASH_ACR PRFTEN (0x40022000 |= 0x40022000>>22
     * = 0x100, HAL_Init prefetch). The reduction had RCC_CR |= 0x1000. */
    volatile uint32_t *flash_acr=(volatile uint32_t *)(uintptr_t)0x40022000u;
    *flash_acr|=0x100u;
    if(case_transfer_clock_config(3u)==0u)case_boot_clock_fallback();
}
