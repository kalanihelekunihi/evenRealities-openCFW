#include <stdint.h>
#include "../../../apollo-common/freertos-queue/queue.h"

/* FreeRTOS xQueueGenericCreate, native 0x441636..0x441695.
 * Its initializer at 0x441696 is included here from the pinned
 * FreeRTOS 10.5.1 queue source and native field offsets. */
extern void *pvPortMalloc(uint32_t bytes);
extern int32_t xQueueGenericReset(QueueHandle_t queue, int32_t fresh);
extern void offline_assert(void);

static void queue_create_invalid(void) {
    /* Decoded stock invalid branch: assert, invalid-address store,
     * terminal loop. This is a genuine fatal path, not success fallback. */
    offline_assert();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) {}
}

static void initialize_new_queue(uint32_t count, uint32_t size,
                                 uint8_t *storage, uint8_t type,
                                 Queue_t *queue) {
    queue->pcHead = size == 0u ? (int8_t *)queue : (int8_t *)storage;
    queue->uxLength = count;
    queue->uxItemSize = size;
    (void)xQueueGenericReset(queue, 1);
    queue->ucQueueType = type;
}

void *audio_queue_create_dynamic(uint32_t count, uint32_t size,
                                 uint32_t queue_type) {
    if (count == 0u || UINT32_MAX / count < size ||
        count * size > UINT32_MAX - 80u)
        queue_create_invalid();
    Queue_t *const queue = pvPortMalloc(80u + count * size);
    if (queue == 0)
        return 0;
    queue->ucStaticallyAllocated = 0u;
    initialize_new_queue(count, size, (uint8_t *)queue + 80u,
                         (uint8_t)queue_type, queue);
    return queue;
}
