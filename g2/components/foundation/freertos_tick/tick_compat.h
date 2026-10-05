/* SPDX-License-Identifier: MIT */
#include "tick.h"
#include "../freertos_resume/resume_compat.h"
#define configUSE_TIME_SLICING 1
#define configUSE_TICK_HOOK 0
#define traceTASK_INCREMENT_TICK(t) ((void)0)
#define xTickCount (*(volatile uint32_t *)(uintptr_t)0x20074a34u)
#define pxOverflowDelayedTaskList (*(List_t * volatile *)(uintptr_t)0x20074a28u)
#define xNumOfOverflows (*(volatile BaseType_t *)(uintptr_t)0x20074a48u)
#define listGET_LIST_ITEM_VALUE(i) ((i)->xItemValue)
#define listLIST_ITEM_CONTAINER(i) ((i)->pxContainer)
#define listCURRENT_LIST_LENGTH(l) ((l)->uxNumberOfItems)
#define taskSWITCH_DELAYED_LISTS() do { \
    List_t *temp; \
    configASSERT(listLIST_IS_EMPTY(pxDelayedTaskList)); \
    temp=pxDelayedTaskList; \
    pxDelayedTaskList=pxOverflowDelayedTaskList; \
    pxOverflowDelayedTaskList=temp; \
    ++xNumOfOverflows; \
    prvResetNextTaskUnblockTime(); \
} while(0)
