#ifndef R1_STARTUP_TIMER_CONTRACT_H
#define R1_STARTUP_TIMER_CONTRACT_H
#include "FreeRTOS.h"
#include "../../components/board/native_task_construction.h"
#define StaticTask_t r1_native_tcb
#include "task.h"
#include "timers.h"
#include "queue.h"
#include "list.h"
#define xTaskCreateStatic r1_native_task_create_static
#undef configTIMER_TASK_PRIORITY
#define configTIMER_TASK_PRIORITY 53
#undef configQUEUE_REGISTRY_SIZE
#define configQUEUE_REGISTRY_SIZE 0
#define configTIMER_SERVICE_TASK_NAME "Tmr Svc"
#define prvTimerTask r1_native_timer_task
void r1_native_timer_task(void *);
/* Timer messages use only a pointer to Timer_t in these selected bodies. */
typedef struct tmrTimerControl Timer_t;
List_t xActiveTimerList1,xActiveTimerList2;
List_t *pxCurrentTimerList,*pxOverflowTimerList;
QueueHandle_t xTimerQueue;
TaskHandle_t xTimerTaskHandle;
_Static_assert(sizeof(StaticTask_t)==112 && sizeof(StaticQueue_t)==80 && configTIMER_QUEUE_LENGTH==32 && configTIMER_TASK_STACK_DEPTH==256 && INCLUDE_xTimerPendFunctionCall==1,"native timer startup ABI");
#endif
