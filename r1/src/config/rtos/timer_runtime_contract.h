#ifndef R1_TIMER_RUNTIME_CONTRACT_H
#define R1_TIMER_RUNTIME_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "queue.h"
#include "list.h"
#include <stddef.h>
typedef struct tmrTimerControl Timer_t;
extern List_t xActiveTimerList1,xActiveTimerList2;
extern List_t *pxCurrentTimerList,*pxOverflowTimerList;
extern QueueHandle_t xTimerQueue;
static TickType_t prvGetNextExpireTime(BaseType_t *);
static TickType_t prvSampleTimeNow(BaseType_t *);
static void prvSwitchTimerLists(void);
static BaseType_t prvInsertTimerInActiveList(Timer_t *,TickType_t,TickType_t,TickType_t);
static void prvProcessExpiredTimer(TickType_t,TickType_t);
static void prvReloadTimer(Timer_t *,TickType_t,TickType_t);
static void prvProcessTimerOrBlockTask(TickType_t,BaseType_t);
static void prvProcessReceivedCommands(void);
_Static_assert(configUSE_TIMERS==1 && configUSE_DAEMON_TASK_STARTUP_HOOK==0 && configUSE_TRACE_FACILITY==1 && configSUPPORT_DYNAMIC_ALLOCATION==1 && INCLUDE_xTimerPendFunctionCall==1,"native timer runtime variant");
#endif
