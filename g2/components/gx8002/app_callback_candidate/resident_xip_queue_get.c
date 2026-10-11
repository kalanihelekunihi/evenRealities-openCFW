/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x10206fb0 LvpQueueGet. Companion to source-owned resident
 * LvpQueuePut: same five-word queue view and signed DIVS modulo.
 */
#include <stdint.h>
#include <stddef.h>

struct gx8002_xip_queue_view {
    uint32_t tail;
    uint32_t head;
    uint8_t *buffer;
    int32_t size;
    int32_t member_size;
};
_Static_assert(offsetof(struct gx8002_xip_queue_view, member_size) == 16,
               "native queue member offset");

static uint32_t signed_remainder(uint32_t sum, int32_t divisor)
{
    int32_t quotient;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(sum), "r"(divisor) : "cc");
    return sum - (uint32_t)quotient * (uint32_t)divisor;
}

int32_t gx8002_xip_tws_dequeue_10206fb0(
    volatile void *storage, uint32_t *output)
{
    volatile struct gx8002_xip_queue_view *const queue = storage;
    if (queue->head == queue->tail) return 0;
    uint8_t *const out = (uint8_t *)output;
    uint32_t offset = 0u;
    for (;;) {
        int32_t member = queue->member_size;
        if ((int32_t)offset >= member) break;
        uint32_t index = signed_remainder(queue->head + offset, queue->size);
        out[offset] = queue->buffer[index];
        ++offset;
    }
    queue->head = signed_remainder(queue->head +
        (uint32_t)queue->member_size, queue->size);
    return 1;
}
