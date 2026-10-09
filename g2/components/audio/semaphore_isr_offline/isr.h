#include <stdint.h>
int32_t xQueueReceiveFromISR(void *,void *,int32_t *);
int32_t xQueueGiveFromISR(void *,int32_t *);
int32_t audio_semaphore_acquire(void *,uint32_t);
int32_t audio_semaphore_release(void *);
