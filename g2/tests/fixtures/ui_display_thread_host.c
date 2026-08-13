#include <stddef.h>

unsigned char open_cfw_test_state[2];
unsigned char open_cfw_test_message[12];
unsigned char open_cfw_test_queued_message[12];
unsigned char open_cfw_test_input[0x2800];
unsigned int open_cfw_test_background;
unsigned int open_cfw_test_mode;
unsigned int open_cfw_test_foreground;
unsigned int open_cfw_test_control;
void *open_cfw_test_driver = (void *)0x1111UL;
void *open_cfw_test_manager = (void *)0x2222UL;
void *open_cfw_test_queue = (void *)0x3333UL;
void *open_cfw_test_mutex = (void *)0x4444UL;
void *open_cfw_test_manager_create_result = (void *)0x5555UL;
unsigned int open_cfw_test_driver_ready;
int open_cfw_test_receive_result;
unsigned int open_cfw_test_switch_result;
unsigned int open_cfw_test_input_result;
unsigned int open_cfw_test_log_flags_value;
unsigned int open_cfw_test_forced_state;

unsigned int open_cfw_test_modules_initialize_count;
unsigned int open_cfw_test_runtime_initialize_count;
unsigned int open_cfw_test_before_count;
unsigned int open_cfw_test_after_count;
unsigned int open_cfw_test_receive_count;
unsigned int open_cfw_test_receive_control;
unsigned int open_cfw_test_mutex_take_count;
unsigned int open_cfw_test_mutex_give_count;
unsigned int open_cfw_test_extract_count;
unsigned int open_cfw_test_extract_token;
unsigned int open_cfw_test_start_prepare_count;
unsigned int open_cfw_test_start_transport_count;
unsigned int open_cfw_test_start_display_count;
unsigned int open_cfw_test_registry_reset_count;
unsigned int open_cfw_test_ui_initialize_count;
unsigned int open_cfw_test_manager_create_count;
unsigned int open_cfw_test_manager_configure_count;
unsigned int open_cfw_test_renderer_initialize_count;
unsigned int open_cfw_test_manager_commit_count;
unsigned int open_cfw_test_background_id_count;
unsigned int open_cfw_test_background_id;
unsigned int open_cfw_test_render_mode_count;
unsigned int open_cfw_test_render_mode;
unsigned int open_cfw_test_refresh_count;
unsigned int open_cfw_test_notify_count;
unsigned int open_cfw_test_update_power_count;
unsigned int open_cfw_test_manager_open_count;
unsigned int open_cfw_test_manager_open_operation[8];
unsigned int open_cfw_test_manager_open_service[8];
unsigned int open_cfw_test_delay_count;
unsigned int open_cfw_test_delay_ticks;
unsigned int open_cfw_test_manager_destroy_count;
void *open_cfw_test_manager_destroy_value;
unsigned int open_cfw_test_close_prepare_count;
unsigned int open_cfw_test_close_display_count;
unsigned int open_cfw_test_set_active_count;
unsigned int open_cfw_test_set_active_value;
unsigned int open_cfw_test_close_transport_count;
unsigned int open_cfw_test_close_runtime_count;
unsigned int open_cfw_test_loop_count;
unsigned int open_cfw_test_driver_call_count;
unsigned int open_cfw_test_driver_offsets[16];

unsigned int open_cfw_test_dispatch_count;
unsigned int open_cfw_test_dispatch_service[16];
unsigned int open_cfw_test_dispatch_event[16];
unsigned int open_cfw_test_dispatch_arg1[16];
unsigned int open_cfw_test_dispatch_arg2[16];
unsigned int open_cfw_test_close_mode1_count;
unsigned int open_cfw_test_close_mode1_event;
unsigned int open_cfw_test_close_mode1_excluded;
unsigned int open_cfw_test_switch_count;
unsigned int open_cfw_test_switch_service;
unsigned int open_cfw_test_switch_arg1;
unsigned int open_cfw_test_switch_arg2;
unsigned int open_cfw_test_input_count;

unsigned int open_cfw_test_log_count;
unsigned int open_cfw_test_log_level[32];
unsigned int open_cfw_test_log_line[32];
unsigned long open_cfw_test_log_format[32];
unsigned int open_cfw_test_trace_count;
unsigned int open_cfw_test_trace_mask[32];
unsigned long open_cfw_test_trace_schema[32];

static void open_cfw_test_zero(void *destination, unsigned int length)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    for (index = 0U; index < length; ++index) {
        bytes[index] = 0U;
    }
}

static void open_cfw_test_u32(
    unsigned char *destination,
    unsigned int value
)
{
    destination[0] = (unsigned char)value;
    destination[1] = (unsigned char)(value >> 8);
    destination[2] = (unsigned char)(value >> 16);
    destination[3] = (unsigned char)(value >> 24);
}

void open_cfw_test_reset(void)
{
    unsigned int index;

    open_cfw_test_zero(open_cfw_test_state, sizeof(open_cfw_test_state));
    open_cfw_test_zero(open_cfw_test_message, sizeof(open_cfw_test_message));
    open_cfw_test_zero(
        open_cfw_test_queued_message,
        sizeof(open_cfw_test_queued_message)
    );
    open_cfw_test_zero(open_cfw_test_input, sizeof(open_cfw_test_input));
    open_cfw_test_background = 0U;
    open_cfw_test_mode = 0U;
    open_cfw_test_foreground = 0U;
    open_cfw_test_control = 0U;
    open_cfw_test_driver = (void *)0x1111UL;
    open_cfw_test_manager = (void *)0x2222UL;
    open_cfw_test_manager_create_result = (void *)0x5555UL;
    open_cfw_test_driver_ready = 1U;
    open_cfw_test_receive_result = 1;
    open_cfw_test_switch_result = 0U;
    open_cfw_test_input_result = 0U;
    open_cfw_test_log_flags_value = 0U;
    open_cfw_test_forced_state = 0xFFFFFFFFU;

    open_cfw_test_modules_initialize_count = 0U;
    open_cfw_test_runtime_initialize_count = 0U;
    open_cfw_test_before_count = 0U;
    open_cfw_test_after_count = 0U;
    open_cfw_test_receive_count = 0U;
    open_cfw_test_receive_control = 0U;
    open_cfw_test_mutex_take_count = 0U;
    open_cfw_test_mutex_give_count = 0U;
    open_cfw_test_extract_count = 0U;
    open_cfw_test_extract_token = 0U;
    open_cfw_test_start_prepare_count = 0U;
    open_cfw_test_start_transport_count = 0U;
    open_cfw_test_start_display_count = 0U;
    open_cfw_test_registry_reset_count = 0U;
    open_cfw_test_ui_initialize_count = 0U;
    open_cfw_test_manager_create_count = 0U;
    open_cfw_test_manager_configure_count = 0U;
    open_cfw_test_renderer_initialize_count = 0U;
    open_cfw_test_manager_commit_count = 0U;
    open_cfw_test_background_id_count = 0U;
    open_cfw_test_background_id = 0U;
    open_cfw_test_render_mode_count = 0U;
    open_cfw_test_render_mode = 0U;
    open_cfw_test_refresh_count = 0U;
    open_cfw_test_notify_count = 0U;
    open_cfw_test_update_power_count = 0U;
    open_cfw_test_manager_open_count = 0U;
    open_cfw_test_delay_count = 0U;
    open_cfw_test_delay_ticks = 0U;
    open_cfw_test_manager_destroy_count = 0U;
    open_cfw_test_manager_destroy_value = (void *)0;
    open_cfw_test_close_prepare_count = 0U;
    open_cfw_test_close_display_count = 0U;
    open_cfw_test_set_active_count = 0U;
    open_cfw_test_set_active_value = 0U;
    open_cfw_test_close_transport_count = 0U;
    open_cfw_test_close_runtime_count = 0U;
    open_cfw_test_loop_count = 0U;
    open_cfw_test_driver_call_count = 0U;
    open_cfw_test_dispatch_count = 0U;
    open_cfw_test_close_mode1_count = 0U;
    open_cfw_test_close_mode1_event = 0U;
    open_cfw_test_close_mode1_excluded = 0U;
    open_cfw_test_switch_count = 0U;
    open_cfw_test_switch_service = 0U;
    open_cfw_test_switch_arg1 = 0U;
    open_cfw_test_switch_arg2 = 0U;
    open_cfw_test_input_count = 0U;
    open_cfw_test_log_count = 0U;
    open_cfw_test_trace_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_driver_offsets[index] = 0U;
        open_cfw_test_dispatch_service[index] = 0U;
        open_cfw_test_dispatch_event[index] = 0U;
        open_cfw_test_dispatch_arg1[index] = 0U;
        open_cfw_test_dispatch_arg2[index] = 0U;
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_manager_open_operation[index] = 0U;
        open_cfw_test_manager_open_service[index] = 0U;
    }
    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_log_level[index] = 0U;
        open_cfw_test_log_line[index] = 0U;
        open_cfw_test_log_format[index] = 0U;
        open_cfw_test_trace_mask[index] = 0U;
        open_cfw_test_trace_schema[index] = 0U;
    }
}

void open_cfw_test_set_message(
    unsigned int command,
    unsigned int service,
    unsigned int token
)
{
    open_cfw_test_zero(
        open_cfw_test_queued_message,
        sizeof(open_cfw_test_queued_message)
    );
    open_cfw_test_queued_message[0] = (unsigned char)command;
    open_cfw_test_u32(open_cfw_test_queued_message + 4U, service);
    open_cfw_test_u32(open_cfw_test_queued_message + 8U, token);
    open_cfw_test_receive_result = 0;
}

void *open_cfw_test_fill(
    void *destination,
    unsigned int length,
    unsigned int value
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    for (index = 0U; index < length; ++index) {
        bytes[index] = (unsigned char)value;
    }
    return destination;
}

int open_cfw_test_receive(
    void *queue,
    void *message,
    unsigned int control
)
{
    unsigned int index;

    (void)queue;
    ++open_cfw_test_receive_count;
    open_cfw_test_receive_control = control;
    if (open_cfw_test_receive_result == 0) {
        for (index = 0U; index < 12U; ++index) {
            ((unsigned char *)message)[index] =
                open_cfw_test_queued_message[index];
        }
    }
    return open_cfw_test_receive_result;
}

void open_cfw_test_mutex_take(void *mutex)
{
    (void)mutex;
    ++open_cfw_test_mutex_take_count;
}

void open_cfw_test_mutex_give(void *mutex)
{
    (void)mutex;
    ++open_cfw_test_mutex_give_count;
}

void open_cfw_test_extract(void *destination, unsigned int token)
{
    ++open_cfw_test_extract_count;
    open_cfw_test_extract_token = token;
    ((unsigned char *)destination)[0] = 0xA5U;
}

void open_cfw_test_driver_call(void *driver, unsigned int offset)
{
    (void)driver;
    open_cfw_test_driver_offsets[open_cfw_test_driver_call_count++] = offset;
}

#define OPEN_CFW_TEST_VOID_ACTION(name) \
    void open_cfw_test_##name(void) \
    { \
        ++open_cfw_test_##name##_count; \
    }

OPEN_CFW_TEST_VOID_ACTION(runtime_initialize)
OPEN_CFW_TEST_VOID_ACTION(after)
OPEN_CFW_TEST_VOID_ACTION(start_prepare)
OPEN_CFW_TEST_VOID_ACTION(start_transport)
OPEN_CFW_TEST_VOID_ACTION(start_display)
OPEN_CFW_TEST_VOID_ACTION(registry_reset)
OPEN_CFW_TEST_VOID_ACTION(ui_initialize)
OPEN_CFW_TEST_VOID_ACTION(manager_configure)
OPEN_CFW_TEST_VOID_ACTION(renderer_initialize)
OPEN_CFW_TEST_VOID_ACTION(manager_commit)
OPEN_CFW_TEST_VOID_ACTION(refresh)
OPEN_CFW_TEST_VOID_ACTION(notify)
OPEN_CFW_TEST_VOID_ACTION(update_power)
OPEN_CFW_TEST_VOID_ACTION(close_prepare)
OPEN_CFW_TEST_VOID_ACTION(close_display)
OPEN_CFW_TEST_VOID_ACTION(close_transport)
OPEN_CFW_TEST_VOID_ACTION(close_runtime)

void open_cfw_test_before(void)
{
    ++open_cfw_test_before_count;
    if (open_cfw_test_forced_state != 0xFFFFFFFFU) {
        open_cfw_test_state[0] =
            (unsigned char)open_cfw_test_forced_state;
    }
}

void *open_cfw_test_manager_create(void)
{
    ++open_cfw_test_manager_create_count;
    return open_cfw_test_manager_create_result;
}

void open_cfw_test_set_background_id(unsigned int value)
{
    ++open_cfw_test_background_id_count;
    open_cfw_test_background_id = value;
}

void open_cfw_test_set_render_mode(unsigned int value)
{
    ++open_cfw_test_render_mode_count;
    open_cfw_test_render_mode = value;
}

unsigned int open_cfw_test_manager_open(
    void *manager,
    unsigned int operation,
    unsigned int service
)
{
    unsigned int index = open_cfw_test_manager_open_count++;

    (void)manager;
    open_cfw_test_manager_open_operation[index] = operation;
    open_cfw_test_manager_open_service[index] = service;
    return 0U;
}

void open_cfw_test_delay(unsigned int ticks)
{
    ++open_cfw_test_delay_count;
    open_cfw_test_delay_ticks = ticks;
}

void open_cfw_test_manager_destroy(void *manager)
{
    ++open_cfw_test_manager_destroy_count;
    open_cfw_test_manager_destroy_value = manager;
}

void open_cfw_test_set_active(unsigned int value)
{
    ++open_cfw_test_set_active_count;
    open_cfw_test_set_active_value = value;
}

unsigned int open_cfw_test_loop_continue(void)
{
    ++open_cfw_test_loop_count;
    return 0U;
}

unsigned int open_cfw_test_log_flags(void)
{
    return open_cfw_test_log_flags_value;
}

void open_cfw_test_log_record(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
)
{
    unsigned int index = open_cfw_test_log_count++;

    (void)module;
    (void)file;
    (void)tag;
    open_cfw_test_log_level[index] = level;
    open_cfw_test_log_line[index] = line;
    open_cfw_test_log_format[index] = (unsigned long)format;
}

void open_cfw_test_trace_record(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
)
{
    unsigned int index = open_cfw_test_trace_count++;

    (void)format;
    open_cfw_test_trace_mask[index] = mask;
    open_cfw_test_trace_schema[index] = (unsigned long)schema;
}

void open_cfw_ui_modules_initialize(void)
{
    ++open_cfw_test_modules_initialize_count;
}

unsigned int open_cfw_ui_module_dispatch_event(
    unsigned int service,
    unsigned int event,
    unsigned int arg1,
    unsigned int arg2
)
{
    unsigned int index = open_cfw_test_dispatch_count++;

    open_cfw_test_dispatch_service[index] = service;
    open_cfw_test_dispatch_event[index] = event;
    open_cfw_test_dispatch_arg1[index] = arg1;
    open_cfw_test_dispatch_arg2[index] = arg2;
    return service;
}

unsigned int open_cfw_ui_modules_close_mode1(
    unsigned int event,
    unsigned int excluded,
    unsigned int unused_arg2,
    unsigned int unused_arg3
)
{
    (void)unused_arg2;
    (void)unused_arg3;
    ++open_cfw_test_close_mode1_count;
    open_cfw_test_close_mode1_event = event;
    open_cfw_test_close_mode1_excluded = excluded;
    return 0U;
}

unsigned int open_cfw_ui_switch_display(
    unsigned int service,
    unsigned int arg1,
    unsigned int arg2
)
{
    ++open_cfw_test_switch_count;
    open_cfw_test_switch_service = service;
    open_cfw_test_switch_arg1 = arg1;
    open_cfw_test_switch_arg2 = arg2;
    return open_cfw_test_switch_result;
}

unsigned int open_cfw_ui_input_event_handler(const unsigned char *record)
{
    ++open_cfw_test_input_count;
    (void)record;
    return open_cfw_test_input_result;
}

#define OPEN_CFW_UI_THREAD_DRIVER open_cfw_test_driver
#define OPEN_CFW_UI_THREAD_MANAGER open_cfw_test_manager
#define OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE open_cfw_test_background
#define OPEN_CFW_UI_THREAD_DISPLAY_MODE open_cfw_test_mode
#define OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE open_cfw_test_foreground
#define OPEN_CFW_UI_THREAD_QUEUE open_cfw_test_queue
#define OPEN_CFW_UI_THREAD_MUTEX open_cfw_test_mutex
#define OPEN_CFW_UI_THREAD_STATE open_cfw_test_state[0]
#define OPEN_CFW_UI_THREAD_CONTROL open_cfw_test_control
#define OPEN_CFW_UI_THREAD_MESSAGE open_cfw_test_message
#define OPEN_CFW_UI_THREAD_INPUT_BUFFER open_cfw_test_input
#define OPEN_CFW_UI_THREAD_DRIVER_READY(driver) \
    (open_cfw_test_driver_ready + (unsigned int)((driver) == (void *)0))
#define OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, offset) \
    open_cfw_test_driver_call((driver), (offset))
#define OPEN_CFW_UI_THREAD_FILL(destination, length, value) \
    open_cfw_test_fill((destination), (length), (value))
#define OPEN_CFW_UI_THREAD_RECEIVE(queue, message, control) \
    open_cfw_test_receive((queue), (message), (control))
#define OPEN_CFW_UI_THREAD_MUTEX_TAKE(mutex) open_cfw_test_mutex_take(mutex)
#define OPEN_CFW_UI_THREAD_MUTEX_GIVE(mutex) open_cfw_test_mutex_give(mutex)
#define OPEN_CFW_UI_THREAD_EXTRACT_INPUT(destination, token) \
    open_cfw_test_extract((destination), (token))
#define OPEN_CFW_UI_THREAD_RUNTIME_INITIALIZE() \
    open_cfw_test_runtime_initialize()
#define OPEN_CFW_UI_THREAD_BEFORE_COMMAND() open_cfw_test_before()
#define OPEN_CFW_UI_THREAD_AFTER_COMMAND() open_cfw_test_after()
#define OPEN_CFW_UI_THREAD_START_PREPARE() open_cfw_test_start_prepare()
#define OPEN_CFW_UI_THREAD_START_TRANSPORT() open_cfw_test_start_transport()
#define OPEN_CFW_UI_THREAD_START_DISPLAY() open_cfw_test_start_display()
#define OPEN_CFW_UI_THREAD_REGISTRY_RESET() open_cfw_test_registry_reset()
#define OPEN_CFW_UI_THREAD_UI_INITIALIZE() open_cfw_test_ui_initialize()
#define OPEN_CFW_UI_THREAD_MANAGER_CREATE() open_cfw_test_manager_create()
#define OPEN_CFW_UI_THREAD_MANAGER_CONFIGURE() \
    open_cfw_test_manager_configure()
#define OPEN_CFW_UI_THREAD_RENDERER_INITIALIZE() \
    open_cfw_test_renderer_initialize()
#define OPEN_CFW_UI_THREAD_MANAGER_COMMIT() open_cfw_test_manager_commit()
#define OPEN_CFW_UI_THREAD_SET_BACKGROUND_ID(value) \
    open_cfw_test_set_background_id(value)
#define OPEN_CFW_UI_THREAD_SET_RENDER_MODE(value) \
    open_cfw_test_set_render_mode(value)
#define OPEN_CFW_UI_THREAD_REFRESH() open_cfw_test_refresh()
#define OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION() open_cfw_test_notify()
#define OPEN_CFW_UI_THREAD_UPDATE_POWER() open_cfw_test_update_power()
#define OPEN_CFW_UI_THREAD_MANAGER_OPEN(manager, operation, service) \
    open_cfw_test_manager_open((manager), (operation), (service))
#define OPEN_CFW_UI_THREAD_DELAY(ticks) open_cfw_test_delay(ticks)
#define OPEN_CFW_UI_THREAD_MANAGER_DESTROY(manager) \
    open_cfw_test_manager_destroy(manager)
#define OPEN_CFW_UI_THREAD_CLOSE_PREPARE() open_cfw_test_close_prepare()
#define OPEN_CFW_UI_THREAD_CLOSE_DISPLAY() open_cfw_test_close_display()
#define OPEN_CFW_UI_THREAD_SET_ACTIVE(value) open_cfw_test_set_active(value)
#define OPEN_CFW_UI_THREAD_CLOSE_TRANSPORT() open_cfw_test_close_transport()
#define OPEN_CFW_UI_THREAD_CLOSE_RUNTIME() open_cfw_test_close_runtime()
#define OPEN_CFW_UI_THREAD_LOOP_CONTINUE() open_cfw_test_loop_continue()
#define OPEN_CFW_UI_THREAD_LOG_FLAGS open_cfw_test_log_flags
#define OPEN_CFW_UI_THREAD_LOG_RECORD open_cfw_test_log_record
#define OPEN_CFW_UI_THREAD_TRACE_RECORD open_cfw_test_trace_record

#include "../../components/apollo_main/core_overlay/ui_display_thread.c"
