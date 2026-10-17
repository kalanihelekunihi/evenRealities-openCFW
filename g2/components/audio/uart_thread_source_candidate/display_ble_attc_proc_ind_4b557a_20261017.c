/* Cordio attcProcInd at stock Main 0x4b557a. */
#include <stdint.h>

extern uint8_t audio_ble_att_common_state[];
extern uint8_t audio_ble_attc_state[];
extern uint8_t *attMsgAlloc(uint16_t);
extern void L2cDataReq(uint16_t, uint16_t, uint16_t, uint8_t *);

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_attc_ind_event_t;

void audio_ble_attc_proc_ind_4b557a(uint8_t *ccb, uint16_t length,
                                     const uint8_t *packet)
{
    if (length < 3u)
        return;

    uint8_t *main_ccb = *(uint8_t **)ccb;
    const uint8_t slot = ccb[0x28u];
    uint8_t *control = main_ccb + (uint32_t)slot * 4u + 2u;
    audio_attc_ind_event_t event = {0};
    event.param = main_ccb[0x0eu];
    event.event = (uint8_t)((packet[8u] & (uint8_t)~1u) / 2u);
    event.value = packet + 11u;
    event.value_length = (uint16_t)(length - 3u);
    event.handle = (uint16_t)packet[9u] | ((uint16_t)packet[10u] << 8);
    void (*callback)(const audio_attc_ind_event_t *) =
        *(void (**)(const audio_attc_ind_event_t *))(audio_ble_att_common_state + 0x58u);
    if (event.handle != 0u && callback != 0)
        callback(&event);

    if (audio_ble_attc_state[0x1b4u] != 0u && event.event == 0x0eu) {
        if ((*control & 0x02u) == 0u) {
            uint8_t *confirm = attMsgAlloc(9u);
            if (confirm != 0) {
                confirm[8u] = 0x1eu;
                const uint16_t link_handle =
                    (uint16_t)main_ccb[0x0cu] | ((uint16_t)main_ccb[0x0du] << 8);
                L2cDataReq(4u, link_handle, 1u, confirm);
            }
        }
        return;
    }
    *control |= 0x10u;
}
