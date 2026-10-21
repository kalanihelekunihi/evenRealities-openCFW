#include <stdint.h>

extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_ble_stack_copy16_542a44(void *, const void *);
extern void audio_wsf_msg_send(uint8_t, void *);
extern uint8_t audio_ble_dm_privacy_state[];

/* Native 0x52bb20: queue the 22-byte slave security request. */
void audio_ble_dm_sec_resolve_52bb20(uint32_t connection, uint32_t has_link,
                                     uint32_t selected, uint32_t link)
{
    uint8_t *msg = (uint8_t *)audio_wsf_msg_alloc(22u);
    if (msg == 0) return;
    msg[2] = 0x29u;
    msg[0] = (uint8_t)connection;
    msg[1] = 0u;
    msg[20] = (uint8_t)has_link;
    msg[21] = (uint8_t)selected;
    if ((uint8_t)has_link != 0u)
        audio_ble_stack_copy16_542a44(msg + 4u, (const void *)(uintptr_t)link);
    audio_wsf_msg_send(audio_ble_dm_privacy_state[0x0cu], msg);
}
