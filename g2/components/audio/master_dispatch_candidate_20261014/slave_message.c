#include <stdint.h>

extern void *audio_wsf_buffer_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t, void *);
extern uint8_t audio_ble_smp_handler_state[];

/* Native WsfMsgAlloc 0x4bf99e, matched to the source-owned WSF allocator. */
void *audio_ble_message_alloc_4bf99e(uint32_t size)
{
    uint8_t *block = (uint8_t *)audio_wsf_buffer_alloc((uint16_t)((uint16_t)size + 8u));
    return block == 0 ? 0 : block + 8u;
}

/* Native 0x537bd6: SMP state byte +0xec holds the WSF message handler. */
void audio_ble_message_send_537bd6(void *message)
{
    audio_wsf_msg_send(audio_ble_smp_handler_state[0xecu], message);
}
