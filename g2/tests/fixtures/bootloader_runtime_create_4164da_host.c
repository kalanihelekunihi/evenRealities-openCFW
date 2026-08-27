#include <stdint.h>

static uintptr_t context_value;
static uintptr_t static_result;
static uintptr_t dynamic_result;
static uintptr_t static_calls;
static uintptr_t dynamic_calls;
static uintptr_t observed_storage;

static uintptr_t open_cfw_test_create_context(void) { return context_value; }
static uintptr_t open_cfw_test_create_static(uintptr_t storage)
{
    ++static_calls;
    observed_storage = storage;
    return static_result;
}
static uintptr_t open_cfw_test_create_dynamic(void)
{
    ++dynamic_calls;
    return dynamic_result;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_create_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_STATIC_419978(storage) \
    open_cfw_test_create_static(storage)
#define OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_DYNAMIC_4199BC() \
    open_cfw_test_create_dynamic()
#include "../../components/bootloader/core_overlay/runtime_create_4164da.c"

void open_cfw_test_create_reset(
    uintptr_t context,
    uintptr_t static_value,
    uintptr_t dynamic_value
)
{
    context_value = context;
    static_result = static_value;
    dynamic_result = dynamic_value;
    static_calls = 0U;
    dynamic_calls = 0U;
    observed_storage = 0U;
}

uintptr_t open_cfw_test_create_static_calls(void) { return static_calls; }
uintptr_t open_cfw_test_create_dynamic_calls(void) { return dynamic_calls; }
uintptr_t open_cfw_test_create_storage(void) { return observed_storage; }
