/*
 * MIT-licensed host harness for the shared G2 FreeRTOS timeout-state adapter.
 */

#include <stdint.h>

enum {
    OPEN_CFW_TEST_TIMEOUT_EVENT_OVERFLOW_READ = 1,
    OPEN_CFW_TEST_TIMEOUT_EVENT_OVERFLOW_STORE = 2,
    OPEN_CFW_TEST_TIMEOUT_EVENT_TICK_READ = 3,
    OPEN_CFW_TEST_TIMEOUT_EVENT_TICK_STORE = 4,
    OPEN_CFW_TEST_TIMEOUT_EVENT_CAPACITY = 4
};

struct open_cfw_test_timeout_event {
    uint32_t kind;
    uint32_t value;
};

static int32_t open_cfw_test_timeout_overflow_word;
static uint32_t open_cfw_test_timeout_tick_word;
static struct open_cfw_test_timeout_event
    open_cfw_test_timeout_events[OPEN_CFW_TEST_TIMEOUT_EVENT_CAPACITY];
static uint32_t open_cfw_test_timeout_event_total;

static void open_cfw_test_timeout_record(uint32_t kind, uint32_t value)
{
    uint32_t index = open_cfw_test_timeout_event_total;

    ++open_cfw_test_timeout_event_total;
    if (index < OPEN_CFW_TEST_TIMEOUT_EVENT_CAPACITY) {
        open_cfw_test_timeout_events[index].kind = kind;
        open_cfw_test_timeout_events[index].value = value;
    }
}

static int32_t open_cfw_test_timeout_overflow_read(void)
{
    open_cfw_test_timeout_record(
        OPEN_CFW_TEST_TIMEOUT_EVENT_OVERFLOW_READ,
        (uint32_t)open_cfw_test_timeout_overflow_word
    );
    return open_cfw_test_timeout_overflow_word;
}

static uint32_t open_cfw_test_timeout_tick_read(void)
{
    open_cfw_test_timeout_record(
        OPEN_CFW_TEST_TIMEOUT_EVENT_TICK_READ,
        open_cfw_test_timeout_tick_word
    );
    return open_cfw_test_timeout_tick_word;
}

static void open_cfw_test_timeout_overflow_store(
    void *timeout,
    int32_t value
)
{
    open_cfw_test_timeout_record(
        OPEN_CFW_TEST_TIMEOUT_EVENT_OVERFLOW_STORE,
        (uint32_t)value
    );
    *(int32_t *)timeout = value;
}

static void open_cfw_test_timeout_tick_store(
    void *timeout,
    uint32_t value
)
{
    open_cfw_test_timeout_record(
        OPEN_CFW_TEST_TIMEOUT_EVENT_TICK_STORE,
        value
    );
    *(uint32_t *)((unsigned char *)timeout + 4U) = value;
}

#define OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_READ() \
    open_cfw_test_timeout_overflow_read()
#define OPEN_CFW_FREERTOS_TIMEOUT_TICK_READ() \
    open_cfw_test_timeout_tick_read()
#define OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_STORE(timeout, value) \
    open_cfw_test_timeout_overflow_store((timeout), (value))
#define OPEN_CFW_FREERTOS_TIMEOUT_TICK_STORE(timeout, value) \
    open_cfw_test_timeout_tick_store((timeout), (value))

#include \
    "../../components/shared/freertos/runtime_freertos_timeout_state.c"

void open_cfw_test_timeout_reset(int32_t overflow, uint32_t tick)
{
    uint32_t index;

    open_cfw_test_timeout_overflow_word = overflow;
    open_cfw_test_timeout_tick_word = tick;
    open_cfw_test_timeout_event_total = 0U;
    for (index = 0U;
         index < OPEN_CFW_TEST_TIMEOUT_EVENT_CAPACITY;
         ++index) {
        open_cfw_test_timeout_events[index].kind = 0U;
        open_cfw_test_timeout_events[index].value = 0U;
    }
}

void open_cfw_test_timeout_invoke(
    int32_t *overflow,
    uint32_t *tick
)
{
    struct open_cfw_freertos_timeout_state timeout;

    timeout.overflow_count = *overflow;
    timeout.time_on_entering = *tick;
    open_cfw_freertos_task_internal_set_timeout_state(&timeout);
    *overflow = timeout.overflow_count;
    *tick = timeout.time_on_entering;
}

uint32_t open_cfw_test_timeout_event_count(void)
{
    return open_cfw_test_timeout_event_total;
}

uint32_t open_cfw_test_timeout_event_kind(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_TIMEOUT_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_timeout_events[index].kind;
}

uint32_t open_cfw_test_timeout_event_value(uint32_t index)
{
    if (index >= OPEN_CFW_TEST_TIMEOUT_EVENT_CAPACITY) {
        return 0U;
    }
    return open_cfw_test_timeout_events[index].value;
}
