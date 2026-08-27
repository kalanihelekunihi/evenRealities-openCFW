#include <stdint.h>

static uintptr_t context_value;
static uintptr_t backend_result;
static uintptr_t context_calls;
static uintptr_t backend_calls;
static uintptr_t observed_object;
static uintptr_t observed_flags;
static uintptr_t observed_clear;
static uintptr_t observed_wait_all;
static uintptr_t observed_timeout;

static uintptr_t open_cfw_test_flags_wait_context(void)
{
    ++context_calls;
    return context_value;
}
static uintptr_t open_cfw_test_flags_wait_backend(
    uintptr_t object,
    uintptr_t flags,
    uintptr_t clear_on_exit,
    uintptr_t wait_all,
    uintptr_t timeout
)
{
    ++backend_calls;
    observed_object = object;
    observed_flags = flags;
    observed_clear = clear_on_exit;
    observed_wait_all = wait_all;
    observed_timeout = timeout;
    return backend_result;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_flags_wait_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_WAIT_4199DC( \
    object, flags, clear_on_exit, wait_all, timeout) \
    open_cfw_test_flags_wait_backend( \
        object, flags, clear_on_exit, wait_all, timeout)
#include "../../components/bootloader/core_overlay/runtime_flags_wait_416590.c"

void open_cfw_test_flags_wait_reset(uintptr_t context, uintptr_t result)
{
    context_value = context;
    backend_result = result;
    context_calls = 0U;
    backend_calls = 0U;
    observed_object = 0U;
    observed_flags = 0U;
    observed_clear = 0U;
    observed_wait_all = 0U;
    observed_timeout = 0U;
}

uintptr_t open_cfw_test_flags_wait_context_calls(void) { return context_calls; }
uintptr_t open_cfw_test_flags_wait_backend_calls(void) { return backend_calls; }
uintptr_t open_cfw_test_flags_wait_object(void) { return observed_object; }
uintptr_t open_cfw_test_flags_wait_flags(void) { return observed_flags; }
uintptr_t open_cfw_test_flags_wait_clear(void) { return observed_clear; }
uintptr_t open_cfw_test_flags_wait_wait_all(void) { return observed_wait_all; }
uintptr_t open_cfw_test_flags_wait_timeout(void) { return observed_timeout; }
