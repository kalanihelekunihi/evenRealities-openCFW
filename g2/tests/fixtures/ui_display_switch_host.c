#define OPEN_CFW_UI_SWITCH_EVENT_ARG_TYPE unsigned long

unsigned int open_cfw_test_terminal_mode;
unsigned int open_cfw_test_terminal_count;
unsigned char open_cfw_test_active_state[16];
unsigned char open_cfw_test_primary_state[8];
void *open_cfw_test_active_pointer;
void *open_cfw_test_display_manager;
unsigned int open_cfw_test_current_service;
unsigned int open_cfw_test_target_mode;
unsigned int open_cfw_test_mode_count;
unsigned int open_cfw_test_mode_service;
unsigned int open_cfw_test_open_count;
unsigned int open_cfw_test_open_operation[4];
unsigned int open_cfw_test_open_service[4];
unsigned int open_cfw_test_open_result[4];
unsigned int open_cfw_test_primary_count;
unsigned int open_cfw_test_lookup_count;
unsigned int open_cfw_test_lookup_service[4];
unsigned long open_cfw_test_lookup_entry[4];
unsigned int open_cfw_test_is_active_count;
unsigned long open_cfw_test_is_active_entry[4];
unsigned int open_cfw_test_is_active_result[4];
unsigned int open_cfw_test_cancel_count;
unsigned int open_cfw_test_cancel_handle;
unsigned int open_cfw_test_cancel_timeout;
unsigned int open_cfw_test_poll_count;
unsigned int open_cfw_test_delay_count;
unsigned int open_cfw_test_delay_ticks;
unsigned int open_cfw_test_lens_side;
unsigned int open_cfw_test_lens_count;
unsigned int open_cfw_test_close_count;
unsigned int open_cfw_test_close_args[4];
unsigned int open_cfw_test_start_count;
unsigned int open_cfw_test_start_args[4];
unsigned int open_cfw_test_replace_count;
unsigned int open_cfw_test_replace_args[4];
unsigned int open_cfw_test_resource_size_count;
unsigned long open_cfw_test_resource_size_pointer;
unsigned int open_cfw_test_resource_size_value;
unsigned int open_cfw_test_resource_prepare_count;
unsigned long open_cfw_test_resource_prepare_pointer;
unsigned int open_cfw_test_resource_prepare_size;
int open_cfw_test_resource_result_value;
unsigned int open_cfw_test_fill_count;
unsigned int open_cfw_test_fill_length[2];
unsigned int open_cfw_test_fill_value[2];
unsigned int open_cfw_test_dispatch_count;
unsigned int open_cfw_test_dispatch_service;
unsigned int open_cfw_test_dispatch_event;
unsigned int open_cfw_test_dispatch_length;
unsigned char open_cfw_test_dispatch_packet[6];
unsigned int open_cfw_test_log_flags_value;
unsigned int open_cfw_test_log_count;
unsigned int open_cfw_test_log_level;
unsigned int open_cfw_test_log_line;
unsigned long open_cfw_test_log_format;
unsigned int open_cfw_test_trace_count;
unsigned int open_cfw_test_trace_mask;
unsigned long open_cfw_test_trace_schema;

static unsigned int open_cfw_test_word(const unsigned char *bytes)
{
    return
        (unsigned int)bytes[0] |
        ((unsigned int)bytes[1] << 8) |
        ((unsigned int)bytes[2] << 16) |
        ((unsigned int)bytes[3] << 24);
}

void open_cfw_test_set_active(
    unsigned int service_id,
    unsigned int mode
)
{
    open_cfw_test_active_state[0] = (unsigned char)service_id;
    open_cfw_test_active_state[1] = (unsigned char)(service_id >> 8);
    open_cfw_test_active_state[2] = (unsigned char)(service_id >> 16);
    open_cfw_test_active_state[3] = (unsigned char)(service_id >> 24);
    open_cfw_test_active_state[11] = (unsigned char)mode;
    open_cfw_test_active_pointer = open_cfw_test_active_state;
}

void open_cfw_test_set_primary(
    unsigned int service_id,
    unsigned int handle
)
{
    unsigned int index;

    for (index = 0; index < 4; ++index) {
        open_cfw_test_primary_state[index] =
            (unsigned char)(service_id >> (index * 8));
        open_cfw_test_primary_state[index + 4] =
            (unsigned char)(handle >> (index * 8));
    }
}

unsigned int open_cfw_test_terminal(void)
{
    ++open_cfw_test_terminal_count;
    return open_cfw_test_terminal_mode;
}

void *open_cfw_test_active(void *display_manager)
{
    (void)display_manager;
    return open_cfw_test_active_pointer;
}

unsigned int open_cfw_test_mode(unsigned int service_id)
{
    ++open_cfw_test_mode_count;
    open_cfw_test_mode_service = service_id;
    return open_cfw_test_target_mode;
}

unsigned int open_cfw_test_open(
    void *display_manager,
    unsigned int operation,
    unsigned int service_id
)
{
    unsigned int index = open_cfw_test_open_count++;

    (void)display_manager;
    open_cfw_test_open_operation[index] = operation;
    open_cfw_test_open_service[index] = service_id;
    return open_cfw_test_open_result[index];
}

void *open_cfw_test_primary(void *display_manager)
{
    (void)display_manager;
    ++open_cfw_test_primary_count;
    return open_cfw_test_primary_state;
}

unsigned long open_cfw_test_lookup(
    void *display_manager,
    unsigned int service_id
)
{
    unsigned int index = open_cfw_test_lookup_count++;

    (void)display_manager;
    open_cfw_test_lookup_service[index] = service_id;
    open_cfw_test_lookup_entry[index] = 0x10000000UL + service_id;
    return open_cfw_test_lookup_entry[index];
}

unsigned int open_cfw_test_is_active(
    void *display_manager,
    unsigned long entry
)
{
    unsigned int index = open_cfw_test_is_active_count++;

    (void)display_manager;
    open_cfw_test_is_active_entry[index] = entry;
    return open_cfw_test_is_active_result[index];
}

void open_cfw_test_cancel(unsigned int handle, unsigned int timeout)
{
    ++open_cfw_test_cancel_count;
    open_cfw_test_cancel_handle = handle;
    open_cfw_test_cancel_timeout = timeout;
}

void open_cfw_test_poll(void)
{
    ++open_cfw_test_poll_count;
}

void open_cfw_test_delay(unsigned int ticks)
{
    ++open_cfw_test_delay_count;
    open_cfw_test_delay_ticks = ticks;
}

unsigned int open_cfw_lens_side(void)
{
    ++open_cfw_test_lens_count;
    return open_cfw_test_lens_side;
}

void open_cfw_test_close(
    unsigned int arg0,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
)
{
    ++open_cfw_test_close_count;
    open_cfw_test_close_args[0] = arg0;
    open_cfw_test_close_args[1] = arg1;
    open_cfw_test_close_args[2] = arg2;
    open_cfw_test_close_args[3] = arg3;
}

void open_cfw_test_start(
    unsigned int arg0,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
)
{
    ++open_cfw_test_start_count;
    open_cfw_test_start_args[0] = arg0;
    open_cfw_test_start_args[1] = arg1;
    open_cfw_test_start_args[2] = arg2;
    open_cfw_test_start_args[3] = arg3;
}

void open_cfw_test_replace(
    unsigned int arg0,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
)
{
    ++open_cfw_test_replace_count;
    open_cfw_test_replace_args[0] = arg0;
    open_cfw_test_replace_args[1] = arg1;
    open_cfw_test_replace_args[2] = arg2;
    open_cfw_test_replace_args[3] = arg3;
}

unsigned int open_cfw_test_resource_size(const void *resource)
{
    ++open_cfw_test_resource_size_count;
    open_cfw_test_resource_size_pointer = (unsigned long)resource;
    return open_cfw_test_resource_size_value;
}

void open_cfw_test_resource_prepare(
    const void *resource,
    unsigned int size
)
{
    ++open_cfw_test_resource_prepare_count;
    open_cfw_test_resource_prepare_pointer = (unsigned long)resource;
    open_cfw_test_resource_prepare_size = size;
}

int open_cfw_test_resource_result(void)
{
    return open_cfw_test_resource_result_value;
}

void *open_cfw_test_fill(
    void *destination,
    unsigned int length,
    unsigned int value
)
{
    unsigned int call = open_cfw_test_fill_count++;
    unsigned int index;
    unsigned char *bytes = destination;

    open_cfw_test_fill_length[call] = length;
    open_cfw_test_fill_value[call] = value;
    for (index = 0; index < length; ++index) {
        bytes[index] = (unsigned char)value;
    }
    return destination;
}

unsigned int open_cfw_ui_module_dispatch_event(
    unsigned int service_id,
    unsigned int event,
    OPEN_CFW_UI_SWITCH_EVENT_ARG_TYPE arg1,
    unsigned int arg2
)
{
    unsigned int index;
    const unsigned char *packet =
        (const unsigned char *)arg1;

    ++open_cfw_test_dispatch_count;
    open_cfw_test_dispatch_service = service_id;
    open_cfw_test_dispatch_event = event;
    open_cfw_test_dispatch_length = arg2;
    if (packet != (const unsigned char *)0 && arg2 == 6) {
        for (index = 0; index < 6; ++index) {
            open_cfw_test_dispatch_packet[index] = packet[index];
        }
    }
    return service_id;
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
    (void)module;
    (void)file;
    (void)tag;
    ++open_cfw_test_log_count;
    open_cfw_test_log_level = level;
    open_cfw_test_log_line = line;
    open_cfw_test_log_format = (unsigned long)format;
}

void open_cfw_test_trace_record(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
)
{
    (void)format;
    ++open_cfw_test_trace_count;
    open_cfw_test_trace_mask = mask;
    open_cfw_test_trace_schema = (unsigned long)schema;
}

#define OPEN_CFW_UI_SWITCH_DISPLAY_MANAGER open_cfw_test_display_manager
#define OPEN_CFW_UI_SWITCH_CURRENT_SERVICE open_cfw_test_current_service
#define OPEN_CFW_UI_SWITCH_TERMINAL_MODE() open_cfw_test_terminal()
#define OPEN_CFW_UI_SWITCH_ACTIVE_STATE(manager) open_cfw_test_active(manager)
#define OPEN_CFW_UI_SWITCH_OPEN(manager, operation, service) \
    open_cfw_test_open(manager, operation, service)
#define OPEN_CFW_UI_SWITCH_PRIMARY_STATE(manager) open_cfw_test_primary(manager)
#define OPEN_CFW_UI_SWITCH_LOOKUP(manager, service) \
    open_cfw_test_lookup(manager, service)
#define OPEN_CFW_UI_SWITCH_IS_ACTIVE(manager, entry) \
    open_cfw_test_is_active(manager, entry)
#define OPEN_CFW_UI_SWITCH_CANCEL(handle, timeout) \
    open_cfw_test_cancel(handle, timeout)
#define OPEN_CFW_UI_SWITCH_POLL() open_cfw_test_poll()
#define OPEN_CFW_UI_SWITCH_DELAY(ticks) open_cfw_test_delay(ticks)
#define OPEN_CFW_UI_SWITCH_CLOSE_MODE(arg0, arg1, arg2, arg3) \
    open_cfw_test_close(arg0, arg1, arg2, arg3)
#define OPEN_CFW_UI_SWITCH_START_MODE0(arg0, arg1, arg2, arg3) \
    open_cfw_test_start(arg0, arg1, arg2, arg3)
#define OPEN_CFW_UI_SWITCH_REPLACE_MODE0(arg0, arg1, arg2, arg3) \
    open_cfw_test_replace(arg0, arg1, arg2, arg3)
#define OPEN_CFW_UI_SWITCH_RESOURCE_SIZE(resource) \
    open_cfw_test_resource_size(resource)
#define OPEN_CFW_UI_SWITCH_RESOURCE_PREPARE(resource, size) \
    open_cfw_test_resource_prepare(resource, size)
#define OPEN_CFW_UI_SWITCH_RESOURCE_RESULT() \
    open_cfw_test_resource_result()
#define OPEN_CFW_UI_SWITCH_FILL(destination, length, value) \
    open_cfw_test_fill(destination, length, value)
#define OPEN_CFW_UI_SWITCH_LOG_FLAGS open_cfw_test_log_flags
#define OPEN_CFW_UI_SWITCH_LOG_RECORD open_cfw_test_log_record
#define OPEN_CFW_UI_SWITCH_TRACE_RECORD open_cfw_test_trace_record
#define open_cfw_ui_module_mode open_cfw_test_mode

#include "../../components/apollo_main/core_overlay/ui_display_switch.c"

unsigned int open_cfw_test_active_service(void)
{
    return open_cfw_test_word(open_cfw_test_active_state);
}
