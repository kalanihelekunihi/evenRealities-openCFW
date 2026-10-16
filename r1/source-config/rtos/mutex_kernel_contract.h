#ifndef R1_MUTEX_KERNEL_CONTRACT_H
#define R1_MUTEX_KERNEL_CONTRACT_H
#include "timer_isr_queue_contract.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include "list.h"
#include <stddef.h>
typedef struct QueueDefinition Queue_t;
static void prvInitialiseMutex(Queue_t *);
static void prvUnlockQueue(Queue_t * const);
static BaseType_t prvIsQueueEmpty(const Queue_t *);
static UBaseType_t prvGetDisinheritPriorityAfterTimeout(const Queue_t * const);
#endif
