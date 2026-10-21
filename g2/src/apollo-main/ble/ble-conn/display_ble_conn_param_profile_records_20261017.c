/* Native connection-parameter profile records adjacent to the existing
 * 0x784eb0 message-transport profile. Each record is exactly 16 bytes. */
#include <stdint.h>

const uint8_t audio_ble_conn_param_slow_profile_784ea0[16]
    __attribute__((section(".g2_rom_00784ea0"), used, aligned(4))) = {
        0x00, 0x00, 0x00, 0x00,
        0x48, 0x00, 0x54, 0x00,
        0x04, 0x00, 0x58, 0x02,
        0x05, 0x00, 0x00, 0x00
    };

const uint8_t audio_ble_conn_param_fast_profile_784ec0[16]
    __attribute__((section(".g2_rom_00784ec0"), used, aligned(4))) = {
        0x00, 0x00, 0x00, 0x00,
        0x0c, 0x00, 0x18, 0x00,
        0x00, 0x00, 0x58, 0x02,
        0x05, 0x00, 0x00, 0x00
    };
