/* SPDX-License-Identifier: MIT */
#include "resume.h"
#include "../freertos_daemon/daemon.h"
#include "../freertos_ready/ready_compat.h"
#define TickType_t uint32_t
#define configUSE_PREEMPTION 1
#define taskENTER_CRITICAL() opencfw_daemon_critical_enter()
#define taskEXIT_CRITICAL() opencfw_daemon_critical_exit()
#define portSOFTWARE_BARRIER() __asm__ volatile("" ::: "memory")
#define portMEMORY_BARRIER() __asm__ volatile("" ::: "memory")
#define taskYIELD_IF_USING_PREEMPTION() opencfw_resume_yield_request()
#define xPendedTicks (*(volatile uint32_t *)(uintptr_t)0x20074a40u)
