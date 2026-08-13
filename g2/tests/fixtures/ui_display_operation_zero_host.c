unsigned char open_cfw_test_operation_zero_busy;
unsigned int open_cfw_test_operation_zero_limit;
unsigned int open_cfw_test_operation_zero_start_result;
unsigned int open_cfw_test_operation_zero_start_count;
unsigned int open_cfw_test_operation_zero_service_count;
unsigned int open_cfw_test_operation_zero_delay_count;
unsigned int open_cfw_test_operation_zero_delay_value;
unsigned int open_cfw_test_operation_zero_service_clear_after;
void *open_cfw_test_operation_zero_start_handle;
const void *open_cfw_test_operation_zero_start_descriptor;
void *open_cfw_test_operation_zero_service_handle;

void open_cfw_test_operation_zero_reset(void)
{
    open_cfw_test_operation_zero_busy = 1U;
    open_cfw_test_operation_zero_limit = 0xFFFFFFFFU;
    open_cfw_test_operation_zero_start_result = 0U;
    open_cfw_test_operation_zero_start_count = 0U;
    open_cfw_test_operation_zero_service_count = 0U;
    open_cfw_test_operation_zero_delay_count = 0U;
    open_cfw_test_operation_zero_delay_value = 0U;
    open_cfw_test_operation_zero_service_clear_after = 0xFFFFFFFFU;
    open_cfw_test_operation_zero_start_handle = (void *)0;
    open_cfw_test_operation_zero_start_descriptor = (const void *)0;
    open_cfw_test_operation_zero_service_handle = (void *)0;
}

unsigned int open_cfw_test_operation_zero_start(
    void *handle,
    const void *descriptor
)
{
    ++open_cfw_test_operation_zero_start_count;
    open_cfw_test_operation_zero_start_handle = handle;
    open_cfw_test_operation_zero_start_descriptor = descriptor;
    return open_cfw_test_operation_zero_start_result;
}

void open_cfw_test_operation_zero_service(void *handle)
{
    ++open_cfw_test_operation_zero_service_count;
    open_cfw_test_operation_zero_service_handle = handle;
    if (
        open_cfw_test_operation_zero_service_count
            == open_cfw_test_operation_zero_service_clear_after
    ) {
        open_cfw_test_operation_zero_busy = 0U;
    }
}

void open_cfw_test_operation_zero_delay(unsigned int duration)
{
    ++open_cfw_test_operation_zero_delay_count;
    open_cfw_test_operation_zero_delay_value = duration;
}

#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_BUSY(handle) \
    open_cfw_test_operation_zero_busy
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_LIMIT(descriptor) \
    open_cfw_test_operation_zero_limit
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_START(handle, descriptor) \
    open_cfw_test_operation_zero_start((handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_SERVICE(handle) \
    open_cfw_test_operation_zero_service(handle)
#define OPEN_CFW_UI_DISPLAY_OPERATION_ZERO_DELAY(duration) \
    open_cfw_test_operation_zero_delay(duration)

#include "../../components/apollo_main/core_overlay/ui_display_operation_zero.c"
