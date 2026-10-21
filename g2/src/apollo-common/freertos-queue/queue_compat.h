/* SPDX-License-Identifier: MIT */
#include "queue.h"
#include <stddef.h>
_Static_assert(offsetof(Queue_t,xTasksWaitingToReceive)==0x24,"receive waiters");
_Static_assert(offsetof(Queue_t,uxMessagesWaiting)==0x38,"count");
_Static_assert(offsetof(Queue_t,uxLength)==0x3c,"capacity");
_Static_assert(offsetof(Queue_t,uxItemSize)==0x40,"item bytes");
_Static_assert(offsetof(Queue_t,cTxLock)==0x45,"deferred TX count");
_Static_assert(sizeof(Queue_t)==80,"stock configured ARM32 queue");
#define configUSE_QUEUE_SETS 0
#define configUSE_MUTEXES 1
#define pdFALSE 0
#define pdTRUE 1
#define pdPASS 1
#define errQUEUE_FULL 0
#define queueSEND_TO_BACK 0
#define queueOVERWRITE 2
#define queueUNLOCKED (-1)
#define queueINT8_MAX 127
#define uxQueueType pcHead
#define queueQUEUE_IS_MUTEX NULL
#define configASSERT(x) do {if(!(x))opencfw_event_group_assert_failure();}while(0)
#define portASSERT_IF_INTERRUPT_PRIORITY_INVALID() ((void)0)
#define portSET_INTERRUPT_MASK_FROM_ISR() opencfw_queue_mask_set()
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(x) opencfw_queue_mask_restore(x)
#define traceQUEUE_SEND_FROM_ISR(x) ((void)0)
#define traceQUEUE_SEND_FROM_ISR_FAILED(x) ((void)0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define listLIST_IS_EMPTY(l) ((l)->uxNumberOfItems==0)
#define memcpy opencfw_queue_memcpy
#define prvIncrementQueueTxLock(q,lock) do { \
 UBaseType_t n=uxTaskGetNumberOfTasks(); \
 if((UBaseType_t)(lock)<n){configASSERT((lock)!=queueINT8_MAX); \
 (q)->cTxLock=(int8_t)((lock)+1);} }while(0)
