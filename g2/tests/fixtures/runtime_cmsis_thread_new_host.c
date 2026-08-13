#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/runtime_cmsis_thread_new.c"

static uint32_t host_irq;
static int32_t host_dynamic_result;
static void *host_dynamic_task;
static void *host_static_task;
static size_t host_dynamic_calls, host_static_calls;
static open_cfw_cmsis_thread_new_function host_function;
static const char *host_name;
static uint32_t host_stack_depth, host_priority;
static void *host_argument, *host_stack_memory, *host_control_block_memory;

uint32_t open_cfw_cmsis_irq_context(void) { return host_irq; }

void *open_cfw_retained_freertos_task_create_static(
    open_cfw_cmsis_thread_new_function function, const char *name,
    uint32_t stack_depth, void *argument, uint32_t priority,
    void *stack_memory, void *control_block_memory
)
{
    ++host_static_calls;
    host_function = function; host_name = name; host_stack_depth = stack_depth;
    host_argument = argument; host_priority = priority;
    host_stack_memory = stack_memory;
    host_control_block_memory = control_block_memory;
    return host_static_task;
}

int32_t open_cfw_retained_freertos_task_create(
    open_cfw_cmsis_thread_new_function function, const char *name,
    uint16_t stack_depth, void *argument, uint32_t priority,
    void **created_task
)
{
    ++host_dynamic_calls;
    host_function = function; host_name = name; host_stack_depth = stack_depth;
    host_argument = argument; host_priority = priority;
    *created_task = host_dynamic_task;
    return host_dynamic_result;
}

static void host_thread(void *argument) { (void)argument; }

void open_cfw_thread_new_host_reset(void)
{
    host_irq = 0; host_dynamic_result = 1;
    host_dynamic_task = (void *)(uintptr_t)0x12345678U;
    host_static_task = (void *)(uintptr_t)0x87654321U;
    host_dynamic_calls = host_static_calls = 0;
    host_function = (void *)0; host_name = (void *)0;
    host_stack_depth = host_priority = 0;
    host_argument = host_stack_memory = host_control_block_memory = (void *)0;
}

void open_cfw_thread_new_host_set_irq(uint32_t value) { host_irq = value; }
void open_cfw_thread_new_host_set_dynamic_result(int32_t value) {
    host_dynamic_result = value;
}

uintptr_t open_cfw_thread_new_host_call(
    uint32_t null_function, uint32_t null_attributes,
    const char *name, uint32_t attribute_bits,
    uintptr_t control_block_memory, uint32_t control_block_size,
    uintptr_t stack_memory, uint32_t stack_size, int32_t priority
)
{
    struct open_cfw_cmsis_thread_new_attributes attributes;
    memset(&attributes, 0, sizeof(attributes));
    attributes.name = name;
    attributes.attribute_bits = attribute_bits;
    attributes.control_block_memory = (void *)control_block_memory;
    attributes.control_block_size = control_block_size;
    attributes.stack_memory = (void *)stack_memory;
    attributes.stack_size = stack_size;
    attributes.priority = priority;
    return (uintptr_t)open_cfw_cmsis_thread_new(
        null_function ? (void *)0 : host_thread,
        (void *)(uintptr_t)0xAABBCCDDU,
        null_attributes ? (void *)0 : &attributes
    );
}

uintptr_t open_cfw_thread_new_host_get(uint32_t index)
{
    uintptr_t values[] = {
        host_dynamic_calls, host_static_calls, (uintptr_t)host_function,
        (uintptr_t)host_name, host_stack_depth, host_priority,
        (uintptr_t)host_argument, (uintptr_t)host_stack_memory,
        (uintptr_t)host_control_block_memory
    };
    return index < sizeof(values) / sizeof(values[0]) ? values[index] : 0;
}
