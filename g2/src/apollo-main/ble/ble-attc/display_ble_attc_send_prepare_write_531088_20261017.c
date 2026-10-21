/* Cordio attcSendPrepWriteReq; stock Main 0x531088. */
#include <stdint.h>
extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];
extern uint8_t *attMsgAlloc(uint16_t);
extern void audio_ble_attc_req_clear_531af2(uint8_t, uint8_t *, uint8_t);
extern void WsfTimerStartSec(void *, uint32_t);
extern void attL2cDataReq(uint8_t *, uint8_t, uint16_t, uint8_t *);
static uint16_t read16(const uint8_t *p) { return (uint16_t)p[0] | ((uint16_t)p[1] << 8); }
void audio_ble_attc_send_prepare_write_531088(uint8_t *ccb)
{
    uint8_t *packet;
    uint16_t data_length;
    if (ccb[7] == 1u) {
        uint8_t *main_ccb = *(uint8_t **)ccb;
        const uint16_t mtu = read16(main_ccb + (uint32_t)ccb[0x28] * 4u);
        const uint16_t pending = read16(ccb + 0x10);
        const uint16_t maximum = (uint16_t)(mtu - 5u);
        data_length = pending < maximum ? pending : maximum;
        packet = attMsgAlloc((uint16_t)(data_length + 13u));
        if (!packet) {
            audio_ble_attc_req_clear_531af2(ccb[0x29], ccb + 4u, 0x70u);
            return;
        }
        const uint8_t *stored = *(uint8_t **)(ccb + 8u);
        const uint8_t *value = *(uint8_t **)(ccb + 0x14u);
        for (uint32_t i = 0; i < 13u; ++i) packet[i] = stored[i];
        for (uint32_t i = 0; i < data_length; ++i) packet[13u + i] = value[i];
        *(uint8_t **)(ccb + 0x14u) = (uint8_t *)(value + data_length);
        const uint16_t remaining = (uint16_t)(pending - data_length);
        ccb[0x10] = (uint8_t)remaining;
        ccb[0x11] = (uint8_t)(remaining >> 8);
    } else {
        data_length = read16(ccb + 0x10);
        packet = *(uint8_t **)(ccb + 8u);
        *(uint32_t *)(ccb + 8u) = 0u;
    }
    const uint16_t offset = read16(ccb + 0x12u);
    packet[11] = (uint8_t)offset;
    packet[12] = (uint8_t)(offset >> 8);
    const uint16_t new_offset = (uint16_t)(offset + data_length);
    ccb[0x12] = (uint8_t)new_offset;
    ccb[0x13] = (uint8_t)(new_offset >> 8);
    ccb[0x22] = 0x14u;
    const uint32_t cfg_address = *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
    WsfTimerStartSec(ccb + 0x18u, ((const uint8_t *)(uintptr_t)cfg_address)[6]);
    attL2cDataReq(*(uint8_t **)ccb, ccb[0x0eu], (uint16_t)(data_length + 5u), packet);
}
