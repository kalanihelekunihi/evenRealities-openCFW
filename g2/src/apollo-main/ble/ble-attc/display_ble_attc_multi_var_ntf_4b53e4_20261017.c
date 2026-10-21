/* Cordio attcProcMultiVarNtf at stock Main 0x4b53e4. */
#include <stdint.h>

extern uint8_t audio_ble_att_common_state[];

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_att_event_t;

void audio_ble_attc_proc_multi_ntf_4b53e4(uint8_t *ccb, uint16_t length,
                                           const uint8_t *packet)
{
    const uint8_t *main_ccb = *(uint8_t *const *)ccb;
    audio_att_event_t event = {0};
    event.param = main_ccb[0x0eu];
    event.event = (uint8_t)((packet[8u] & (uint8_t)~1u) / 2u);
    event.value = packet + 9u;
    event.value_length = (uint16_t)(length - 1u);
    void (*callback)(const audio_att_event_t *) =
        *(void (**)(const audio_att_event_t *))(audio_ble_att_common_state + 0x58u);
    if (callback != 0)
        callback(&event);
    uint8_t *control = (uint8_t *)main_ccb + ((uint32_t)ccb[0x28u] * 4u) + 2u;
    *control |= 0x10u;
}
