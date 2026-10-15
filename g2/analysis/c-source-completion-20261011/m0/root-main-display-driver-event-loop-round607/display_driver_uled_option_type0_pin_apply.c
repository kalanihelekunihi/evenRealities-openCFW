/* Apollo S200 pin configuration writer at 0x480f0c. */
#include <stdint.h>

extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_pin_apply_480f0c(uint32_t pin,uint32_t configuration) {
    if (pin>=224u) return 5u;
    uint32_t mask=1u<<(pin&31u);
    uint32_t bank=pin>>5;
    uint32_t capability=*(const uint32_t *)(uintptr_t)(0x768ba8u+bank*4u);
    if ((capability&mask)==0u) {
        if (((configuration>>10)&3u)>=2u &&
            ((*(const uint32_t *)(uintptr_t)(0x768bc4u+bank*4u))&mask)==0u)
            return 7u;
    } else {
        uint32_t function=(configuration>>13)&7u;
        if (function!=0u && function!=1u && function!=6u) return 7u;
    }
    uint32_t saved=display_driver_uled_irq_save_473940();
    *(volatile uint32_t *)(uintptr_t)0x40010400u=0x73u;
    *(volatile uint32_t *)(uintptr_t)(0x40010000u+pin*4u)=configuration;
    *(volatile uint32_t *)(uintptr_t)0x40010400u=0u;
    __asm__ volatile("msr PRIMASK, %0" :: "r"(saved) : "memory");
    return 0u;
}
