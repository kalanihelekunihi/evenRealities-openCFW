/* SPDX-License-Identifier: MIT */
#include "event_group.h"
#include "../wsf_radio/wsf_radio.h"
int32_t opencfw_wsf_notify_task(uint32_t group,uint32_t bits)
{return (int32_t)xEventGroupSetBits((EventGroupHandle_t)(uintptr_t)group,bits);}
int32_t opencfw_wsf_notify_isr(uint32_t group,uint32_t bits,int32_t *higher)
{return xEventGroupSetBitsFromISR((EventGroupHandle_t)(uintptr_t)group,bits,higher);}
