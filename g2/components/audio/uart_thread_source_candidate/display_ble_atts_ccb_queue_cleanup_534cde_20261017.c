/* Cordio server CCB queue cleanup, stock 0x534cde..0x534d06. */
#include <stdint.h>

extern uint8_t audio_ble_atts_state[];
extern void *audio_ble_wsf_queue_dequeue(void *queue);
extern void WsfBufFree(void *buffer);

void audio_ble_atts_ccb_queue_cleanup_534cde(uint8_t *ccb)
{
    uint8_t *const queue = audio_ble_atts_state + 0x238u +
                           (uint32_t)ccb[0x24u] * 8u;
    void *message;
    while ((message = audio_ble_wsf_queue_dequeue(queue)) != 0)
        WsfBufFree(message);
}
