/* Apollo timing delay 0x4807a0. VFP operations retain native rounding.
 * ROM call 0x00000040 is a separate provider boundary.
 */
#include <stdint.h>
extern void display_driver_uled_rom_delay_00000040(uint32_t);

void display_driver_uled_delay_4807a0(uint32_t duration) {
    uint32_t ticks;
    __asm__ volatile(
        "vmov s0, %1\n\t"
        "vcvt.f32.u32 s0, s0\n\t"
        "vcvt.u32.f32 s0, s0, #5\n\t"
        "vmov %0, s0"
        : "=r"(ticks) : "r"(duration) : "s0");
    uint32_t threshold=15u;
    uint32_t clock_mode=*(volatile uint32_t *)(uintptr_t)0x40021000u;
    if (((clock_mode >> 3u) & 3u) == 2u) {
        uint32_t scaled;
        const uint32_t multiplier_bits=0x437a0000u; /* 250.0f */
        const uint32_t divisor_bits=0x42c00000u;    /* 96.0f */
        __asm__ volatile(
            "vmov s0, %1\n\t"
            "vcvt.f32.u32 s0, s0\n\t"
            "vmov s1, %2\n\t"
            "vmul.f32 s0, s0, s1\n\t"
            "vmov s1, %3\n\t"
            "vdiv.f32 s0, s0, s1\n\t"
            "vcvt.u32.f32 s0, s0\n\t"
            "vmov %0, s0"
            : "=r"(scaled)
            : "r"(ticks),"r"(multiplier_bits),"r"(divisor_bits)
            : "s0","s1");
        ticks=scaled;
        threshold=24u;
    }
    if (ticks > threshold)
        display_driver_uled_rom_delay_00000040(ticks-threshold);
}
