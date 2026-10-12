/* Native osSemaphoreGetCount 0x449a0e uses the same FreeRTOS queue count
 * operation as selected osMessageQueueGetCount 0x449bc8. */
#include <stdint.h>
extern uint32_t audio_cmsis_queue_get_count(void *); /* selected 0x449bc8 */
uint32_t audio_semaphore_get_count(void *semaphore) {
    return audio_cmsis_queue_get_count(semaphore);
}
