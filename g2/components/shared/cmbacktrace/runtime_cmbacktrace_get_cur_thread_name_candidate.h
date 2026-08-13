/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CMBACKTRACE_GET_CUR_THREAD_NAME_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CMBACKTRACE_GET_CUR_THREAD_NAME_CANDIDATE_H

/*
 * Production-excluded CmBacktrace/FreeRTOS integration seam.
 *
 * A candidate host or target supplies this symbol with the semantics of the
 * already source-owned FreeRTOS pcTaskGetName(NULL) call.  Keeping the seam
 * external makes the candidate's sole dependency explicit and prevents this
 * research boundary from reaching the retained G2 vTaskName adapter.
 */
const char *open_cfw_cmbacktrace_pc_task_get_name_current_candidate(void);

/* Return the current FreeRTOS task name through the explicit port seam. */
const char *open_cfw_cmbacktrace_get_cur_thread_name_candidate(void);

#endif
