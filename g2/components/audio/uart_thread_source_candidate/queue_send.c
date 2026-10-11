/* Native 0x4417ee is FreeRTOS xQueueGenericSend. The selected full pinned
 * FreeRTOS C body exports xQueueGenericSend; this caller ABI name is a
 * source-level bridge to that same queue implementation. */
#include <stdint.h>
extern int32_t xQueueGenericSend(void *queue, const void *item,
                                 uint32_t ticks, int32_t position);

int32_t audio_uart_queue_send(void *queue, const void *item,
                              uint32_t ticks, uint32_t position) {
    return xQueueGenericSend(queue, item, ticks, (int32_t)position);
}
