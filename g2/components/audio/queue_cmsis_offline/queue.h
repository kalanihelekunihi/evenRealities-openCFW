/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_QUEUE_CMSIS_OFFLINE_H
#define OPENCFW_QUEUE_CMSIS_OFFLINE_H
#include "../../foundation/freertos_queue/queue.h"
#include "../timer_wake_providers_offline/unlock.h"
BaseType_t xQueueGenericSend(QueueHandle_t,const void *,uint32_t,BaseType_t);
BaseType_t xQueueReceive(QueueHandle_t,void *,uint32_t);
uint32_t audio_scheduler_state(void);
uint32_t audio_cmsis_irq_context(void);
int32_t audio_cmsis_queue_put(void *,const void *,uint8_t,uint32_t);
void *audio_queue_copy_bytes(void *,const void *,uint32_t);
#endif
