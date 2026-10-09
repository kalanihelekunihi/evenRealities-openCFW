#include "../queue_cmsis_offline/compat.h"
#define configMAX_PRIORITIES 56
#define tskIDLE_PRIORITY 0
#define traceQUEUE_RECEIVE(q) ((void)0)
#define traceQUEUE_RECEIVE_FAILED(q) ((void)0)
#define traceBLOCKING_ON_QUEUE_RECEIVE(q) ((void)0)
#define listCURRENT_LIST_LENGTH(l) ((l)->uxNumberOfItems)
#define listGET_ITEM_VALUE_OF_HEAD_ENTRY(l) ((l)->xListEnd.pxNext->xItemValue)
extern void *pvTaskIncrementMutexHeldCount(void);
extern BaseType_t xTaskPriorityInherit(void *);
extern void vTaskPriorityDisinheritAfterTimeout(void *,uint32_t);

#define pdFAIL 0
#define queueMUTEX_GIVE_BLOCK_TIME 0
#define traceGIVE_MUTEX_RECURSIVE(q) ((void)0)
#define traceGIVE_MUTEX_RECURSIVE_FAILED(q) ((void)0)
#define traceTAKE_MUTEX_RECURSIVE(q) ((void)0)
#define traceTAKE_MUTEX_RECURSIVE_FAILED(q) ((void)0)
#define xTaskGetCurrentTaskHandle() (*(void* volatile*)0x20074a20u)
extern BaseType_t xQueueSemaphoreTake(QueueHandle_t,uint32_t);
