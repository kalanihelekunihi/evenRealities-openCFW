#ifndef R1_TIMER_API_CONTRACT_H
#define R1_TIMER_API_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"
#include "queue.h"
#include "list.h"
#include <stddef.h>
typedef struct tmrTimerControl Timer_t;
extern QueueHandle_t xTimerQueue;
void r1_native_timer_infrastructure(void);
#define prvCheckForValidListAndQueue r1_native_timer_infrastructure
static void prvInitialiseNewTimer(const char *,TickType_t,BaseType_t,void *,TimerCallbackFunction_t,Timer_t *);
#endif
