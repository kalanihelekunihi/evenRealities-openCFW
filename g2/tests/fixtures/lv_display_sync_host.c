typedef struct {
    int x1;
    int y1;
    int x2;
    int y2;
} open_cfw_test_lv_display_sync_area;

int open_cfw_test_lv_display_sync_x;
int open_cfw_test_lv_display_sync_y;
unsigned char open_cfw_test_lv_display_sync_ready_result;
void *open_cfw_test_lv_display_sync_buffer;
unsigned int open_cfw_test_lv_display_sync_trace_count;
unsigned int open_cfw_test_lv_display_sync_trace[10];
unsigned int open_cfw_test_lv_display_sync_get_x_calls;
void *open_cfw_test_lv_display_sync_get_x_display;
unsigned int open_cfw_test_lv_display_sync_get_y_calls;
void *open_cfw_test_lv_display_sync_get_y_display;
unsigned int open_cfw_test_lv_display_sync_translate_calls;
open_cfw_test_lv_display_sync_area
    open_cfw_test_lv_display_sync_translate_input;
open_cfw_test_lv_display_sync_area
    open_cfw_test_lv_display_sync_translate_output;
unsigned int open_cfw_test_lv_display_sync_translate_dx;
unsigned int open_cfw_test_lv_display_sync_translate_dy;
unsigned int open_cfw_test_lv_display_sync_select_calls;
void *open_cfw_test_lv_display_sync_select_buffer;
unsigned int open_cfw_test_lv_display_sync_select_value;
unsigned int open_cfw_test_lv_display_sync_ready_calls;
void *open_cfw_test_lv_display_sync_ready_display;
unsigned int open_cfw_test_lv_display_sync_begin_calls;
unsigned int open_cfw_test_lv_display_sync_buffer_sync_calls;
const void *open_cfw_test_lv_display_sync_buffer_sync_area;
void *open_cfw_test_lv_display_sync_buffer_sync_destination;
unsigned char open_cfw_test_lv_display_sync_buffer_sync_finish;
unsigned int open_cfw_test_lv_display_sync_end_calls;
unsigned int open_cfw_test_lv_display_sync_clear_calls;
unsigned int open_cfw_test_lv_display_sync_clear_arguments[6];

static void open_cfw_test_lv_display_sync_record(unsigned int value)
{
    unsigned int index = open_cfw_test_lv_display_sync_trace_count++;

    if (index < 10U) {
        open_cfw_test_lv_display_sync_trace[index] = value;
    }
}

int open_cfw_test_lv_display_sync_get_x(void *display)
{
    open_cfw_test_lv_display_sync_record(1U);
    open_cfw_test_lv_display_sync_get_x_calls += 1U;
    open_cfw_test_lv_display_sync_get_x_display = display;
    return open_cfw_test_lv_display_sync_x;
}

int open_cfw_test_lv_display_sync_get_y(void *display)
{
    open_cfw_test_lv_display_sync_record(2U);
    open_cfw_test_lv_display_sync_get_y_calls += 1U;
    open_cfw_test_lv_display_sync_get_y_display = display;
    return open_cfw_test_lv_display_sync_y;
}

void open_cfw_test_lv_display_sync_translate(
    open_cfw_test_lv_display_sync_area *area,
    unsigned int dx,
    unsigned int dy
)
{
    open_cfw_test_lv_display_sync_record(3U);
    open_cfw_test_lv_display_sync_translate_calls += 1U;
    open_cfw_test_lv_display_sync_translate_input = *area;
    open_cfw_test_lv_display_sync_translate_dx = dx;
    open_cfw_test_lv_display_sync_translate_dy = dy;
    area->x1 = (int)((unsigned int)area->x1 + dx);
    area->x2 = (int)((unsigned int)area->x2 + dx);
    area->y1 = (int)((unsigned int)area->y1 + dy);
    area->y2 = (int)((unsigned int)area->y2 + dy);
    open_cfw_test_lv_display_sync_translate_output = *area;
}

void open_cfw_test_lv_display_sync_select(
    void *buffer,
    unsigned int value
)
{
    open_cfw_test_lv_display_sync_record(4U);
    open_cfw_test_lv_display_sync_select_calls += 1U;
    open_cfw_test_lv_display_sync_select_buffer = buffer;
    open_cfw_test_lv_display_sync_select_value = value;
}

unsigned char open_cfw_test_lv_display_sync_ready(void *display)
{
    open_cfw_test_lv_display_sync_record(5U);
    open_cfw_test_lv_display_sync_ready_calls += 1U;
    open_cfw_test_lv_display_sync_ready_display = display;
    return open_cfw_test_lv_display_sync_ready_result;
}

void open_cfw_test_lv_display_sync_begin(void)
{
    open_cfw_test_lv_display_sync_record(6U);
    open_cfw_test_lv_display_sync_begin_calls += 1U;
}

void open_cfw_test_lv_display_sync_buffer_sync(
    const void *area,
    void *destination,
    unsigned char finish
)
{
    open_cfw_test_lv_display_sync_record(7U);
    open_cfw_test_lv_display_sync_buffer_sync_calls += 1U;
    open_cfw_test_lv_display_sync_buffer_sync_area = area;
    open_cfw_test_lv_display_sync_buffer_sync_destination = destination;
    open_cfw_test_lv_display_sync_buffer_sync_finish = finish;
}

void open_cfw_test_lv_display_sync_end(void)
{
    open_cfw_test_lv_display_sync_record(8U);
    open_cfw_test_lv_display_sync_end_calls += 1U;
}

void open_cfw_test_lv_display_sync_clear(
    unsigned int x1,
    unsigned int y1,
    unsigned int x2,
    unsigned int y2,
    unsigned int width,
    unsigned int height
)
{
    open_cfw_test_lv_display_sync_record(9U);
    open_cfw_test_lv_display_sync_clear_calls += 1U;
    open_cfw_test_lv_display_sync_clear_arguments[0] = x1;
    open_cfw_test_lv_display_sync_clear_arguments[1] = y1;
    open_cfw_test_lv_display_sync_clear_arguments[2] = x2;
    open_cfw_test_lv_display_sync_clear_arguments[3] = y2;
    open_cfw_test_lv_display_sync_clear_arguments[4] = width;
    open_cfw_test_lv_display_sync_clear_arguments[5] = height;
}

#define OPEN_CFW_LV_DISPLAY_SYNC_GET_X(display) \
    open_cfw_test_lv_display_sync_get_x(display)
#define OPEN_CFW_LV_DISPLAY_SYNC_GET_Y(display) \
    open_cfw_test_lv_display_sync_get_y(display)
#define OPEN_CFW_LV_DISPLAY_SYNC_TRANSLATE(area, dx, dy) \
    open_cfw_test_lv_display_sync_translate( \
        (open_cfw_test_lv_display_sync_area *)(void *)(area), \
        (dx), \
        (dy) \
    )
#define OPEN_CFW_LV_DISPLAY_SYNC_BUFFER \
    open_cfw_test_lv_display_sync_buffer
#define OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SELECT(buffer, value) \
    open_cfw_test_lv_display_sync_select((buffer), (value))
#define OPEN_CFW_LV_DISPLAY_SYNC_READY(display) \
    open_cfw_test_lv_display_sync_ready(display)
#define OPEN_CFW_LV_DISPLAY_SYNC_BEGIN() \
    open_cfw_test_lv_display_sync_begin()
#define OPEN_CFW_LV_DISPLAY_SYNC_BUFFER_SYNC(area, destination, finish) \
    open_cfw_test_lv_display_sync_buffer_sync( \
        (area), \
        (destination), \
        (finish) \
    )
#define OPEN_CFW_LV_DISPLAY_SYNC_END() \
    open_cfw_test_lv_display_sync_end()
#define OPEN_CFW_LV_DISPLAY_SYNC_CLEAR(x1, y1, x2, y2, width, height) \
    open_cfw_test_lv_display_sync_clear( \
        (x1), \
        (y1), \
        (x2), \
        (y2), \
        (width), \
        (height) \
    )

#include "../../components/apollo_main/core_overlay/lv_display_sync.c"
