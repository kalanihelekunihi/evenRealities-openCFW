/* SPDX-License-Identifier: MIT */
#include "ready.h"
#include <stddef.h>
_Static_assert(offsetof(TCB_t,xStateListItem)==4,"state item");
_Static_assert(offsetof(TCB_t,xEventListItem)==24,"event item");
_Static_assert(offsetof(TCB_t,uxPriority)==44,"priority");
_Static_assert(sizeof(List_t)==20 && sizeof(ListItem_t)==20,"list ABI");
#define pdFALSE 0
#define pdTRUE 1
#define configUSE_TICKLESS_IDLE 1
#define portMAX_DELAY 0xffffffffu
#define configASSERT(x) do{if(!(x))opencfw_event_group_assert_failure();}while(0)
#define mtCOVERAGE_TEST_DELAY() ((void)0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define listTEST_LIST_INTEGRITY(x) ((void)0)
#define listTEST_LIST_ITEM_INTEGRITY(x) ((void)0)
#define listGET_OWNER_OF_HEAD_ENTRY(l) ((l)->xListEnd.pxNext->pvOwner)
#define listGET_ITEM_VALUE_OF_HEAD_ENTRY(l) ((l)->xListEnd.pxNext->xItemValue)
#define listLIST_IS_EMPTY(l) ((l)->uxNumberOfItems==0)
#define listREMOVE_ITEM(i) ((void)uxListRemove(i))
#define listINSERT_END(l,i) vListInsertEnd((l),(i))
#define traceMOVED_TASK_TO_READY_STATE(t) ((void)0)
#define tracePOST_MOVED_TASK_TO_READY_STATE(t) ((void)0)
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)0x20074a58u)
#define uxTopReadyPriority (*(volatile UBaseType_t *)(uintptr_t)0x20074a38u)
#define pxReadyTasksLists ((List_t *)(uintptr_t)0x2006a49cu)
#define xPendingReadyList (*(List_t *)(uintptr_t)0x20073d24u)
#define pxCurrentTCB (*(TCB_t * volatile *)(uintptr_t)0x20074a20u)
#define pxDelayedTaskList (*(List_t * volatile *)(uintptr_t)0x20074a24u)
#define xNextTaskUnblockTime (*(volatile uint32_t *)(uintptr_t)0x20074a50u)
#define xYieldPending (*(volatile BaseType_t *)(uintptr_t)0x20074a44u)
#define uxCurrentNumberOfTasks (*(volatile UBaseType_t *)(uintptr_t)0x20074a30u)
#define taskRECORD_READY_PRIORITY(p) do{if((p)>uxTopReadyPriority)uxTopReadyPriority=(p);}while(0)
#define prvAddTaskToReadyList(t) do{taskRECORD_READY_PRIORITY((t)->uxPriority); \
 listINSERT_END(&pxReadyTasksLists[(t)->uxPriority],&(t)->xStateListItem);}while(0)
#define xTaskRemoveFromEventList opencfw_ready_remove_event_list
