unsigned int open_cfw_test_handler_order_count;
unsigned int open_cfw_test_handler_order[4];
const void *open_cfw_test_length_buffer;
unsigned int open_cfw_test_length_result;
unsigned int open_cfw_test_sink_selector;
const void *open_cfw_test_sink_buffer;
unsigned int open_cfw_test_sink_length;

void (*open_cfw_test_callback_target)(void *context);

void open_cfw_test_handler_reset(void)
{
    open_cfw_test_handler_order_count = 0U;
    open_cfw_test_handler_order[0] = 0U;
    open_cfw_test_handler_order[1] = 0U;
    open_cfw_test_handler_order[2] = 0U;
    open_cfw_test_handler_order[3] = 0U;
    open_cfw_test_length_buffer = (const void *)0;
    open_cfw_test_length_result = 0U;
    open_cfw_test_sink_selector = 0U;
    open_cfw_test_sink_buffer = (const void *)0;
    open_cfw_test_sink_length = 0U;
}

unsigned int open_cfw_test_handler_length(const void *buffer)
{
    open_cfw_test_handler_order[open_cfw_test_handler_order_count++] = 1U;
    open_cfw_test_length_buffer = buffer;
    return open_cfw_test_length_result;
}

void open_cfw_test_handler_sink(
    unsigned int selector,
    const void *buffer,
    unsigned int length
)
{
    open_cfw_test_handler_order[open_cfw_test_handler_order_count++] = 2U;
    open_cfw_test_sink_selector = selector;
    open_cfw_test_sink_buffer = buffer;
    open_cfw_test_sink_length = length;
}

#define OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET open_cfw_test_callback_target
#define OPEN_CFW_UI_DISPLAY_HANDLER_LENGTH(buffer) \
    open_cfw_test_handler_length(buffer)
#define OPEN_CFW_UI_DISPLAY_HANDLER_SINK(selector, buffer, length) \
    open_cfw_test_handler_sink((selector), (buffer), (length))

#include "../../components/apollo_main/core_overlay/ui_display_callback.c"
