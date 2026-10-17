/* Cordio ATT response leaf handlers at stock Main 0x4b53da..0x4b53e2. */
#include <stdint.h>

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_attc_leaf_event_t;

void audio_attc_rsp_read_4b53da(uint8_t *ccb, uint16_t length,
                                const uint8_t *packet,
                                audio_attc_leaf_event_t *event)
{
    (void)ccb;
    (void)length;
    (void)packet;
    (void)event;
}

void audio_attc_rsp_write_4b53dc(uint8_t *ccb, uint16_t length,
                                 const uint8_t *packet,
                                 audio_attc_leaf_event_t *event)
{
    (void)ccb;
    (void)length;
    (void)packet;
    event->value_length = 0u;
}

void audio_attc_rsp_read_multi_var_4b53e2(uint8_t *ccb, uint16_t length,
                                          const uint8_t *packet,
                                          audio_attc_leaf_event_t *event)
{
    (void)ccb;
    (void)length;
    (void)packet;
    (void)event;
}
