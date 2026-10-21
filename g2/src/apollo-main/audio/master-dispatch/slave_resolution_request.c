#include <stdint.h>

extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_ble_stack_copy16_542a44(void *, const void *);
extern void audio_ble_copy_address6_4d293c(void *, const void *);
extern void audio_wsf_msg_send(uint8_t, void *);
extern uint8_t audio_ble_dm_privacy_state[];

/* Native 0x4d27f6: queue a 26-byte address-resolution request. */
void audio_ble_slave_resolution_request_4d27f6(uint32_t identity,
                                                uint32_t link,
                                                uint32_t connection)
{
    uint8_t *msg = (uint8_t *)audio_wsf_msg_alloc(26u);
    if (msg == 0) return;
    msg[2] = 0x30u;
    msg[0] = (uint8_t)connection;
    msg[1] = (uint8_t)(connection >> 8u);
    audio_ble_stack_copy16_542a44(msg + 4u, (const void *)(uintptr_t)link);
    audio_ble_copy_address6_4d293c(msg + 20u, (const void *)(uintptr_t)identity);
    audio_wsf_msg_send(audio_ble_dm_privacy_state[0x0cu], msg);
}
