/* Cordio attcProcPrepWriteRsp at stock Main 0x539dcc. */
#include <stdint.h>

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_attc_prep_event_t;

void audio_attc_rsp_prepare_write_539dcc(uint8_t *ccb, uint16_t length,
                                         const uint8_t *packet,
                                         audio_attc_prep_event_t *event)
{
    (void)length;
    (void)packet;
    if (ccb[7u] == 1u && ccb[0x10u] == 0u && ccb[0x11u] == 0u)
        ccb[7u] = 0u;
    event->value += 4u;
    event->value_length = (uint16_t)(event->value_length - 4u);
}
