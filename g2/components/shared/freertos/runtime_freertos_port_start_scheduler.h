/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded bounded Apollo scheduler-port start adaptation.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_PORT_START_SCHEDULER_H
#define OPEN_CFW_RUNTIME_FREERTOS_PORT_START_SCHEDULER_H

typedef unsigned int open_cfw_freertos_port_start_u32;
typedef int open_cfw_freertos_port_start_base_type;

extern volatile open_cfw_freertos_port_start_u32
    open_cfw_retained_freertos_system_handler_priority;
extern volatile open_cfw_freertos_port_start_u32
    open_cfw_retained_freertos_critical_nesting;

open_cfw_freertos_port_start_base_type
open_cfw_freertos_port_start_scheduler(void);

#endif
