#include <stdint.h>

/* CMSIS osMessageQueueNew, native 0x449a32..0x449abd.
 * CMSIS attr->cb_mem is +8, cb_size +12, mq_mem +16, mq_size +20.
 * Static and dynamic FreeRTOS constructors are explicit lower calls. */
typedef struct {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
    void *mq_mem;
    uint32_t mq_size;
} audio_queue_attributes;

extern uint32_t audio_irq_context(void);
extern void *audio_queue_create_static(uint32_t count, uint32_t size,
                                       void *storage, void *control,
                                       uint32_t queue_type);
extern void *audio_queue_create_dynamic(uint32_t count, uint32_t size,
                                        uint32_t queue_type);

void *audio_queue_new(uint32_t count, uint32_t size,
                      const audio_queue_attributes *attr) {
    if (audio_irq_context() != 0u || count == 0u || size == 0u)
        return 0;
    uint32_t mode = 0u;
    if (attr != 0) {
        mode = UINT32_MAX;
        if (attr->cb_mem != 0 && attr->cb_size >= 80u &&
            attr->mq_mem != 0 && attr->mq_size >= count * size)
            mode = 1u;
        else if (attr->cb_mem == 0 && attr->cb_size == 0u &&
                 attr->mq_mem == 0 && attr->mq_size == 0u)
            mode = 0u;
    }
    if (mode == 1u)
        return audio_queue_create_static(count, size, attr->mq_mem,
                                         attr->cb_mem, 0u);
    if (mode == 0u)
        return audio_queue_create_dynamic(count, size, 0u);
    return 0;
}
