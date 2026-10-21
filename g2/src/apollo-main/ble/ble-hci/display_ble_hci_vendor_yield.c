/* Native vendor delay 0x4807a0. ROM 0x4807f0/f4/f8 authenticate
 * 250.0f, 96.0f and live 0x40021000 clock configuration. The 0x40
 * cycle-delay target is populated from the official payload's ITCM
 * decompression record; its boot copy remains a separate contract. */
#include <stdint.h>

extern void audio_ble_vendor_cycle_delay_rom_00000040(uint32_t);

void audio_ble_vendor_yield_4807a0(uint32_t duration) {
    uint32_t fixed;
    __asm volatile("vmov s0, %1\n\t"
                   "vcvt.f32.u32 s0, s0\n\t"
                   "vcvt.u32.f32 s0, s0, #5\n\t"
                   "vmov %0, s0"
                   : "=r"(fixed) : "r"(duration) : "s0");
    uint32_t overhead=15u;
    volatile uint32_t *const mode=(volatile uint32_t *)(uintptr_t)0x40021000u;
    if(((*mode>>3u)&3u)==2u) {
        float scaled=((float)fixed*250.0f)/96.0f;
        fixed=(scaled>0.0f)?(uint32_t)scaled:0u;
        overhead=24u;
    }
    if(fixed>overhead)
        audio_ble_vendor_cycle_delay_rom_00000040(fixed-overhead);
}
