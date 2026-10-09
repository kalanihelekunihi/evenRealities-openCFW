#include <stdint.h>
int32_t xQueueSemaphoreTake(void *queue,uint32_t wait_ticks);
int32_t xQueueTakeMutexRecursive(void *,uint32_t);
int32_t xQueueGiveMutexRecursive(void *);
int32_t audio_mutex_acquire(uint32_t tagged_mutex,uint32_t wait_ticks);
int32_t audio_mutex_release(uint32_t tagged_mutex);
