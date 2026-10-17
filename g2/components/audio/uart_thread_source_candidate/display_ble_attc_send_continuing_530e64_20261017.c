/* Cordio attcSendContinuingReq at stock Main 0x530e64. */
#include <stdint.h>

extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];
extern uint8_t *attMsgAlloc(uint16_t);
extern void audio_ble_attc_req_clear_531af2(uint8_t, uint8_t *, uint8_t);
extern void WsfTimerStartSec(void *, uint32_t);
extern void attL2cDataReq(uint8_t *, uint8_t, uint16_t, uint8_t *);

static uint16_t read16(const uint8_t *data)
{
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

static void write16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

void audio_ble_attc_send_continuing_530e64(uint8_t *ccb)
{
    uint8_t *stored = *(uint8_t **)(ccb + 8u);
    uint8_t *packet;
    if (ccb[7u] == 1u) {
        const uint16_t payload_length = read16(stored);
        packet = attMsgAlloc((uint16_t)(payload_length + 8u));
        if (packet == 0) {
            audio_ble_attc_req_clear_531af2(ccb[0x29u], ccb + 4u, 0x70u);
            return;
        }
        for (uint32_t index = 0u; index < (uint32_t)payload_length + 8u; ++index)
            packet[index] = stored[index];
    } else {
        packet = stored;
        *(uint32_t *)(ccb + 8u) = 0u;
    }

    uint8_t *fields = packet + 9u;
    if (ccb[6u] == 6u) {
        fields += 2u;
        write16(fields, read16(ccb + 0x12u));
    } else {
        write16(fields, read16(ccb + 0x12u));
        write16(fields + 2u, read16(ccb + 0x14u));
    }
    ccb[0x22u] = 0x14u;
    const uint32_t config_address =
        *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
    const uint8_t *config = (const uint8_t *)(uintptr_t)config_address;
    WsfTimerStartSec(ccb + 0x18u, config[6u]);
    attL2cDataReq(*(uint8_t **)ccb, ccb[0x0eu], read16(packet), packet);
}
