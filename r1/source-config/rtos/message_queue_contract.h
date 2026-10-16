#ifndef R1_MESSAGE_QUEUE_CONTRACT_H
#define R1_MESSAGE_QUEUE_CONTRACT_H
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "cmsis_os2.h"
#include <stddef.h>
#undef configQUEUE_REGISTRY_SIZE
#define configQUEUE_REGISTRY_SIZE 0
_Static_assert(sizeof(StaticQueue_t)==80 && offsetof(StaticQueue_t,uxDummy4)==56,"native CMSIS queue query layout");
_Static_assert(sizeof(osMessageQueueAttr_t)==24 && offsetof(osMessageQueueAttr_t,cb_mem)==8 && offsetof(osMessageQueueAttr_t,mq_mem)==16,"native CMSIS queue attributes");
#endif
