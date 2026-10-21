#include "timing.h"
uint32_t audio_save_irq(void) {
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    return saved;
}
void audio_delay_cycles(uint32_t count) {
    /* Reconstructed source loop, not a copied ITCM opcode array. */
    do { __asm__ volatile("" ::: "memory"); } while (--count);
}
static float float_from_uint(uint32_t x) {
    float y;
    __asm__ volatile("vmov %0,%1\n\tvcvt.f32.u32 %0,%0" : "=&t"(y) : "r"(x));
    return y;
}
static uint32_t fixed32(float x) {
    __asm__ volatile("vcvt.u32.f32 %0,%0,#5" : "+t"(x));
    uint32_t result;
    __asm__ volatile("vmov %0,%1" : "=r"(result) : "t"(x));
    return result;
}
static uint32_t high_performance_iterations(uint32_t count) {
    float x = float_from_uint(count), ratio_numerator = 250.0f, divisor = 96.0f;
    __asm__ volatile("vmul.f32 %0,%0,%1\n\tvdiv.f32 %0,%0,%2\n\tvcvt.u32.f32 %0,%0"
                     : "+t"(x) : "t"(ratio_numerator), "t"(divisor));
    uint32_t result;
    __asm__ volatile("vmov %0,%1" : "=r"(result) : "t"(x));
    return result;
}
void audio_delay_us(uint32_t microseconds) {
    uint32_t count = fixed32(float_from_uint(microseconds));
    uint32_t overhead;
    if (((*(volatile uint32_t *)0x40021000 >> 3) & 3) == 2) {
        count = high_performance_iterations(count);
        overhead = 24;
    } else {
        overhead = 15;
    }
    if (count > overhead) audio_delay_cycles(count - overhead);
}
uint32_t audio_wait4(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected) {
    for (;;) {
        if ((*(volatile uint32_t *)address & mask) == expected) return 0;
        if (!budget--) return 4;
        audio_delay_us(1);
    }
}
uint32_t audio_wait5(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected,uint32_t equal) {
    for (;;) {
        uint32_t matched = (*(volatile uint32_t *)address & mask) == expected;
        if ((uint8_t)equal ? matched : !matched) return 0;
        if (!budget--) return 4;
        audio_delay_us(1);
    }
}
