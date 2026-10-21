/* Apollo MAIN 0x57A48A: NVIC external interrupt disable. */
#include <stdint.h>

void audio_irq_disable(int32_t irq) {
    int16_t number = (int16_t)irq;
    if (number < 0) return;
    uint32_t bit = 1u << ((uint32_t)irq & 31u);
    volatile uint32_t * const icer = (volatile uint32_t *)0xe000e180u;
    icer[(uint16_t)number >> 5] = bit;
    __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
}
