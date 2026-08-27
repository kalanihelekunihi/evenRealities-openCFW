#include <stdint.h>

static uintptr_t context_value;
static uintptr_t backend_result;
static uintptr_t call_count;
static uintptr_t observed_owner;
static uintptr_t observed_kind;
static uintptr_t observed_argument;
static uintptr_t observed_option;
static uintptr_t observed_reserved;

static uintptr_t open_cfw_test_submit_context(void) { return context_value; }
static uintptr_t open_cfw_test_submit_backend(
    uintptr_t owner,
    uintptr_t kind,
    uintptr_t argument,
    uintptr_t option,
    uintptr_t reserved
)
{
    ++call_count;
    observed_owner = owner;
    observed_kind = kind;
    observed_argument = argument;
    observed_option = option;
    observed_reserved = reserved;
    return backend_result;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_submit_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_SUBMIT_41937C( \
    owner, kind, argument, option, reserved) \
    open_cfw_test_submit_backend(owner, kind, argument, option, reserved)
#include "../../components/bootloader/core_overlay/runtime_submit_41649a.c"

void open_cfw_test_submit_reset(uintptr_t context, uintptr_t result)
{
    context_value = context;
    backend_result = result;
    call_count = 0U;
    observed_owner = 0U;
    observed_kind = 0U;
    observed_argument = 0U;
    observed_option = 0U;
    observed_reserved = 0U;
}

uintptr_t open_cfw_test_submit_call_count(void) { return call_count; }
uintptr_t open_cfw_test_submit_owner(void) { return observed_owner; }
uintptr_t open_cfw_test_submit_kind(void) { return observed_kind; }
uintptr_t open_cfw_test_submit_argument(void) { return observed_argument; }
uintptr_t open_cfw_test_submit_option(void) { return observed_option; }
uintptr_t open_cfw_test_submit_reserved(void) { return observed_reserved; }
