/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TICK_H
#define OPENCFW_TICK_H
#include "../freertos_resume/resume.h"
/* Call with the kernel's exclusion precondition; no masking is added here. */
BaseType_t xTaskIncrementTick(void);
#endif
