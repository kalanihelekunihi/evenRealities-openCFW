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


void audio_ble_attc_free_pkt_531ac0(uint8_t *message)
{
    void *packet = *(void **)(message + 4u);
    if (packet != 0) {
        WsfMsgFree(packet);
        *(void **)(message + 4u) = 0;
    }
}
