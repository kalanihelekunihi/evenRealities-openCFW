#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

union open_cfw_test_state_union {
    unsigned char bytes[16];
    unsigned int words[4];
};

union open_cfw_test_state_union open_cfw_test_state;
void *open_cfw_test_manager = (void *)(uintptr_t)0x12345678U;
unsigned int open_cfw_test_state_present = 1U;
unsigned int open_cfw_test_stage;
unsigned int open_cfw_test_current_service;
unsigned int open_cfw_test_post_result;
unsigned int open_cfw_test_post_count;
unsigned int open_cfw_test_post_event[8];
unsigned long open_cfw_test_post_data[8];
unsigned int open_cfw_test_post_value[8];
unsigned int open_cfw_test_onboarding_result;
unsigned int open_cfw_test_onboarding_count;
unsigned int open_cfw_test_terminal_result;
unsigned int open_cfw_test_terminal_count;
unsigned int open_cfw_test_longpress_count;
unsigned int open_cfw_test_lens_result;
unsigned int open_cfw_test_lens_count;
unsigned int open_cfw_test_system_count;
unsigned int open_cfw_test_system_args[4];
unsigned int open_cfw_test_mode3_reset_count;
unsigned int open_cfw_test_mode_handle_result;
unsigned int open_cfw_test_mode_handle_count;
unsigned int open_cfw_test_mode_handle_mode[2];
unsigned int open_cfw_test_mode_active_result;
unsigned int open_cfw_test_mode_active_count;
unsigned int open_cfw_test_mode_active_handle[2];
unsigned int open_cfw_test_dispatch_count;
unsigned int open_cfw_test_dispatch_args[4];
unsigned int open_cfw_test_ring_count;
unsigned int open_cfw_test_ring_event;
int open_cfw_test_ring_coordinates[2];
unsigned int open_cfw_test_x_value;
unsigned int open_cfw_test_x_set_count;
unsigned int open_cfw_test_x_apply_count;
unsigned int open_cfw_test_y_value;
unsigned int open_cfw_test_y_set_count;
unsigned int open_cfw_test_y_apply_count;
unsigned int open_cfw_test_log_flags_value;
unsigned int open_cfw_test_log_count;
unsigned int open_cfw_test_log_level[8];
unsigned int open_cfw_test_log_line[8];
unsigned long open_cfw_test_log_format[8];
unsigned int open_cfw_test_trace_count;
unsigned int open_cfw_test_trace_mask[8];
unsigned long open_cfw_test_trace_schema[8];

int *open_cfw_test_current_state(void *manager)
{
    (void)manager;
    if (open_cfw_test_state_present == 0U) {
        return (int *)0;
    }
    return (int *)(void *)open_cfw_test_state.bytes;
}

int open_cfw_test_post(
    void *manager,
    unsigned int event,
    const void *data
)
{
    unsigned int index = open_cfw_test_post_count++;

    (void)manager;
    open_cfw_test_post_event[index] = event;
    open_cfw_test_post_data[index] = (unsigned long)data;
    if ((uintptr_t)data > 0x1000U) {
        open_cfw_test_post_value[index] =
            *(const unsigned int *)data;
    }
    return (int)open_cfw_test_post_result;
}

unsigned int open_cfw_test_onboarding(void)
{
    ++open_cfw_test_onboarding_count;
    return open_cfw_test_onboarding_result;
}

unsigned int open_cfw_test_terminal(void)
{
    ++open_cfw_test_terminal_count;
    return open_cfw_test_terminal_result;
}

void open_cfw_test_longpress(void)
{
    ++open_cfw_test_longpress_count;
}

unsigned int open_cfw_test_lens_side(void)
{
    ++open_cfw_test_lens_count;
    return open_cfw_test_lens_result;
}

void open_cfw_test_system_event(
    unsigned int first,
    unsigned int second,
    unsigned int third,
    unsigned int fourth
)
{
    ++open_cfw_test_system_count;
    open_cfw_test_system_args[0] = first;
    open_cfw_test_system_args[1] = second;
    open_cfw_test_system_args[2] = third;
    open_cfw_test_system_args[3] = fourth;
}

void open_cfw_test_mode3_reset(void)
{
    ++open_cfw_test_mode3_reset_count;
}

unsigned int open_cfw_test_mode_handle(
    void *manager,
    unsigned int mode
)
{
    unsigned int index = open_cfw_test_mode_handle_count++;

    (void)manager;
    open_cfw_test_mode_handle_mode[index] = mode;
    return open_cfw_test_mode_handle_result;
}

unsigned int open_cfw_test_mode_active(
    void *manager,
    unsigned int handle
)
{
    unsigned int index = open_cfw_test_mode_active_count++;

    (void)manager;
    open_cfw_test_mode_active_handle[index] = handle;
    return open_cfw_test_mode_active_result;
}

unsigned int open_cfw_test_dispatch(
    unsigned int service,
    unsigned int event,
    unsigned int arg1,
    unsigned int arg2
)
{
    ++open_cfw_test_dispatch_count;
    open_cfw_test_dispatch_args[0] = service;
    open_cfw_test_dispatch_args[1] = event;
    open_cfw_test_dispatch_args[2] = arg1;
    open_cfw_test_dispatch_args[3] = arg2;
    return 0U;
}

int open_cfw_test_ring_release(
    void *manager,
    int event,
    void *data
)
{
    int *coordinates = (int *)data;

    (void)manager;
    ++open_cfw_test_ring_count;
    open_cfw_test_ring_event = (unsigned int)event;
    open_cfw_test_ring_coordinates[0] = coordinates[0];
    open_cfw_test_ring_coordinates[1] = coordinates[1];
    return 0;
}

void open_cfw_test_set_x(unsigned int value)
{
    ++open_cfw_test_x_set_count;
    open_cfw_test_x_value = value;
}

void open_cfw_test_apply_x(void)
{
    ++open_cfw_test_x_apply_count;
}

void open_cfw_test_set_y(unsigned int value)
{
    ++open_cfw_test_y_set_count;
    open_cfw_test_y_value = value;
}

void open_cfw_test_apply_y(void)
{
    ++open_cfw_test_y_apply_count;
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

#define OPEN_CFW_UI_INPUT_MANAGER open_cfw_test_manager
#define OPEN_CFW_UI_INPUT_STAGE open_cfw_test_stage
#define OPEN_CFW_UI_INPUT_CURRENT_SERVICE open_cfw_test_current_service
#define OPEN_CFW_UI_INPUT_CURRENT_STATE(manager) \
    open_cfw_test_current_state(manager)
#define OPEN_CFW_UI_INPUT_POST(manager, event, data) \
    open_cfw_test_post(manager, event, data)
#define OPEN_CFW_UI_INPUT_TERMINAL_MODE() open_cfw_test_terminal()
#define OPEN_CFW_UI_INPUT_MODE3_RESET() open_cfw_test_mode3_reset()
#define OPEN_CFW_UI_INPUT_MODE_HANDLE(manager, mode) \
    open_cfw_test_mode_handle(manager, mode)
#define OPEN_CFW_UI_INPUT_MODE_ACTIVE(manager, handle) \
    open_cfw_test_mode_active(manager, handle)
#define OPEN_CFW_UI_INPUT_SEND_SYSTEM_EVENT(a, b, c, d) \
    open_cfw_test_system_event(a, b, c, d)
#define OPEN_CFW_UI_INPUT_SET_Y(value) open_cfw_test_set_y(value)
#define OPEN_CFW_UI_INPUT_APPLY_Y() open_cfw_test_apply_y()
#define OPEN_CFW_UI_INPUT_SET_X(value) open_cfw_test_set_x(value)
#define OPEN_CFW_UI_INPUT_APPLY_X() open_cfw_test_apply_x()
#define OPEN_CFW_UI_INPUT_ONBOARDING_RUNNING() \
    open_cfw_test_onboarding()
#define OPEN_CFW_UI_INPUT_LONGPRESS() open_cfw_test_longpress()
#define OPEN_CFW_UI_INPUT_RING_RELEASE(manager, event, data) \
    open_cfw_test_ring_release(manager, event, data)
#define OPEN_CFW_UI_INPUT_LENS_SIDE() open_cfw_test_lens_side()
#define OPEN_CFW_UI_INPUT_DISPATCH_EVENT(service, event, arg1, arg2) \
    open_cfw_test_dispatch(service, event, arg1, arg2)
#define OPEN_CFW_UI_INPUT_LOG_FLAGS open_cfw_test_log_flags
#define OPEN_CFW_UI_INPUT_LOG_RECORD open_cfw_test_log_record
#define OPEN_CFW_UI_INPUT_TRACE_RECORD open_cfw_test_trace_record

#include "../../components/apollo_main/core_overlay/ui_input_event.c"
