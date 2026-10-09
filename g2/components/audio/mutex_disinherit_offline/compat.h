#include "../../foundation/freertos_ready/ready.h"
#include <stddef.h>
typedef uint32_t TickType_t;
/* Only accessed offsets; no claim of a complete TCB allocation. */
typedef struct {void*stack;ListItem_t state,event;uint32_t priority;uint8_t unused[48];uint32_t base,held;} MutexTCB;
_Static_assert(offsetof(MutexTCB,base)==96 && offsetof(MutexTCB,held)==100,"stock ABI");
#define TCB_t MutexTCB
#define TaskHandle_t void*
#define uxMutexesHeld held
#define uxBasePriority base
#define uxPriority priority
#define xStateListItem state
#define xEventListItem event
#define pdFALSE 0
#define pdTRUE 1
#define pxCurrentTCB (*(MutexTCB* volatile*)0x20074a20u)
#define uxTopReadyPriority (*(volatile uint32_t*)0x20074a38u)
#define pxReadyTasksLists ((List_t*)0x2006a49cu)
#define configMAX_PRIORITIES 56
extern void mutex_assert_boundary(void);
#define configASSERT(x) do{if(!(x))mutex_assert_boundary();}while(0)
#define portRESET_READY_PRIORITY(p,t) ((void)0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define traceTASK_PRIORITY_DISINHERIT(t,p) ((void)0)
#define listSET_LIST_ITEM_VALUE(i,v) ((i)->xItemValue=(v))
#define prvAddTaskToReadyList(t) do{if((t)->priority>uxTopReadyPriority)uxTopReadyPriority=(t)->priority;vListInsertEnd(&pxReadyTasksLists[(t)->priority],&(t)->state);}while(0)

#define taskEVENT_LIST_ITEM_VALUE_IN_USE 0x80000000u
#define listGET_LIST_ITEM_VALUE(i) ((i)->xItemValue)
#define listIS_CONTAINED_WITHIN(l,i) ((i)->pxContainer==(l))

#define traceTASK_PRIORITY_INHERIT(t,p) ((void)0)
