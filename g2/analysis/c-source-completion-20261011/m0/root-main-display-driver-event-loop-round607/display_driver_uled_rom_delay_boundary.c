/* Apollo resident ROM boundary called by 0x4807ea. This supplies a linkable
 * Thumb call to the original 0x00000040 entry; it does not implement or
 * validate the ROM routine or its hardware timing contract.
 */
#include <stdint.h>

void display_driver_uled_rom_delay_00000040(uint32_t ticks) {
    void (*const resident_delay)(uint32_t)=(void (*)(uint32_t))(uintptr_t)0x41u;
    resident_delay(ticks);
}
