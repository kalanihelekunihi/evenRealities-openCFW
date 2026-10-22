/* SPDX-License-Identifier: MIT
 * Resident 0x100261b8 LvpQueuePut in authenticated image-A SRAM.
 * Queue fields and signed DIVS follow the retained NationalChip queue body.
 */
#include <stdint.h>
#include <stddef.h>

struct resident_queue_view {
    uint32_t tail;
    uint32_t head;
    uint8_t *buffer;
    int32_t size;
    int32_t member_size;
};
_Static_assert(offsetof(struct resident_queue_view, size) == 12, "queue size offset");
_Static_assert(offsetof(struct resident_queue_view, member_size) == 16, "queue member offset");

static uint32_t resident_remainder(uint32_t sum, int32_t size)
{
    int32_t quotient;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(sum), "r"(size) : "cc");
    return sum - (uint32_t)quotient * (uint32_t)size;
}

/* Stock 0x100261B8 (LvpQueuePut) */
uint32_t g2_codec_queue_enqueue(void *storage, const void *source)
{
    volatile struct resident_queue_view *const queue = storage;
    const uint32_t member = (uint32_t)queue->member_size;
    const uint32_t tail = queue->tail;
    const int32_t size = queue->size;
    if (resident_remainder(tail + member, size) == queue->head) return 0;

    const volatile uint8_t *const input = source;
    uint32_t offset = 0;
    for (;;) {
        const int32_t current_member = queue->member_size;
        const uint32_t current_tail = queue->tail;
        const int32_t current_size = queue->size;
        if ((int32_t)offset >= current_member) {
            queue->tail = resident_remainder(current_tail + (uint32_t)current_member,
                                             current_size);
            return 1;
        }
        const uint32_t index = resident_remainder(current_tail + offset,
                                                   current_size);
        volatile uint8_t *const buffer = queue->buffer;
        buffer[index] = input[offset];
        offset++;
    }
}
