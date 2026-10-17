/* Cordio attcProcErrRsp 0x4b5230 and attcFreePkt 0x531ac0. */
#include <stdint.h>

extern void WsfMsgFree(void *);

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_attc_error_event_t;

void audio_attc_rsp_error_4b5230(uint8_t *ccb, uint16_t length,
                                 const uint8_t *packet,
                                 audio_attc_error_event_t *event)
{
    (void)length;
    const uint8_t request = ccb[6u];
    event->event = request;
    const uint8_t *cursor = packet + 10u;
    if (request == 5u || request == 6u || request == 9u || request == 11u) {
        cursor += 2u;
    } else {
        event->handle = (uint16_t)cursor[0] | ((uint16_t)cursor[1] << 8);
        cursor += 2u;
    }
    event->status = *cursor;
    if (event->status == 0u)
        event->status = 0x75u;
    event->value_length = 0u;
}

void audio_ble_attc_free_pkt_531ac0(uint8_t *message)
{
    void *packet = *(void **)(message + 4u);
    if (packet != 0) {
        WsfMsgFree(packet);
        *(void **)(message + 4u) = 0;
    }
}
