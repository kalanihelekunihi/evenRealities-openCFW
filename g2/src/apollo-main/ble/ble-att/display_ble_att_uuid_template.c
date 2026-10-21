/* Apollo Main compressed SRAM record 0x75d3f4 initializes the mutable
 * 16-byte ATT UUID template at native 0x2000044c. The discovery path
 * replaces bytes 12 and 13 for UUID16 comparison. Exact RAM placement
 * and whole startup scatter remain open. */
#include <stdint.h>

uint8_t audio_ble_att_uuid_base_2000044c[16u] = {
    0xfbu, 0x34u, 0x9bu, 0x5fu, 0x80u, 0x00u, 0x00u, 0x80u,
    0x00u, 0x10u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u,
};
