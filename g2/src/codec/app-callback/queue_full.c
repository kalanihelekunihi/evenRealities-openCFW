/* Native-checked LvpQueueIsFull at 0x10207008, corroborated by pinned
 * NationalChip lvp/common/lvp_queue.c. Keep the signed hardware division
 * instruction explicit: C division would have undefined exceptional operands.
 * This target-specific C unit uses one decoded instruction mnemonic, no blob.
 */
#include <stddef.h>
#include <stdint.h>
struct g2_codec_queue {
    int32_t tail;
    int32_t head;
    uint8_t *buffer;
    int32_t size;
    int32_t member_size;
};
_Static_assert(offsetof(struct g2_codec_queue, size) == 12, "queue size offset");
_Static_assert(offsetof(struct g2_codec_queue, member_size) == 16, "member offset");

/* Stock 0x10207008 (LvpQueueIsFull) */
uint32_t g2_codec_queue_is_full(void *storage)
{
    const volatile struct g2_codec_queue *const queue = storage;
    const uint32_t member = (uint32_t)queue->member_size;
    const uint32_t tail = (uint32_t)queue->tail;
    const int32_t size = queue->size;
    const uint32_t sum = tail + member;
    int32_t quotient;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(sum), "r"(size) : "cc");
    const uint32_t remainder = sum - (uint32_t)quotient * (uint32_t)size;
    return remainder == (uint32_t)queue->head;
}
