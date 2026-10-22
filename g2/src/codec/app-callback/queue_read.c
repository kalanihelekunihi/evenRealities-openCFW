/* Stock 0x10206fb0 read and 0x10206ffc empty, corroborated by pinned
 * NationalChip LvpQueueGet/IsEmpty. Preserve native re-load order and DIVS.
 */
#include <stdint.h>
struct queue_view { uint32_t tail, head; uint8_t *buffer; int32_t size, member_size; };
static uint32_t native_remainder(uint32_t sum, int32_t size)
{
    int32_t quotient;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(sum), "r"(size) : "cc");
    return sum - (uint32_t)quotient * (uint32_t)size;
}
/* Stock 0x10206FFC (LvpQueueIsEmpty) */
uint32_t g2_codec_queue_is_empty(void *storage)
{
    volatile struct queue_view *const queue = storage;
    const uint32_t head = queue->head;
    const uint32_t tail = queue->tail;
    return head == tail;
}
uint32_t g2_codec_queue_read(void *storage, void *destination)
{
    volatile struct queue_view *const queue = storage;
    const uint32_t head = queue->head;
    const uint32_t tail = queue->tail;
    if (head == tail) return 0;
    uint32_t offset = 0;
    volatile uint8_t *const output = destination;
    for (;;) {
        const int32_t member = queue->member_size;
        const uint32_t current_head = queue->head;
        const int32_t size = queue->size;
        if ((int32_t)offset >= member) {
            queue->head = native_remainder(current_head + (uint32_t)member, size);
            return 1;
        }
        const uint32_t index = native_remainder(current_head + offset, size);
        volatile uint8_t *const buffer = queue->buffer;
        output[offset] = buffer[index];
        offset++;
    }
}
