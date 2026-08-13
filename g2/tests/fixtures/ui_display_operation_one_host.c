unsigned char open_cfw_test_operation_one_busy;
unsigned int open_cfw_test_operation_one_limit;
unsigned int open_cfw_test_operation_one_start_result;
unsigned int open_cfw_test_operation_one_start_count;
unsigned int open_cfw_test_operation_one_service_count;
unsigned int open_cfw_test_operation_one_delay_count;
unsigned int open_cfw_test_operation_one_delay_value;
unsigned int open_cfw_test_operation_one_service_clear_after;
unsigned int open_cfw_test_operation_one_trace[32];
unsigned int open_cfw_test_operation_one_trace_count;
void *open_cfw_test_operation_one_start_handle;
const void *open_cfw_test_operation_one_start_descriptor;
void *open_cfw_test_operation_one_service_handle;

void open_cfw_test_operation_one_reset(void)
{
    unsigned int index;

    open_cfw_test_operation_one_busy = 1U;
    open_cfw_test_operation_one_limit = 0xFFFFFFFFU;
    open_cfw_test_operation_one_start_result = 0U;
    open_cfw_test_operation_one_start_count = 0U;
    open_cfw_test_operation_one_service_count = 0U;
    open_cfw_test_operation_one_delay_count = 0U;
    open_cfw_test_operation_one_delay_value = 0U;
    open_cfw_test_operation_one_service_clear_after = 0xFFFFFFFFU;
    open_cfw_test_operation_one_trace_count = 0U;
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_operation_one_trace[index] = 0U;
    }
    open_cfw_test_operation_one_start_handle = (void *)0;
    open_cfw_test_operation_one_start_descriptor = (const void *)0;
    open_cfw_test_operation_one_service_handle = (void *)0;
}

static void open_cfw_test_operation_one_record(unsigned int event)
{
    if (open_cfw_test_operation_one_trace_count < 32U) {
        open_cfw_test_operation_one_trace[
            open_cfw_test_operation_one_trace_count
        ] = event;
    }
    ++open_cfw_test_operation_one_trace_count;
}

unsigned int open_cfw_test_operation_one_start(
    void *handle,
    const void *descriptor
)
{
    ++open_cfw_test_operation_one_start_count;
    open_cfw_test_operation_one_start_handle = handle;
    open_cfw_test_operation_one_start_descriptor = descriptor;
    open_cfw_test_operation_one_record(1U);
    return open_cfw_test_operation_one_start_result;
}

void open_cfw_test_operation_one_service(void *handle)
{
    ++open_cfw_test_operation_one_service_count;
    open_cfw_test_operation_one_service_handle = handle;
    open_cfw_test_operation_one_record(2U);
    if (
        open_cfw_test_operation_one_service_count
            == open_cfw_test_operation_one_service_clear_after
    ) {
        open_cfw_test_operation_one_busy = 0U;
    }
}

void open_cfw_test_operation_one_delay(unsigned int duration)
{
    ++open_cfw_test_operation_one_delay_count;
    open_cfw_test_operation_one_delay_value = duration;
    open_cfw_test_operation_one_record(3U);
}

#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_BUSY(handle) \
    open_cfw_test_operation_one_busy
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_LIMIT(descriptor) \
    open_cfw_test_operation_one_limit
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_START(handle, descriptor) \
    open_cfw_test_operation_one_start((handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_SERVICE(handle) \
    open_cfw_test_operation_one_service(handle)
#define OPEN_CFW_UI_DISPLAY_OPERATION_ONE_DELAY(duration) \
    open_cfw_test_operation_one_delay(duration)

#include "../../components/apollo_main/core_overlay/ui_display_operation_one.c"
