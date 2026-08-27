#include <stdint.h>

static uintptr_t context_value;
static uintptr_t isr_result;
static uintptr_t isr_bits;
static uintptr_t task_result;
static uintptr_t wake_value;
static uintptr_t context_calls;
static uintptr_t isr_set_calls;
static uintptr_t isr_get_calls;
static uintptr_t task_calls;
static uintptr_t pendsv_calls;
static uintptr_t observed_object;
static uintptr_t observed_flags;

static uintptr_t open_cfw_test_flags_context(void)
{
    ++context_calls;
    return context_value;
}
static uintptr_t open_cfw_test_flags_set_isr(
    uintptr_t object,
    uintptr_t flags,
    uintptr_t *wake_required
)
{
    ++isr_set_calls;
    observed_object = object;
    observed_flags = flags;
    *wake_required = wake_value;
    return isr_result;
}
static uintptr_t open_cfw_test_flags_get_isr(uintptr_t object)
{
    ++isr_get_calls;
    observed_object = object;
    return isr_bits;
}
static uintptr_t open_cfw_test_flags_set_task(uintptr_t object, uintptr_t flags)
{
    ++task_calls;
    observed_object = object;
    observed_flags = flags;
    return task_result;
}
static void open_cfw_test_flags_pendsv(void) { ++pendsv_calls; }

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_flags_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_ISR_419BD2( \
    object, flags, wake_required) \
    open_cfw_test_flags_set_isr(object, flags, wake_required)
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_GET_ISR_419AF4(object) \
    open_cfw_test_flags_get_isr(object)
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_SET_TASK_419B06(object, flags) \
    open_cfw_test_flags_set_task(object, flags)
#define OPEN_CFW_BOOTLOADER_RUNTIME_REQUEST_PENDSV() open_cfw_test_flags_pendsv()
#include "../../components/bootloader/core_overlay/runtime_flags_set_41652e.c"

void open_cfw_test_flags_reset(
    uintptr_t context,
    uintptr_t set_isr_result,
    uintptr_t get_isr_bits,
    uintptr_t set_task_result,
    uintptr_t wake
)
{
    context_value = context;
    isr_result = set_isr_result;
    isr_bits = get_isr_bits;
    task_result = set_task_result;
    wake_value = wake;
    context_calls = 0U;
    isr_set_calls = 0U;
    isr_get_calls = 0U;
    task_calls = 0U;
    pendsv_calls = 0U;
    observed_object = 0U;
    observed_flags = 0U;
}

uintptr_t open_cfw_test_flags_context_calls(void) { return context_calls; }
uintptr_t open_cfw_test_flags_isr_set_calls(void) { return isr_set_calls; }
uintptr_t open_cfw_test_flags_isr_get_calls(void) { return isr_get_calls; }
uintptr_t open_cfw_test_flags_task_calls(void) { return task_calls; }
uintptr_t open_cfw_test_flags_pendsv_calls(void) { return pendsv_calls; }
uintptr_t open_cfw_test_flags_object(void) { return observed_object; }
uintptr_t open_cfw_test_flags_flags(void) { return observed_flags; }
