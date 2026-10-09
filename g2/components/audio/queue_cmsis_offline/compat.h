/* SPDX-License-Identifier: MIT */
#include "queue.h"
#include <stddef.h>
typedef uint32_t TickType_t;
typedef struct {uint32_t overflow,tick;} TimeOut_t;
#define pdFALSE 0
#define pdTRUE 1
#define pdPASS 1
#define errQUEUE_FULL 0
#define errQUEUE_EMPTY 0
#define queueSEND_TO_BACK 0
#define queueOVERWRITE 2
#define configUSE_QUEUE_SETS 0
#define configUSE_MUTEXES 1
#define INCLUDE_xTaskGetSchedulerState 1
#define configUSE_TIMERS 1
#define taskSCHEDULER_SUSPENDED 0
#define uxQueueType pcHead
#define queueQUEUE_IS_MUTEX NULL
#define configASSERT(x) do{if(!(x))audio_queue_bad_argument();}while(0)
#define taskENTER_CRITICAL() stock_enter_critical()
#define taskEXIT_CRITICAL() stock_exit_critical()
#define xTaskGetSchedulerState() audio_scheduler_state()
#define xTaskRemoveFromEventList(l) opencfw_ready_remove_event_list(l)
#define memcpy audio_queue_copy_bytes
#define xTaskPriorityDisinherit stock_priority_disinherit
#define vTaskInternalSetTimeOutState stock_timeout_capture
#define xTaskCheckForTimeOut stock_timeout_check
#define vTaskSuspendAll stock_scheduler_suspend
#define xTaskResumeAll stock_scheduler_resume
#define vTaskPlaceOnEventList stock_place_event
#define prvUnlockQueue(q) audio_public_queue_unlock(q)
#define portYIELD_WITHIN_API() stock_port_yield()
#define queueYIELD_IF_USING_PREEMPTION() stock_port_yield()
#define traceQUEUE_SEND(q) ((void)0)
#define traceQUEUE_SEND_FAILED(q) ((void)0)
#define traceQUEUE_RECEIVE(q) ((void)0)
#define traceQUEUE_RECEIVE_FAILED(q) ((void)0)
#define traceBLOCKING_ON_QUEUE_SEND(q) ((void)0)
#define traceBLOCKING_ON_QUEUE_RECEIVE(q) ((void)0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define listLIST_IS_EMPTY(l) ((l)->uxNumberOfItems==0)
extern void audio_queue_bad_argument(void) __attribute__((noreturn));
extern void stock_timeout_capture(TimeOut_t *),stock_scheduler_suspend(void),stock_port_yield(void);
extern BaseType_t stock_timeout_check(TimeOut_t *,TickType_t *),stock_scheduler_resume(void),stock_priority_disinherit(void *);
extern void stock_place_event(List_t *,TickType_t);
static void prvLockQueue(Queue_t *q){stock_enter_critical();if(q->cRxLock==-1)q->cRxLock=0;if(q->cTxLock==-1)q->cTxLock=0;stock_exit_critical();}
static BaseType_t prvIsQueueFull(Queue_t *q){stock_enter_critical();BaseType_t result=q->uxMessagesWaiting==q->uxLength;stock_exit_critical();return result;}
static BaseType_t prvIsQueueEmpty(Queue_t *q){stock_enter_critical();BaseType_t result=q->uxMessagesWaiting==0;stock_exit_critical();return result;}
