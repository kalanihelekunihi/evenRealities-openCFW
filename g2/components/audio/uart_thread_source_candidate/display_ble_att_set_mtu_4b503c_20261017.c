/* Cordio attSetMtu at stock Main 0x4b503c. */
#include <stdint.h>

extern void audio_ble_att_exec_callback_4b5074(uint8_t, uint8_t,
                                                uint16_t, uint8_t, uint16_t);

void audio_ble_att_set_mtu_4b503c(uint8_t *main_ccb, uint8_t slot,
                                  uint16_t peer, uint16_t local)
{
    const uint16_t negotiated = peer < local ? peer : local;
    uint8_t *row = main_ccb + (uint32_t)slot * 4u;
    const uint16_t current = (uint16_t)row[0] | ((uint16_t)row[1] << 8);
    if (current == negotiated)
        return;
    row[0] = (uint8_t)negotiated;
    row[1] = (uint8_t)(negotiated >> 8);
    audio_ble_att_exec_callback_4b5074(main_ccb[0x0eu], 0x16u,
                                       0u, 0u, negotiated);
}
