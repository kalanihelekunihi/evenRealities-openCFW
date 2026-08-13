/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CMBACKTRACE_PC_TASK_GET_NAME_CURRENT_H
#define OPEN_CFW_RUNTIME_CMBACKTRACE_PC_TASK_GET_NAME_CURRENT_H

/* Return current TCB + 0x34, preserving the stock null-TCB result of 0x34. */
const char *open_cfw_cmbacktrace_pc_task_get_name_current(void);

#endif
