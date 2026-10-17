/* Cordio attcPendWriteCmd; stock Main 0x530d74, one pending handle slot. */
#include <stdint.h>
uint8_t audio_ble_attc_pend_write_cmd_530d74(const uint8_t *ccb, uint16_t handle)
{
    const uint16_t pending = (uint16_t)ccb[0x2au] | ((uint16_t)ccb[0x2bu] << 8);
    if (pending != 0u && pending == handle)
        return 1u;
    return pending != 0u;
}
