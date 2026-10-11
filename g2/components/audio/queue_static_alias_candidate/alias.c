#include <stdint.h>

/* Native 0x4415ca is selected FreeRTOS xQueueGenericCreateStatic.
 * The CMSIS constructor child name uses its exact five-argument ABI. */
extern void *xQueueGenericCreateStatic(uint32_t count, uint32_t size,
                                       uint8_t *storage, void *control,
                                       uint8_t queue_type);

void *audio_queue_create_static(uint32_t count, uint32_t size,
                                void *storage, void *control,
                                uint32_t queue_type) {
    return xQueueGenericCreateStatic(count, size, storage, control,
                                     (uint8_t)queue_type);
}
