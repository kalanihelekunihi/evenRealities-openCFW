#include <stddef.h>

void *open_cfw_test_driver;
void *open_cfw_test_queue;
void *open_cfw_test_mutex;
void *open_cfw_test_driver_result;
void *open_cfw_test_queue_result;
void *open_cfw_test_mutex_result;
unsigned int open_cfw_test_ring_result;
unsigned int open_cfw_test_log_flags_value;

unsigned int open_cfw_test_order_count;
unsigned int open_cfw_test_order[16];
unsigned int open_cfw_test_queue_storage_size;
unsigned int open_cfw_test_queue_item_size;
unsigned int open_cfw_test_queue_configuration[6];
void *open_cfw_test_ring_descriptor;
void *open_cfw_test_ring_storage;
unsigned int open_cfw_test_ring_capacity;
unsigned int open_cfw_test_mutex_attributes;
void *open_cfw_test_registered_entry;
void *open_cfw_test_registered_context;
unsigned int open_cfw_test_thread_configuration[9];
unsigned int open_cfw_test_thread_call_count;

unsigned int open_cfw_test_log_count;
unsigned int open_cfw_test_log_level[4];
unsigned int open_cfw_test_log_line[4];
unsigned long open_cfw_test_log_module[4];
unsigned long open_cfw_test_log_file[4];
unsigned long open_cfw_test_log_tag[4];
unsigned long open_cfw_test_log_format[4];
unsigned int open_cfw_test_trace_count;
unsigned int open_cfw_test_trace_mask[4];
unsigned long open_cfw_test_trace_schema[4];

static void open_cfw_test_zero(
    void *destination,
    unsigned int length
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    for (index = 0U; index < length; ++index) {
        bytes[index] = 0U;
    }
}

static void open_cfw_test_record_order(unsigned int value)
{
    open_cfw_test_order[open_cfw_test_order_count++] = value;
}

void open_cfw_test_reset(void)
{
    open_cfw_test_driver = (void *)0;
    open_cfw_test_queue = (void *)0;
    open_cfw_test_mutex = (void *)0;
    open_cfw_test_driver_result = (void *)0x1111UL;
    open_cfw_test_queue_result = (void *)0x2222UL;
    open_cfw_test_mutex_result = (void *)0x3333UL;
    open_cfw_test_ring_result = 1U;
    open_cfw_test_log_flags_value = 0U;

    open_cfw_test_order_count = 0U;
    open_cfw_test_queue_storage_size = 0U;
    open_cfw_test_queue_item_size = 0U;
    open_cfw_test_ring_descriptor = (void *)0;
    open_cfw_test_ring_storage = (void *)0;
    open_cfw_test_ring_capacity = 0U;
    open_cfw_test_mutex_attributes = 0U;
    open_cfw_test_registered_entry = (void *)0;
    open_cfw_test_registered_context = (void *)1;
    open_cfw_test_thread_call_count = 0U;
    open_cfw_test_log_count = 0U;
    open_cfw_test_trace_count = 0U;

    open_cfw_test_zero(
        open_cfw_test_order,
        sizeof(open_cfw_test_order)
    );
    open_cfw_test_zero(
        open_cfw_test_queue_configuration,
        sizeof(open_cfw_test_queue_configuration)
    );
    open_cfw_test_zero(
        open_cfw_test_thread_configuration,
        sizeof(open_cfw_test_thread_configuration)
    );
    open_cfw_test_zero(
        open_cfw_test_log_level,
        sizeof(open_cfw_test_log_level)
    );
    open_cfw_test_zero(
        open_cfw_test_log_line,
        sizeof(open_cfw_test_log_line)
    );
    open_cfw_test_zero(
        open_cfw_test_log_module,
        sizeof(open_cfw_test_log_module)
    );
    open_cfw_test_zero(
        open_cfw_test_log_file,
        sizeof(open_cfw_test_log_file)
    );
    open_cfw_test_zero(
        open_cfw_test_log_tag,
        sizeof(open_cfw_test_log_tag)
    );
    open_cfw_test_zero(
        open_cfw_test_log_format,
        sizeof(open_cfw_test_log_format)
    );
    open_cfw_test_zero(
        open_cfw_test_trace_mask,
        sizeof(open_cfw_test_trace_mask)
    );
    open_cfw_test_zero(
        open_cfw_test_trace_schema,
        sizeof(open_cfw_test_trace_schema)
    );
}

void *open_cfw_test_get_driver(void)
{
    open_cfw_test_record_order(1U);
    return open_cfw_test_driver_result;
}

void open_cfw_test_prepare_display(void)
{
    open_cfw_test_record_order(2U);
}

void open_cfw_test_prepare_input(void)
{
    open_cfw_test_record_order(3U);
}

void *open_cfw_test_queue_create(
    unsigned int storage_size,
    unsigned int item_size,
    const void *configuration
)
{
    const unsigned int *words = (const unsigned int *)configuration;
    unsigned int index;

    open_cfw_test_record_order(4U);
    open_cfw_test_queue_storage_size = storage_size;
    open_cfw_test_queue_item_size = item_size;
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_queue_configuration[index] = words[index];
    }
    return open_cfw_test_queue_result;
}

unsigned int open_cfw_test_ring_initialize(
    void *descriptor,
    void *storage,
    unsigned int capacity
)
{
    open_cfw_test_record_order(5U);
    open_cfw_test_ring_descriptor = descriptor;
    open_cfw_test_ring_storage = storage;
    open_cfw_test_ring_capacity = capacity;
    return open_cfw_test_ring_result;
}

void *open_cfw_test_mutex_create(unsigned int attributes)
{
    open_cfw_test_record_order(6U);
    open_cfw_test_mutex_attributes = attributes;
    return open_cfw_test_mutex_result;
}

void open_cfw_ui_display_thread(void *context)
{
    (void)context;
    ++open_cfw_test_thread_call_count;
}

void open_cfw_test_register_thread(
    void (*entry)(void *context),
    void *context,
    const void *configuration
)
{
    const unsigned int *words = (const unsigned int *)configuration;
    unsigned int index;

    open_cfw_test_record_order(7U);
    open_cfw_test_registered_entry = (void *)entry;
    open_cfw_test_registered_context = context;
    for (index = 0U; index < 9U; ++index) {
        open_cfw_test_thread_configuration[index] = words[index];
    }
}

unsigned long open_cfw_test_display_thread_address(void)
{
    return (unsigned long)open_cfw_ui_display_thread;
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

    open_cfw_test_log_level[index] = level;
    open_cfw_test_log_line[index] = line;
    open_cfw_test_log_module[index] = (unsigned long)module;
    open_cfw_test_log_file[index] = (unsigned long)file;
    open_cfw_test_log_tag[index] = (unsigned long)tag;
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

#define OPEN_CFW_UI_INITIALIZER_DRIVER open_cfw_test_driver
#define OPEN_CFW_UI_INITIALIZER_QUEUE open_cfw_test_queue
#define OPEN_CFW_UI_INITIALIZER_MUTEX open_cfw_test_mutex
#define OPEN_CFW_UI_INITIALIZER_RING_DESCRIPTOR ((void *)0x4444UL)
#define OPEN_CFW_UI_INITIALIZER_RING_STORAGE ((void *)0x5555UL)
#define OPEN_CFW_UI_INITIALIZER_GET_DRIVER() open_cfw_test_get_driver()
#define OPEN_CFW_UI_INITIALIZER_PREPARE_DISPLAY() \
    open_cfw_test_prepare_display()
#define OPEN_CFW_UI_INITIALIZER_PREPARE_INPUT() open_cfw_test_prepare_input()
#define OPEN_CFW_UI_INITIALIZER_QUEUE_CREATE( \
    storage_size, \
    item_size, \
    configuration \
) \
    open_cfw_test_queue_create( \
        (storage_size), \
        (item_size), \
        (configuration) \
    )
#define OPEN_CFW_UI_INITIALIZER_RING_INITIALIZE( \
    descriptor, \
    storage, \
    capacity \
) \
    open_cfw_test_ring_initialize((descriptor), (storage), (capacity))
#define OPEN_CFW_UI_INITIALIZER_MUTEX_CREATE(attributes) \
    open_cfw_test_mutex_create(attributes)
#define OPEN_CFW_UI_INITIALIZER_REGISTER_THREAD( \
    entry, \
    context, \
    configuration \
) \
    open_cfw_test_register_thread((entry), (context), (configuration))
#define OPEN_CFW_UI_INITIALIZER_LOG_FLAGS open_cfw_test_log_flags
#define OPEN_CFW_UI_INITIALIZER_LOG_RECORD open_cfw_test_log_record
#define OPEN_CFW_UI_INITIALIZER_TRACE_RECORD open_cfw_test_trace_record

#include "../../components/apollo_main/core_overlay/ui_display_initializer.c"
