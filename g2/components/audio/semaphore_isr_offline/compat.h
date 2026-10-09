#include "../../foundation/freertos_queue/queue_compat.h"
#define pdFAIL 0
#define errQUEUE_EMPTY 0
#define traceQUEUE_RECEIVE_FROM_ISR(q) ((void)0)
#define traceQUEUE_RECEIVE_FROM_ISR_FAILED(q) ((void)0)
#define prvIncrementQueueRxLock(q,lock) do {uint32_t n=uxTaskGetNumberOfTasks();if((uint32_t)(lock)<n){configASSERT((lock)!=127);(q)->cRxLock=(int8_t)((lock)+1);}}while(0)
extern uint32_t audio_cmsis_irq_context(void);
extern BaseType_t xQueueSemaphoreTake(QueueHandle_t,uint32_t);
extern BaseType_t xQueueGenericSend(QueueHandle_t,const void*,uint32_t,BaseType_t);
