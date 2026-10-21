/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_EVENT_GROUP_H
#define OPENCFW_EVENT_GROUP_H
#include <stdint.h>
typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
typedef uint32_t EventBits_t;
typedef struct xLIST_ITEM ListItem_t;
typedef struct xLIST List_t;
struct xLIST_ITEM {uint32_t xItemValue;ListItem_t *pxNext,*pxPrevious;void *pvOwner;List_t *pxContainer;};
typedef struct {uint32_t xItemValue;ListItem_t *pxNext,*pxPrevious;} MiniListItem_t;
struct xLIST {uint32_t uxNumberOfItems;ListItem_t *pxIndex;MiniListItem_t xListEnd;};
typedef struct {uint32_t uxEventBits;List_t xTasksWaitingForBits;uint32_t uxEventGroupNumber;uint8_t ucStaticallyAllocated,padding[3];} EventGroup_t;
typedef EventGroup_t *EventGroupHandle_t;
typedef void (*PendedFunction_t)(void *,uint32_t);
/* Stock task-context setter uses scheduler suspension (not PRIMASK masking).
 * Valid initialized event-group and serialized scheduler/list providers required.
 * Bits restricted to low24; invalidhandle/highcontrolbyte triggers fatalassert.
 * Each matched waiter sees pre-clear accumulatedbits|0x02000000. Clear-on-exit
 * union applies after scanningallwaiters. Return is FINALBITS, not status.
 * ISR queues16-byte daemoncommand(-2,callback,group,bits); group must stayalive
 * through deferred execution. Queue provider must synchronously COPY packet. */
EventBits_t xEventGroupSetBits(EventGroupHandle_t,EventBits_t);
void vEventGroupSetBitsCallback(void *,uint32_t);
BaseType_t xEventGroupSetBitsFromISR(EventGroupHandle_t,EventBits_t,BaseType_t *);
BaseType_t xTimerPendFunctionCallFromISR(PendedFunction_t,void *,uint32_t,BaseType_t *);
/* Required production scheduler/queue boundaries; simulatorprovidersonly. */
void vTaskSuspendAll(void);
BaseType_t xTaskResumeAll(void);
void vTaskRemoveFromUnorderedEventList(ListItem_t *,EventBits_t);
BaseType_t opencfw_event_queue_send_isr(void *,const void *,BaseType_t *,BaseType_t);
void opencfw_event_group_assert_failure(void) __attribute__((noreturn));
#endif
