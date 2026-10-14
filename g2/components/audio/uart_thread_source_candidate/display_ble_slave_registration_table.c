/* Apollo Main compressed SRAM record 0x75d3f4 initializes the mutable
 * advertising intervals at 0x200003e0. The next object begins at
 * 0x200003ec; absolute RAM placement remains a linker gate. */
#include <stdint.h>

uint8_t audio_ble_slave_registration_table[12u] = {
    0x30u, 0x75u, 0x00u, 0x00u, 0x00u, 0x00u,
    0xa0u, 0x00u, 0x40u, 0x06u, 0x00u, 0x00u,
};
