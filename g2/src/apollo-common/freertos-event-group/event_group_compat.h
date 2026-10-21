/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_EVENT_GROUP_COMPAT_H
#define OPENCFW_EVENT_GROUP_COMPAT_H
#include "event_group.h"
#include <stddef.h>
_Static_assert(sizeof(void *)==4,"stock ARM32 pointers");
_Static_assert(sizeof(ListItem_t)==20 && sizeof(List_t)==20,"stock waiter list");
_Static_assert(sizeof(EventGroup_t)==32,"stock EventGroup32B");
_Static_assert(offsetof(EventGroup_t,xTasksWaitingForBits)==4,"stock waitlist");
#define eventCLEAR_EVENTS_ON_EXIT_BIT 0x01000000u
#define eventUNBLOCKED_DUE_TO_BIT_SET 0x02000000u
#define eventWAIT_FOR_ALL_BITS 0x04000000u
#define eventEVENT_BITS_CONTROL_BYTES 0xff000000u
#define pdFALSE 0
#define pdTRUE 1
#define configASSERT(x) do{if(!(x))opencfw_event_group_assert_failure();}while(0)
#define traceEVENT_GROUP_SET_BITS(a,b) ((void)0)
#define traceEVENT_GROUP_SET_BITS_FROM_ISR(a,b) ((void)0)
#define tracePEND_FUNC_CALL_FROM_ISR(a,b,c,d) ((void)0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define listGET_END_MARKER(l) ((ListItem_t *)&((l)->xListEnd))
#define listGET_HEAD_ENTRY(l) ((l)->xListEnd.pxNext)
#define listGET_NEXT(i) ((i)->pxNext)
#define listGET_LIST_ITEM_VALUE(i) ((i)->xItemValue)
#define tmrCOMMAND_EXECUTE_CALLBACK_FROM_ISR (-2)
typedef struct {PendedFunction_t pxCallbackFunction;void *pvParameter1;uint32_t ulParameter2;} CallbackParameters_t;
typedef struct {BaseType_t xMessageID;union{CallbackParameters_t xCallbackParameters;}u;} DaemonTaskMessage_t;
_Static_assert(sizeof(DaemonTaskMessage_t)==16,"stock daemon copy16B");
#define xTimerQueue (*(void **)(uintptr_t)0x20074ab0u)
#define xQueueSendFromISR(q,m,w) opencfw_event_queue_send_isr((q),(m),(w),0)
#endif
