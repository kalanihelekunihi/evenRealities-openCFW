#include <stdint.h>

#include "../../components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.h"
#include "../../components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name_candidate.h"

extern const char *open_cfw_cmbacktrace_get_cur_thread_name_upstream_oracle(
    void
);

static const char *open_cfw_test_name;
static uintptr_t open_cfw_test_current_tcb;
static uint32_t open_cfw_test_production_calls;
static uint32_t open_cfw_test_candidate_calls;
static uint32_t open_cfw_test_upstream_calls;

void open_cfw_test_cmbacktrace_get_cur_thread_name_production_reset(
    uintptr_t current_tcb
)
{
    open_cfw_test_current_tcb = current_tcb;
    open_cfw_test_name = (const char *)(current_tcb + 0x34U);
    open_cfw_test_production_calls = 0U;
    open_cfw_test_candidate_calls = 0U;
    open_cfw_test_upstream_calls = 0U;
}

uintptr_t open_cfw_cmbacktrace_host_test_current_tcb(void)
{
    open_cfw_test_production_calls++;
    return open_cfw_test_current_tcb;
}

const char *open_cfw_cmbacktrace_pc_task_get_name_current_candidate(void)
{
    open_cfw_test_candidate_calls++;
    return open_cfw_test_name;
}

char *vTaskName(void)
{
    open_cfw_test_upstream_calls++;
    return (char *)open_cfw_test_name;
}

const char *open_cfw_test_cmbacktrace_get_cur_thread_name_production(void)
{
    return open_cfw_cmbacktrace_get_cur_thread_name();
}

const char *open_cfw_test_cmbacktrace_get_cur_thread_name_candidate(void)
{
    return open_cfw_cmbacktrace_get_cur_thread_name_candidate();
}

const char *open_cfw_test_cmbacktrace_get_cur_thread_name_upstream(void)
{
    return open_cfw_cmbacktrace_get_cur_thread_name_upstream_oracle();
}

uint32_t open_cfw_test_cmbacktrace_production_calls(void)
{
    return open_cfw_test_production_calls;
}

uint32_t open_cfw_test_cmbacktrace_candidate_calls(void)
{
    return open_cfw_test_candidate_calls;
}

uint32_t open_cfw_test_cmbacktrace_upstream_calls(void)
{
    return open_cfw_test_upstream_calls;
}
