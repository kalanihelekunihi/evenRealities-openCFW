#include <stdint.h>

/* Native ROM 0x78c9a4..0x78c9b3. The following bytes at 0x78c9b4
 * begin the distinct "IDLE" string. */
const uint8_t audio_ble_comm_profile_table[16] = {
    0x09u, 0x00u, 0x01u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u,
    0x02u, 0x00u, 0x01u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u
};

/* Native RAM 0x20074358, assigned by bleCommHandlerInit 0x4b7e74. */
const uint8_t *audio_ble_comm_profile_slot;
