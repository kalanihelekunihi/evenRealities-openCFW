/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_WSF_TIMER_COMPAT_H
#define OPENCFW_WSF_TIMER_COMPAT_H
#include "wsf_timer_stop.h"
#include "../wsf_radio/wsf_radio.h"
#include "../ambiq_gpio_config/gpio_interrupt_control.h"
#include <stddef.h>
#define FALSE 0u
#define WSF_TRACE_INFO1(...)
#define WSF_ASSERT(condition) ((void)0)
#define WSF_CS_INIT(name)
#define WSF_CS_ENTER(name) opencfw_wsf_cs_enter()
#define WSF_CS_EXIT(name) opencfw_wsf_cs_exit()
#define WSF_QUEUE_NEXT(element) (*(void **)(element))
#define wsfTimerTimerQueue (*(wsfQueue_t *)(uintptr_t)0x200741b0u)
_Static_assert(sizeof(void *)==4,"stock pointer ABI");
_Static_assert(sizeof(wsfTimer_t)==16,"stock cancellation view");
_Static_assert(offsetof(wsfTimer_t,isStarted)==13,"stock active flag");
_Static_assert(sizeof(wsfQueue_t)==8,"stock head/tail pair");
#endif
