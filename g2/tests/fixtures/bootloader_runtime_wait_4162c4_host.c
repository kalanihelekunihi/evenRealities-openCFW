#include <stdint.h>

typedef struct {
    uint32_t clear_mask;
    uint32_t timeout;
} open_cfw_test_wait_call;

static uint32_t context_value;
static uint32_t ticks[16];
static uint32_t tick_count;
static uint32_t tick_index;
static int statuses[16];
static uint32_t observed_values[16];
static uint32_t response_count;
static uint32_t response_index;
static open_cfw_test_wait_call calls[16];
static uint32_t call_count;

uint32_t open_cfw_test_wait_context(void) { return context_value; }
uint32_t open_cfw_test_wait_tick(void) {
    uint32_t index = tick_index < tick_count ? tick_index++ : tick_count - 1U;
    return ticks[index];
}
int open_cfw_test_wait_backend(
    uint32_t argument_0,
    uint32_t argument_1,
    uint32_t clear_mask,
    uint32_t *observed,
    uint32_t timeout
) {
    uint32_t index = response_index < response_count ? response_index++ : response_count - 1U;
    (void)argument_0;
    (void)argument_1;
    calls[call_count].clear_mask = clear_mask;
    calls[call_count].timeout = timeout;
    ++call_count;
    *observed = observed_values[index];
    return statuses[index];
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_wait_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_TICK_41835A() open_cfw_test_wait_tick()
#define OPEN_CFW_BOOTLOADER_RUNTIME_WAIT_418DAC(...) open_cfw_test_wait_backend(__VA_ARGS__)
#include "../../components/bootloader/core_overlay/runtime_wait_4162c4.c"

void open_cfw_test_wait_reset(uint32_t context) {
    uint32_t index;
    context_value = context;
    tick_count = tick_index = response_count = response_index = call_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        ticks[index] = 0U;
        statuses[index] = 0;
        observed_values[index] = 0U;
        calls[index].clear_mask = calls[index].timeout = 0U;
    }
}
void open_cfw_test_wait_tick_add(uint32_t value) { ticks[tick_count++] = value; }
void open_cfw_test_wait_response_add(int status, uint32_t observed) {
    statuses[response_count] = status;
    observed_values[response_count++] = observed;
}
uint32_t open_cfw_test_wait_tick_calls(void) { return tick_index; }
uint32_t open_cfw_test_wait_call_count(void) { return call_count; }
open_cfw_test_wait_call open_cfw_test_wait_call_get(uint32_t index) { return calls[index]; }
