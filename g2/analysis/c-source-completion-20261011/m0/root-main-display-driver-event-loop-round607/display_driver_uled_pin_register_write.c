/* Apollo pin register writer 0x480f0c. Candidate, fixed address map. */
#include <stdint.h>

extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_pin_register_write_480f0c(uint32_t pin,uint32_t value) {
    if (pin >= 0xe0u) return 5u;
    uint32_t word=pin>>5u;
    uint32_t bit=1u<<(pin&31u);
    uint32_t existing=*(volatile uint32_t *)(uintptr_t)(0x00768ba8u+4u*word);
    if ((existing & bit)==0u) {
        if (((value>>10u)&3u)>=2u &&
            (*(volatile uint32_t *)(uintptr_t)(0x00768bc4u+4u*word)&bit)==0u)
            return 7u;
    } else {
        uint32_t mode=(value>>13u)&7u;
        if (mode!=0u && mode!=6u && mode!=1u)return 7u;
    }
    uint32_t prior=display_driver_uled_irq_save_473940();
    *(volatile uint32_t *)(uintptr_t)0x40010400u=0x73u;
    *(volatile uint32_t *)(uintptr_t)(0x40010000u+4u*pin)=value;
    *(volatile uint32_t *)(uintptr_t)0x40010400u=0u;
    __asm__ volatile("msr primask, %0" :: "r"(prior) : "memory");
    return 0u;
}
