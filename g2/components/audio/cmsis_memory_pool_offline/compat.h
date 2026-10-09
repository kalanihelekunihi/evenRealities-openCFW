#include "pool.h"
#include "../queue_cmsis_offline/compat.h"
#include <stddef.h>
_Static_assert(sizeof(MemPool_t)==116 && offsetof(MemPool_t,status)==32 && offsetof(MemPool_t,n)==28 && offsetof(MemPool_t,mem_sem)==36,"stock pool ABI");
typedef void *osMemoryPoolId_t;
typedef int32_t osStatus_t;
#define osOK 0
#define osErrorResource (-3)
#define osErrorParameter (-4)
#define MPOOL_STATUS 0x5eed0000u
#define IRQ_Context audio_cmsis_irq_context
extern BaseType_t xQueueSemaphoreTake(QueueHandle_t,uint32_t);
extern BaseType_t xQueueReceiveFromISR(QueueHandle_t,void *,BaseType_t *);
extern BaseType_t xQueueGiveFromISR(QueueHandle_t,BaseType_t *);
extern UBaseType_t uxQueueMessagesWaiting(QueueHandle_t);
extern UBaseType_t uxQueueMessagesWaitingFromISR(QueueHandle_t);
extern uint32_t opencfw_queue_mask_set(void);
extern void opencfw_queue_mask_restore(uint32_t);
#define xSemaphoreTake(q,t) xQueueSemaphoreTake(q,t)
#define xSemaphoreTakeFromISR(q,w) xQueueReceiveFromISR(q,0,w)
#define xSemaphoreGive(q) xQueueGenericSend(q,0,0,0)
#define xSemaphoreGiveFromISR(q,w) xQueueGiveFromISR(q,w)
#define uxSemaphoreGetCount uxQueueMessagesWaiting
#define uxSemaphoreGetCountFromISR uxQueueMessagesWaitingFromISR
#define taskENTER_CRITICAL_FROM_ISR() opencfw_queue_mask_set()
#define taskEXIT_CRITICAL_FROM_ISR(s) opencfw_queue_mask_restore(s)
#define portYIELD_FROM_ISR(w) do{if(w)*(volatile uint32_t*)0xe000ed04u=0x10000000;}while(0)

#define configSUPPORT_STATIC_ALLOCATION 1
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configASSERT_DEFINED 1
#define configUSE_TRACE_FACILITY 1
#define queueUNLOCKED (-1)
#define queueSEMAPHORE_QUEUE_ITEM_LENGTH 0
#define queueQUEUE_TYPE_COUNTING_SEMAPHORE 2
#define pdFAIL 0
#define traceQUEUE_CREATE(q) ((void)0)
#define traceCREATE_COUNTING_SEMAPHORE() ((void)0)
#define traceCREATE_COUNTING_SEMAPHORE_FAILED() ((void)0)
#define MEMPOOL_ARR_SIZE(c,s) ((uint32_t)(c)*(((uint32_t)(s)+3u)>>2)*4u)
typedef Queue_t StaticQueue_t;
extern void vListInitialise(List_t *);
extern BaseType_t xQueueGenericReset(QueueHandle_t,BaseType_t);
extern QueueHandle_t xQueueGenericCreateStatic(uint32_t,uint32_t,uint8_t *,StaticQueue_t *,uint8_t);
extern QueueHandle_t xQueueCreateCountingSemaphoreStatic(uint32_t,uint32_t,StaticQueue_t *);
#define xSemaphoreCreateCountingStatic xQueueCreateCountingSemaphoreStatic
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
