/*
 * MIT-licensed host harness for the shared G2 FreeRTOS tick-count adapter.
 */

#include <stdint.h>

static volatile uint32_t open_cfw_test_freertos_tick_count_word;
static volatile uint32_t open_cfw_test_freertos_tick_count_read_count;

static uint32_t open_cfw_test_freertos_tick_count_read_word(void)
{
    ++open_cfw_test_freertos_tick_count_read_count;
    return open_cfw_test_freertos_tick_count_word;
}

#define OPEN_CFW_FREERTOS_TICK_COUNT_WORD \
    open_cfw_test_freertos_tick_count_read_word()

#include \
    "../../components/shared/freertos/runtime_freertos_tick_count.c"

void open_cfw_test_freertos_tick_count_set(uint32_t ticks)
{
    open_cfw_test_freertos_tick_count_word = ticks;
    open_cfw_test_freertos_tick_count_read_count = 0U;
}

uint32_t open_cfw_test_freertos_tick_count_get_task(void)
{
    return open_cfw_freertos_task_get_tick_count();
}

uint32_t open_cfw_test_freertos_tick_count_get_from_isr(void)
{
    return open_cfw_freertos_task_get_tick_count_from_isr();
}

uint32_t open_cfw_test_freertos_tick_count_get_provider(void)
{
    return open_cfw_freertos_tick_count_read();
}

uint32_t open_cfw_test_freertos_tick_count_reads(void)
{
    return open_cfw_test_freertos_tick_count_read_count;
}
