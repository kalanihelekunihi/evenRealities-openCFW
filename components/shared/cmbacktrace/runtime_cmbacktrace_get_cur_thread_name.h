/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CMBACKTRACE_GET_CUR_THREAD_NAME_H
#define OPEN_CFW_RUNTIME_CMBACKTRACE_GET_CUR_THREAD_NAME_H

/*
 * Return the current task name through an explicit zero-argument port seam.
 * The target adapter preserves the recovered vTaskName behavior by loading
 * the current TCB word and adding the configured task-name offset. This keeps
 * the zero-argument ABI independent of any incoming register value.
 */
const char *open_cfw_cmbacktrace_pc_task_get_name_current(void);

/* Return the current FreeRTOS task name for CmBacktrace diagnostics. */
const char *open_cfw_cmbacktrace_get_cur_thread_name(void);

#endif
