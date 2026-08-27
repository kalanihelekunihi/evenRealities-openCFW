#include <stdint.h>

static uint32_t context_value;
static uint32_t call_count;
static uint32_t last_argument;

uint32_t open_cfw_test_notify_context(void) { return context_value; }
void open_cfw_test_notify_backend(uint32_t argument) {
    ++call_count;
    last_argument = argument;
}
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_notify_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_NOTIFY_417FA8(argument) open_cfw_test_notify_backend(argument)
#include "../../components/bootloader/core_overlay/runtime_notify_416378.c"

void open_cfw_test_notify_reset(uint32_t context) {
    context_value = context;
    call_count = 0U;
    last_argument = 0U;
}
uint32_t open_cfw_test_notify_call_count(void) { return call_count; }
uint32_t open_cfw_test_notify_last_argument(void) { return last_argument; }
