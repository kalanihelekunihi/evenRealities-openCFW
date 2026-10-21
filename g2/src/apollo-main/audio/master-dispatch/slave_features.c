#include <stdint.h>

extern void *audio_ble_message_alloc_4bf99e(uint32_t);
extern void audio_ble_message_send_537bd6(void *);

/* Native 0x52bacc: construct the eight-byte slave feature message. */
void audio_ble_slave_set_features_52bacc(uint32_t connection, uint32_t event,
                                         uint32_t policy, uint32_t flags,
                                         uint32_t supported)
{
    uint8_t *msg = (uint8_t *)audio_ble_message_alloc_4bf99e(8u);
    if (msg == 0) return;
    msg[2] = 2u;
    msg[0] = (uint8_t)connection;
    msg[1] = 0u;
    msg[4] = (uint8_t)event;
    msg[5] = (uint8_t)policy;
    msg[6] = (uint8_t)(flags & 7u);
    msg[7] = (uint8_t)(supported & 7u);
    audio_ble_message_send_537bd6(msg);
}
