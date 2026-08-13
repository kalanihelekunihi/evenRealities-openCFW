/*
 * MIT-licensed host harness for the shared G2 FreeRTOS missed-yield adapter.
 */

#include <stdint.h>

static volatile int32_t open_cfw_test_freertos_yield_pending_word;
static volatile uint32_t open_cfw_test_freertos_yield_pending_store_count;

static void open_cfw_test_freertos_yield_pending_store(int32_t value)
{
    open_cfw_test_freertos_yield_pending_word = value;
    ++open_cfw_test_freertos_yield_pending_store_count;
}

#define OPEN_CFW_FREERTOS_YIELD_PENDING_STORE(value) \
    open_cfw_test_freertos_yield_pending_store(value)

#include \
    "../../components/shared/freertos/runtime_freertos_missed_yield.c"

void open_cfw_test_freertos_missed_yield_reset(int32_t value)
{
    open_cfw_test_freertos_yield_pending_word = value;
    open_cfw_test_freertos_yield_pending_store_count = 0U;
}

void open_cfw_test_freertos_missed_yield_invoke(void)
{
    open_cfw_freertos_task_missed_yield();
}

int32_t open_cfw_test_freertos_missed_yield_value(void)
{
    return open_cfw_test_freertos_yield_pending_word;
}

uint32_t open_cfw_test_freertos_missed_yield_stores(void)
{
    return open_cfw_test_freertos_yield_pending_store_count;
}
