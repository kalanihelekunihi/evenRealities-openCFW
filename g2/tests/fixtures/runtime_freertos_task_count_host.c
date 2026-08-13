#include <stdint.h>

static volatile uint32_t open_cfw_test_task_count;
static volatile uint32_t open_cfw_test_task_count_reads;

static uint32_t open_cfw_test_read_task_count(void)
{
    ++open_cfw_test_task_count_reads;
    return open_cfw_test_task_count;
}

#define OPEN_CFW_FREERTOS_CURRENT_TASK_COUNT \
    open_cfw_test_read_task_count()

#include "../../components/apollo_main/core_overlay/runtime_freertos_task_count.c"

void open_cfw_test_freertos_task_count_set(uint32_t count)
{
    open_cfw_test_task_count = count;
    open_cfw_test_task_count_reads = 0U;
}

uint32_t open_cfw_test_freertos_task_count_get(void)
{
    return open_cfw_freertos_task_get_number_of_tasks();
}

uint32_t open_cfw_test_freertos_task_count_reads(void)
{
    return open_cfw_test_task_count_reads;
}
