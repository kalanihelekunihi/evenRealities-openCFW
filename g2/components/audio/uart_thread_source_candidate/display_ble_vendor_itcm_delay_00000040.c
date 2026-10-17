/* Exact positive-count Thumb loop decoded from Apollo Main ITCM record.
 * The zero-count input intentionally wraps, matching the original loop. */
#include <stdint.h>

__attribute__((naked, used, section(".text.opencfw.itcm.delay_00000040")))
void audio_ble_vendor_cycle_delay_rom_00000040(uint32_t iterations __attribute__((unused))) {
    __asm__ volatile(
        "1: subs r0, #1\n"
        "   bne 1b\n"
        "   bx lr\n");
}
