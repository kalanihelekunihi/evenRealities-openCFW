/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Apollo-main scheduler-port source interface.  The production overlay
 * compiles its three entry points as isolated, relocated source leaves.
 */

#ifndef OPEN_CFW_FREERTOS_SCHEDULER_PORT_TRIO_H
#define OPEN_CFW_FREERTOS_SCHEDULER_PORT_TRIO_H

typedef __UINT32_TYPE__ open_cfw_freertos_port_u32;

#define OPEN_CFW_FREERTOS_PORT_ICSR_ADDRESS 0xE000ED04U
#define OPEN_CFW_FREERTOS_PORT_PENDSVSET_BIT 0x10000000U
#define OPEN_CFW_FREERTOS_PORT_CRITICAL_NESTING_ADDRESS 0x2000309CU
#define OPEN_CFW_FREERTOS_PORT_MAX_SYSCALL_PRIORITY 0x30U

void open_cfw_freertos_port_yield(void);
void open_cfw_freertos_port_enter_critical(void);
void open_cfw_freertos_port_exit_critical(void);

#endif
