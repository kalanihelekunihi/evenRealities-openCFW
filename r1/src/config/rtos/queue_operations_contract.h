#ifndef R1_QUEUE_OPERATIONS_CONTRACT_H
#define R1_QUEUE_OPERATIONS_CONTRACT_H
/* Native vQueueDelete has no registry-unregister route. Scoped to admitted
 * send/delete provider; baseline queue creation and kernel config stay separate. */
#include "FreeRTOS.h"
#undef configQUEUE_REGISTRY_SIZE
#define configQUEUE_REGISTRY_SIZE 0
#include <string.h>
/* Native copy helper calls0x2775c, whose overlap-safe movement and observed
 * non-ISO return ABI already have a C provider. The result is unused here. */
void *r1_native_memory_move(void *,const void *,size_t);
#define memcpy r1_native_memory_move
#endif
