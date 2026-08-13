/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name_candidate.h"

extern const char *open_cfw_cmbacktrace_get_cur_thread_name_upstream_oracle(
    void
);

static const char *open_cfw_test_current_name;
static uint32_t open_cfw_test_candidate_seam_calls;
static uint32_t open_cfw_test_upstream_seam_calls;

void open_cfw_test_cmbacktrace_get_cur_thread_name_reset(
    const char *current_name
)
{
    open_cfw_test_current_name = current_name;
    open_cfw_test_candidate_seam_calls = 0U;
    open_cfw_test_upstream_seam_calls = 0U;
}

const char *open_cfw_cmbacktrace_pc_task_get_name_current_candidate(void)
{
    open_cfw_test_candidate_seam_calls++;
    return open_cfw_test_current_name;
}

const char *vTaskName(void)
{
    open_cfw_test_upstream_seam_calls++;
    return open_cfw_test_current_name;
}

const char *open_cfw_test_cmbacktrace_get_cur_thread_name_candidate(void)
{
    return open_cfw_cmbacktrace_get_cur_thread_name_candidate();
}

const char *open_cfw_test_cmbacktrace_get_cur_thread_name_upstream(void)
{
    return open_cfw_cmbacktrace_get_cur_thread_name_upstream_oracle();
}

uint32_t open_cfw_test_cmbacktrace_candidate_seam_calls(void)
{
    return open_cfw_test_candidate_seam_calls;
}

uint32_t open_cfw_test_cmbacktrace_upstream_seam_calls(void)
{
    return open_cfw_test_upstream_seam_calls;
}
