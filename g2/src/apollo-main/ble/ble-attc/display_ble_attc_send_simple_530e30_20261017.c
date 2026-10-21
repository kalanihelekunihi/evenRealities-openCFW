/* Cordio attcSendSimpleReq at stock Main 0x530e30. */
#include <stdint.h>

extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];
extern void WsfTimerStartSec(void *, uint32_t);
extern void attL2cDataReq(uint8_t *, uint8_t, uint16_t, uint8_t *);

void audio_ble_attc_send_simple_530e30(uint8_t *ccb)
{
    uint8_t *packet = *(uint8_t **)(ccb + 8u);
    *(uint32_t *)(ccb + 8u) = 0u;
    if (ccb[6u] != 10u) {
        ccb[0x22u] = 0x14u;
        const uint32_t config_address =
            *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
        const uint8_t *config = (const uint8_t *)(uintptr_t)config_address;
        WsfTimerStartSec(ccb + 0x18u, config[6u]);
    }
    const uint16_t length = (uint16_t)packet[0] | ((uint16_t)packet[1] << 8);
    attL2cDataReq(*(uint8_t **)ccb, ccb[0x0eu], length, packet);
}
