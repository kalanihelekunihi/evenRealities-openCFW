/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_RESUME_H
#define OPENCFW_RESUME_H
#include "../freertos_ready/ready.h"
void vTaskSuspendAll(void);
BaseType_t xTaskResumeAll(void);
void opencfw_resume_yield_request(void);
BaseType_t xTaskIncrementTick(void); /* external tick boundary */
#endif
