#include <stdarg.h>

void *open_cfw_test_lv_display_setup_state;
void *open_cfw_test_lv_display_setup_buffer;
unsigned char open_cfw_test_lv_display_setup_configure_result;
unsigned int open_cfw_test_lv_display_setup_configuration_result;
void *open_cfw_test_lv_display_setup_allocate_result;
void *open_cfw_test_lv_display_setup_create_result;
void *open_cfw_test_lv_display_setup_buffer_create_result;
unsigned int open_cfw_test_lv_display_setup_trace_count;
unsigned int open_cfw_test_lv_display_setup_trace[10];
unsigned int open_cfw_test_lv_display_setup_allocate_calls;
unsigned int open_cfw_test_lv_display_setup_allocate_size;
unsigned int open_cfw_test_lv_display_setup_configuration_calls;
unsigned int open_cfw_test_lv_display_setup_configure_calls;
void *open_cfw_test_lv_display_setup_configure_state;
unsigned int open_cfw_test_lv_display_setup_configure_arguments[6];
unsigned int open_cfw_test_lv_display_setup_log_calls;
unsigned int open_cfw_test_lv_display_setup_log_level;
const void *open_cfw_test_lv_display_setup_log_file;
unsigned int open_cfw_test_lv_display_setup_log_line;
const void *open_cfw_test_lv_display_setup_log_function;
const void *open_cfw_test_lv_display_setup_log_argument;
unsigned int open_cfw_test_lv_display_setup_create_calls;
unsigned int open_cfw_test_lv_display_setup_create_arguments[2];
unsigned int open_cfw_test_lv_display_setup_register_calls;
void *open_cfw_test_lv_display_setup_register_object;
const void *open_cfw_test_lv_display_setup_register_callback;
unsigned int open_cfw_test_lv_display_setup_buffer_create_calls;
unsigned int open_cfw_test_lv_display_setup_buffer_create_arguments[4];
unsigned int open_cfw_test_lv_display_setup_attach_calls;
void *open_cfw_test_lv_display_setup_attach_object;
void *open_cfw_test_lv_display_setup_attach_buffer;
unsigned int open_cfw_test_lv_display_setup_attach_layer;
unsigned int open_cfw_test_lv_display_setup_mode_calls;
void *open_cfw_test_lv_display_setup_mode_object;
unsigned int open_cfw_test_lv_display_setup_mode_value;
unsigned int open_cfw_test_lv_display_setup_size_calls;
void *open_cfw_test_lv_display_setup_size_object;
unsigned int open_cfw_test_lv_display_setup_size_arguments[2];
unsigned int open_cfw_test_lv_display_setup_position_calls;
void *open_cfw_test_lv_display_setup_position_object;
unsigned int open_cfw_test_lv_display_setup_position_arguments[2];

static void open_cfw_test_lv_display_setup_record(unsigned int value)
{
    unsigned int index = open_cfw_test_lv_display_setup_trace_count++;

    if (index < 10U) {
        open_cfw_test_lv_display_setup_trace[index] = value;
    }
}

void *open_cfw_test_lv_display_setup_allocate(unsigned int size)
{
    open_cfw_test_lv_display_setup_record(1U);
    open_cfw_test_lv_display_setup_allocate_calls += 1U;
    open_cfw_test_lv_display_setup_allocate_size = size;
    return open_cfw_test_lv_display_setup_allocate_result;
}

unsigned int open_cfw_test_lv_display_setup_configuration(void)
{
    open_cfw_test_lv_display_setup_record(2U);
    open_cfw_test_lv_display_setup_configuration_calls += 1U;
    return open_cfw_test_lv_display_setup_configuration_result;
}

unsigned char open_cfw_test_lv_display_setup_configure(
    void *state,
    unsigned int width,
    unsigned int height,
    unsigned int format,
    unsigned int flags,
    unsigned int configuration,
    unsigned int bytes
)
{
    open_cfw_test_lv_display_setup_record(3U);
    open_cfw_test_lv_display_setup_configure_calls += 1U;
    open_cfw_test_lv_display_setup_configure_state = state;
    open_cfw_test_lv_display_setup_configure_arguments[0] = width;
    open_cfw_test_lv_display_setup_configure_arguments[1] = height;
    open_cfw_test_lv_display_setup_configure_arguments[2] = format;
    open_cfw_test_lv_display_setup_configure_arguments[3] = flags;
    open_cfw_test_lv_display_setup_configure_arguments[4] = configuration;
    open_cfw_test_lv_display_setup_configure_arguments[5] = bytes;
    return open_cfw_test_lv_display_setup_configure_result;
}

void open_cfw_test_lv_display_setup_log(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
)
{
    va_list arguments;

    open_cfw_test_lv_display_setup_record(4U);
    open_cfw_test_lv_display_setup_log_calls += 1U;
    open_cfw_test_lv_display_setup_log_level = level;
    open_cfw_test_lv_display_setup_log_file = file;
    open_cfw_test_lv_display_setup_log_line = line;
    open_cfw_test_lv_display_setup_log_function = function;
    va_start(arguments, function);
    open_cfw_test_lv_display_setup_log_argument =
        va_arg(arguments, const void *);
    va_end(arguments);
}

void *open_cfw_test_lv_display_setup_create(
    unsigned int width,
    unsigned int height
)
{
    open_cfw_test_lv_display_setup_record(4U);
    open_cfw_test_lv_display_setup_create_calls += 1U;
    open_cfw_test_lv_display_setup_create_arguments[0] = width;
    open_cfw_test_lv_display_setup_create_arguments[1] = height;
    return open_cfw_test_lv_display_setup_create_result;
}

void open_cfw_test_lv_display_setup_register(
    void *object,
    const void *callback
)
{
    open_cfw_test_lv_display_setup_record(5U);
    open_cfw_test_lv_display_setup_register_calls += 1U;
    open_cfw_test_lv_display_setup_register_object = object;
    open_cfw_test_lv_display_setup_register_callback = callback;
}

void *open_cfw_test_lv_display_setup_buffer_create(
    unsigned int width,
    unsigned int height,
    unsigned int format,
    unsigned int flags
)
{
    open_cfw_test_lv_display_setup_record(6U);
    open_cfw_test_lv_display_setup_buffer_create_calls += 1U;
    open_cfw_test_lv_display_setup_buffer_create_arguments[0] = width;
    open_cfw_test_lv_display_setup_buffer_create_arguments[1] = height;
    open_cfw_test_lv_display_setup_buffer_create_arguments[2] = format;
    open_cfw_test_lv_display_setup_buffer_create_arguments[3] = flags;
    return open_cfw_test_lv_display_setup_buffer_create_result;
}

void open_cfw_test_lv_display_setup_attach(
    void *object,
    void *buffer,
    unsigned int layer
)
{
    open_cfw_test_lv_display_setup_record(7U);
    open_cfw_test_lv_display_setup_attach_calls += 1U;
    open_cfw_test_lv_display_setup_attach_object = object;
    open_cfw_test_lv_display_setup_attach_buffer = buffer;
    open_cfw_test_lv_display_setup_attach_layer = layer;
}

void open_cfw_test_lv_display_setup_mode(
    void *object,
    unsigned int value
)
{
    open_cfw_test_lv_display_setup_record(8U);
    open_cfw_test_lv_display_setup_mode_calls += 1U;
    open_cfw_test_lv_display_setup_mode_object = object;
    open_cfw_test_lv_display_setup_mode_value = value;
}

void open_cfw_test_lv_display_setup_size(
    void *object,
    unsigned int width,
    unsigned int height
)
{
    open_cfw_test_lv_display_setup_record(9U);
    open_cfw_test_lv_display_setup_size_calls += 1U;
    open_cfw_test_lv_display_setup_size_object = object;
    open_cfw_test_lv_display_setup_size_arguments[0] = width;
    open_cfw_test_lv_display_setup_size_arguments[1] = height;
}

void open_cfw_test_lv_display_setup_position(
    void *object,
    unsigned int x,
    unsigned int y
)
{
    open_cfw_test_lv_display_setup_record(10U);
    open_cfw_test_lv_display_setup_position_calls += 1U;
    open_cfw_test_lv_display_setup_position_object = object;
    open_cfw_test_lv_display_setup_position_arguments[0] = x;
    open_cfw_test_lv_display_setup_position_arguments[1] = y;
}

#define OPEN_CFW_LV_DISPLAY_SETUP_STATE \
    open_cfw_test_lv_display_setup_state
#define OPEN_CFW_LV_DISPLAY_SETUP_BUFFER \
    open_cfw_test_lv_display_setup_buffer
#define OPEN_CFW_LV_DISPLAY_SETUP_ALLOCATE(size) \
    open_cfw_test_lv_display_setup_allocate(size)
#define OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURATION() \
    open_cfw_test_lv_display_setup_configuration()
#define OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURE( \
    state, width, height, format, flags, configuration, bytes \
) \
    open_cfw_test_lv_display_setup_configure( \
        (state), \
        (width), \
        (height), \
        (format), \
        (flags), \
        (configuration), \
        (bytes) \
    )
#define OPEN_CFW_LV_DISPLAY_SETUP_LOG open_cfw_test_lv_display_setup_log
#define OPEN_CFW_LV_DISPLAY_SETUP_CREATE(width, height) \
    open_cfw_test_lv_display_setup_create((width), (height))
#define OPEN_CFW_LV_DISPLAY_SETUP_REGISTER(object, callback) \
    open_cfw_test_lv_display_setup_register((object), (callback))
#define OPEN_CFW_LV_DISPLAY_SETUP_BUFFER_CREATE(width, height, format, flags) \
    open_cfw_test_lv_display_setup_buffer_create( \
        (width), \
        (height), \
        (format), \
        (flags) \
    )
#define OPEN_CFW_LV_DISPLAY_SETUP_ATTACH(object, buffer, layer) \
    open_cfw_test_lv_display_setup_attach((object), (buffer), (layer))
#define OPEN_CFW_LV_DISPLAY_SETUP_MODE(object, value) \
    open_cfw_test_lv_display_setup_mode((object), (value))
#define OPEN_CFW_LV_DISPLAY_SETUP_SIZE(object, width, height) \
    open_cfw_test_lv_display_setup_size((object), (width), (height))
#define OPEN_CFW_LV_DISPLAY_SETUP_POSITION(object, x, y) \
    open_cfw_test_lv_display_setup_position((object), (x), (y))

#include "../../components/apollo_main/core_overlay/lv_display_setup.c"
