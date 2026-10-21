/* Apollo Main compressed SRAM record 0x75d3f4 initializes these mutable
 * master target and security cells at 0x200003c0, 0x200003c8 and
 * 0x200003d8. Their selected connect/security paths later update them.
 * Gaps between objects and absolute RAM placement remain linker gates. */
#include <stdint.h>

uint8_t audio_ble_master_target_address[6u] = {
    0x87u, 0x20u, 0xc3u, 0x59u, 0xf8u, 0xc4u,
};
char audio_ble_master_target_name[15u] = "EVEN R1_XXXXXX";
volatile uint8_t audio_ble_master_security_address[7u] = {
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0xffu,
};
