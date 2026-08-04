unsigned int open_cfw_test_duration_delay_perf_status;
unsigned int open_cfw_test_duration_delay_cycle_calls;
unsigned int open_cfw_test_duration_delay_cycles;

void open_cfw_test_duration_delay_reset(void)
{
    open_cfw_test_duration_delay_perf_status = 1U;
    open_cfw_test_duration_delay_cycle_calls = 0U;
    open_cfw_test_duration_delay_cycles = 0U;
}

void open_cfw_test_duration_delay_record(unsigned int iterations)
{
    ++open_cfw_test_duration_delay_cycle_calls;
    open_cfw_test_duration_delay_cycles = iterations;
}

#define OPEN_CFW_DURATION_DELAY_HOST 1
#define OPEN_CFW_DURATION_DELAY_PERF_STATUS() \
    open_cfw_test_duration_delay_perf_status
#define OPEN_CFW_DURATION_DELAY_CYCLES(iterations) \
    open_cfw_test_duration_delay_record(iterations)

#include "../../components/apollo_main/core_overlay/duration_delay.c"
