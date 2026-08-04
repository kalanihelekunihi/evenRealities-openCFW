#include <stdint.h>

unsigned int open_cfw_test_onboarding_runtime_init_prerequisite;
unsigned int open_cfw_test_onboarding_runtime_init_thread_handle;
unsigned int open_cfw_test_onboarding_runtime_init_thread_result;
unsigned int open_cfw_test_onboarding_runtime_init_attribute_values[3];
unsigned int open_cfw_test_onboarding_runtime_init_attribute_inputs[2];
unsigned int open_cfw_test_onboarding_runtime_init_thread_fields[7];
unsigned int open_cfw_test_onboarding_runtime_init_events[16];
unsigned int open_cfw_test_onboarding_runtime_init_event_count;
unsigned int open_cfw_test_onboarding_runtime_init_core_calls;
unsigned int open_cfw_test_onboarding_runtime_init_core_sets_prerequisite;
unsigned int open_cfw_test_onboarding_runtime_init_prerequisite_reads;
unsigned int open_cfw_test_onboarding_runtime_init_attribute_calls;
unsigned int open_cfw_test_onboarding_runtime_init_thread_calls;
unsigned int open_cfw_test_onboarding_runtime_init_store_calls;
unsigned int open_cfw_test_onboarding_runtime_init_load_calls;
unsigned int open_cfw_test_onboarding_runtime_init_fail_stop_calls;

static void open_cfw_test_onboarding_runtime_init_record(unsigned int event)
{
    open_cfw_test_onboarding_runtime_init_events[
        open_cfw_test_onboarding_runtime_init_event_count++
    ] = event;
}

void open_cfw_test_onboarding_runtime_init_reset(void)
{
    unsigned int index;

    open_cfw_test_onboarding_runtime_init_prerequisite = 0U;
    open_cfw_test_onboarding_runtime_init_thread_handle = 0U;
    open_cfw_test_onboarding_runtime_init_thread_result = 0U;
    open_cfw_test_onboarding_runtime_init_event_count = 0U;
    open_cfw_test_onboarding_runtime_init_core_calls = 0U;
    open_cfw_test_onboarding_runtime_init_core_sets_prerequisite = 0U;
    open_cfw_test_onboarding_runtime_init_prerequisite_reads = 0U;
    open_cfw_test_onboarding_runtime_init_attribute_calls = 0U;
    open_cfw_test_onboarding_runtime_init_thread_calls = 0U;
    open_cfw_test_onboarding_runtime_init_store_calls = 0U;
    open_cfw_test_onboarding_runtime_init_load_calls = 0U;
    open_cfw_test_onboarding_runtime_init_fail_stop_calls = 0U;
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_onboarding_runtime_init_attribute_values[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_onboarding_runtime_init_attribute_inputs[index] = 0U;
    }
    for (index = 0U; index < 7U; ++index) {
        open_cfw_test_onboarding_runtime_init_thread_fields[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_onboarding_runtime_init_events[index] = 0U;
    }
}

static void open_cfw_test_onboarding_runtime_init_core(void)
{
    open_cfw_test_onboarding_runtime_init_record(1U);
    ++open_cfw_test_onboarding_runtime_init_core_calls;
    if (
        open_cfw_test_onboarding_runtime_init_core_sets_prerequisite != 0U
    ) {
        open_cfw_test_onboarding_runtime_init_prerequisite =
            open_cfw_test_onboarding_runtime_init_core_sets_prerequisite;
    }
}

static unsigned int open_cfw_test_onboarding_runtime_init_prerequisite_get(
    void
)
{
    open_cfw_test_onboarding_runtime_init_record(2U);
    ++open_cfw_test_onboarding_runtime_init_prerequisite_reads;
    return open_cfw_test_onboarding_runtime_init_prerequisite;
}

static void open_cfw_test_onboarding_runtime_init_attributes(
    unsigned int *control_block,
    unsigned int *stack_memory,
    unsigned int *attribute_bits
)
{
    open_cfw_test_onboarding_runtime_init_record(3U);
    ++open_cfw_test_onboarding_runtime_init_attribute_calls;
    open_cfw_test_onboarding_runtime_init_attribute_inputs[0] =
        *control_block;
    open_cfw_test_onboarding_runtime_init_attribute_inputs[1] =
        *stack_memory;
    *control_block =
        open_cfw_test_onboarding_runtime_init_attribute_values[0];
    *stack_memory =
        open_cfw_test_onboarding_runtime_init_attribute_values[1];
    *attribute_bits =
        open_cfw_test_onboarding_runtime_init_attribute_values[2];
}

static unsigned int open_cfw_test_onboarding_runtime_init_thread(
    const void *entry,
    const void *name,
    unsigned int attribute_bits,
    unsigned int argument,
    unsigned int priority,
    unsigned int stack_memory,
    unsigned int control_block
)
{
    open_cfw_test_onboarding_runtime_init_record(4U);
    ++open_cfw_test_onboarding_runtime_init_thread_calls;
    open_cfw_test_onboarding_runtime_init_thread_fields[0] =
        (unsigned int)(uintptr_t)entry;
    open_cfw_test_onboarding_runtime_init_thread_fields[1] =
        (unsigned int)(uintptr_t)name;
    open_cfw_test_onboarding_runtime_init_thread_fields[2] = attribute_bits;
    open_cfw_test_onboarding_runtime_init_thread_fields[3] = argument;
    open_cfw_test_onboarding_runtime_init_thread_fields[4] = priority;
    open_cfw_test_onboarding_runtime_init_thread_fields[5] = stack_memory;
    open_cfw_test_onboarding_runtime_init_thread_fields[6] = control_block;
    return open_cfw_test_onboarding_runtime_init_thread_result;
}

static void open_cfw_test_onboarding_runtime_init_thread_store(
    unsigned int thread
)
{
    open_cfw_test_onboarding_runtime_init_record(5U);
    ++open_cfw_test_onboarding_runtime_init_store_calls;
    open_cfw_test_onboarding_runtime_init_thread_handle = thread;
}

static unsigned int open_cfw_test_onboarding_runtime_init_thread_load(void)
{
    open_cfw_test_onboarding_runtime_init_record(6U);
    ++open_cfw_test_onboarding_runtime_init_load_calls;
    return open_cfw_test_onboarding_runtime_init_thread_handle;
}

static void open_cfw_test_onboarding_runtime_init_fail_stop(void)
{
    open_cfw_test_onboarding_runtime_init_record(7U);
    ++open_cfw_test_onboarding_runtime_init_fail_stop_calls;
}

#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_CORE() \
    open_cfw_test_onboarding_runtime_init_core()
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_PREREQUISITE() \
    open_cfw_test_onboarding_runtime_init_prerequisite_get()
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_ATTRIBUTES(...) \
    open_cfw_test_onboarding_runtime_init_attributes(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD(...) \
    open_cfw_test_onboarding_runtime_init_thread(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_STORE(value) \
    open_cfw_test_onboarding_runtime_init_thread_store(value)
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_THREAD_LOAD() \
    open_cfw_test_onboarding_runtime_init_thread_load()
#define OPEN_CFW_ONBOARDING_RUNTIME_INIT_FAIL_STOP() \
    open_cfw_test_onboarding_runtime_init_fail_stop()

#include "../../components/apollo_main/core_overlay/onboarding_runtime_init.c"
