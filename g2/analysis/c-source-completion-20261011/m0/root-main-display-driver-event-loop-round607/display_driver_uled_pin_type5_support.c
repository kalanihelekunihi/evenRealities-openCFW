/* Apollo type-5 wait/finalize and power configuration providers. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_delay_4807a0(uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);

void display_driver_uled_wait_flag_4c387e(volatile uint8_t *flag,uint32_t *remaining) {
    while (*remaining!=0u && *flag!=0u) {
        (void)display_driver_uled_delay_4807a0(10u);
        *remaining=*remaining-1u;
    }
}

void display_driver_uled_pin_type5_finalize_4c4058(uint32_t *remaining) {
    volatile uint8_t *flag=(volatile uint8_t *)(uintptr_t)0x20074f58u;
    if (*flag==0u)return;
    display_driver_uled_wait_flag_4c387e(flag,remaining);
    uint32_t prior=display_driver_uled_irq_save_473940();
    *flag=0u;
    *(volatile uint32_t *)(uintptr_t)0x20074268u=0u;
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
}

uint32_t display_driver_uled_power_config_4d3992(const volatile void *config) {
    if(config==0)return 6u;
    const volatile uint8_t *bytes=(const volatile uint8_t *)config;
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)0x4000404cu;
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40004048u;
    volatile uint32_t *timing=(volatile uint32_t *)(uintptr_t)0x40004050u;
    *enable=*enable|7u;
    *control=(*control & ~0x20000000u)|((uint32_t)(bytes[0]&1u)<<29u);
    *timing=(*timing & ~3u)|(uint32_t)(bytes[1]&3u);
    uint32_t word=*(const volatile uint32_t *)(const void *)(bytes+4);
    *timing=(*timing & 0x80000003u)|((word&0x1fffffffu)<<2u);
    *control=*control|1u;
    return 0u;
}
