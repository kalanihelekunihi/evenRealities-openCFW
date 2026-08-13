#include <stdarg.h>

void *open_cfw_test_lv_buffer_sync_display;
unsigned char open_cfw_test_lv_buffer_sync_ready_result;
unsigned int open_cfw_test_lv_buffer_sync_trace_count;
unsigned int open_cfw_test_lv_buffer_sync_trace[4];
unsigned int open_cfw_test_lv_buffer_sync_ready_calls;
void *open_cfw_test_lv_buffer_sync_ready_display;

typedef struct {
    int x1;
    int y1;
    int x2;
    int y2;
} open_cfw_test_lv_buffer_sync_area;

open_cfw_test_lv_buffer_sync_area open_cfw_test_lv_buffer_sync_ready_area;
unsigned int open_cfw_test_lv_buffer_sync_ready_layer;
unsigned int open_cfw_test_lv_buffer_sync_transfer_calls;
void *open_cfw_test_lv_buffer_sync_transfer_destination;
const void *open_cfw_test_lv_buffer_sync_transfer_source;
unsigned int open_cfw_test_lv_buffer_sync_transfer_width;
unsigned int open_cfw_test_lv_buffer_sync_transfer_height;
unsigned int open_cfw_test_lv_buffer_sync_select_calls;
unsigned int open_cfw_test_lv_buffer_sync_select_value;
unsigned int open_cfw_test_lv_buffer_sync_finish_calls;
unsigned int open_cfw_test_lv_buffer_sync_finish_value;
unsigned int open_cfw_test_lv_buffer_sync_log_calls;
unsigned int open_cfw_test_lv_buffer_sync_log_level;
const void *open_cfw_test_lv_buffer_sync_log_file;
unsigned int open_cfw_test_lv_buffer_sync_log_line;
const void *open_cfw_test_lv_buffer_sync_log_function;
const void *open_cfw_test_lv_buffer_sync_log_arguments[3];
unsigned int open_cfw_test_lv_buffer_sync_fatal_calls;

static void open_cfw_test_lv_buffer_sync_record(unsigned int value)
{
    unsigned int index = open_cfw_test_lv_buffer_sync_trace_count++;

    if (index < 4U) {
        open_cfw_test_lv_buffer_sync_trace[index] = value;
    }
}

unsigned char open_cfw_test_lv_buffer_sync_ready(
    void *display,
    const open_cfw_test_lv_buffer_sync_area *area,
    unsigned int layer
)
{
    open_cfw_test_lv_buffer_sync_record(1U);
    open_cfw_test_lv_buffer_sync_ready_calls += 1U;
    open_cfw_test_lv_buffer_sync_ready_display = display;
    open_cfw_test_lv_buffer_sync_ready_area = *area;
    open_cfw_test_lv_buffer_sync_ready_layer = layer;
    return open_cfw_test_lv_buffer_sync_ready_result;
}

void open_cfw_test_lv_buffer_sync_transfer(
    void *destination,
    const void *source,
    unsigned int width,
    unsigned int height
)
{
    open_cfw_test_lv_buffer_sync_record(2U);
    open_cfw_test_lv_buffer_sync_transfer_calls += 1U;
    open_cfw_test_lv_buffer_sync_transfer_destination = destination;
    open_cfw_test_lv_buffer_sync_transfer_source = source;
    open_cfw_test_lv_buffer_sync_transfer_width = width;
    open_cfw_test_lv_buffer_sync_transfer_height = height;
}

void open_cfw_test_lv_buffer_sync_select(unsigned int value)
{
    open_cfw_test_lv_buffer_sync_record(3U);
    open_cfw_test_lv_buffer_sync_select_calls += 1U;
    open_cfw_test_lv_buffer_sync_select_value = value;
}

void open_cfw_test_lv_buffer_sync_finish(unsigned int value)
{
    open_cfw_test_lv_buffer_sync_record(4U);
    open_cfw_test_lv_buffer_sync_finish_calls += 1U;
    open_cfw_test_lv_buffer_sync_finish_value = value;
}

void open_cfw_test_lv_buffer_sync_log(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
)
{
    va_list arguments;
    unsigned int index;

    open_cfw_test_lv_buffer_sync_log_calls += 1U;
    open_cfw_test_lv_buffer_sync_log_level = level;
    open_cfw_test_lv_buffer_sync_log_file = file;
    open_cfw_test_lv_buffer_sync_log_line = line;
    open_cfw_test_lv_buffer_sync_log_function = function;
    va_start(arguments, function);
    for (index = 0U; index < 3U; index += 1U) {
        open_cfw_test_lv_buffer_sync_log_arguments[index] =
            va_arg(arguments, const void *);
    }
    va_end(arguments);
}

void open_cfw_test_lv_buffer_sync_fatal(void)
{
    open_cfw_test_lv_buffer_sync_fatal_calls += 1U;
}

#define OPEN_CFW_LV_BUFFER_SYNC_DISPLAY \
    open_cfw_test_lv_buffer_sync_display
#define OPEN_CFW_LV_BUFFER_SYNC_READY(display, area, layer) \
    open_cfw_test_lv_buffer_sync_ready( \
        (display), \
        (const open_cfw_test_lv_buffer_sync_area *)(const void *)(area), \
        (layer) \
    )
#define OPEN_CFW_LV_BUFFER_SYNC_TRANSFER(destination, source, width, height) \
    open_cfw_test_lv_buffer_sync_transfer( \
        (destination), \
        (source), \
        (width), \
        (height) \
    )
#define OPEN_CFW_LV_BUFFER_SYNC_SELECT(value) \
    open_cfw_test_lv_buffer_sync_select(value)
#define OPEN_CFW_LV_BUFFER_SYNC_FINISH(value) \
    open_cfw_test_lv_buffer_sync_finish(value)
#define OPEN_CFW_LV_BUFFER_SYNC_LOG open_cfw_test_lv_buffer_sync_log
#define OPEN_CFW_LV_BUFFER_SYNC_FATAL() open_cfw_test_lv_buffer_sync_fatal()

#include "../../components/apollo_main/core_overlay/lv_buffer_sync.c"
