/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_QUEUE_H
#define OPENCFW_QUEUE_H
#include "../freertos_event_group/event_group.h"
typedef struct {
    int8_t *pcHead,*pcWriteTo;
    union {struct {int8_t *pcTail,*pcReadFrom;} xQueue;
           struct {void *xMutexHolder;UBaseType_t uxRecursiveCallCount;} xSemaphore;} u;
    List_t xTasksWaitingToSend,xTasksWaitingToReceive;
    volatile UBaseType_t uxMessagesWaiting;
    UBaseType_t uxLength,uxItemSize;
    volatile int8_t cRxLock,cTxLock;
    uint8_t ucStaticallyAllocated,pad;
    UBaseType_t uxQueueNumber;
    uint8_t ucQueueType,padding[3];
} Queue_t;
typedef Queue_t *QueueHandle_t;
BaseType_t xQueueGenericSendFromISR(QueueHandle_t,const void *,BaseType_t *,BaseType_t);
/* Scheduler boundaries, not implemented by this producer module. */
BaseType_t xTaskRemoveFromEventList(List_t *);
BaseType_t xTaskPriorityDisinherit(void *);
UBaseType_t uxTaskGetNumberOfTasks(void);
uint32_t opencfw_queue_mask_set(void);
void opencfw_queue_mask_restore(uint32_t);
void *opencfw_queue_memcpy(void *,const void *,uint32_t);
#endif
