/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * 16-byte device-manager prefix at 0x2000060c. Both C consumer names refer
 * to the same native state. The complete native allocation extent and
 * absolute pointer/code placement remain separate gates. */
#include <stdint.h>

_Alignas(4) uint8_t audio_device_manager_state[16u] = {
    0x41u, 0x62u, 0x4cu, 0x00u, 0xa5u, 0x64u, 0x4cu, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u,
};
__asm__(".global audio_ble_device_manager_state\n"
        ".set audio_ble_device_manager_state,audio_device_manager_state");
