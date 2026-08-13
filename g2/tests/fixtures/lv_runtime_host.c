unsigned int open_cfw_test_lv_runtime_primask;
unsigned int open_cfw_test_lv_runtime_trace_count;
unsigned int open_cfw_test_lv_runtime_trace[2];
unsigned int open_cfw_test_lv_runtime_read_calls;
unsigned int open_cfw_test_lv_runtime_enable_calls;
unsigned int open_cfw_test_lv_runtime_disable_calls;

static void open_cfw_test_lv_runtime_record(unsigned int value)
{
    unsigned int index = open_cfw_test_lv_runtime_trace_count++;

    if (index < 2U) {
        open_cfw_test_lv_runtime_trace[index] = value;
    }
}

unsigned int open_cfw_test_lv_runtime_read(void)
{
    open_cfw_test_lv_runtime_record(1U);
    open_cfw_test_lv_runtime_read_calls += 1U;
    return open_cfw_test_lv_runtime_primask;
}

void open_cfw_test_lv_runtime_enable(void)
{
    open_cfw_test_lv_runtime_record(2U);
    open_cfw_test_lv_runtime_enable_calls += 1U;
}

void open_cfw_test_lv_runtime_disable(void)
{
    open_cfw_test_lv_runtime_record(3U);
    open_cfw_test_lv_runtime_disable_calls += 1U;
}

#define OPEN_CFW_LV_RUNTIME_PRIMASK_READ() \
    open_cfw_test_lv_runtime_read()
#define OPEN_CFW_LV_RUNTIME_IRQ_ENABLE() \
    open_cfw_test_lv_runtime_enable()
#define OPEN_CFW_LV_RUNTIME_IRQ_DISABLE() \
    open_cfw_test_lv_runtime_disable()

#include "../../components/apollo_main/core_overlay/lv_runtime.c"
