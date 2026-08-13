/*
 * MIT-licensed host harness and pristine-logic oracle for the G2 FreeRTOS
 * xTaskCheckForTimeOut source candidate.
 */

#include <stdint.h>

enum {
    OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE = 0,
    OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE = 1,
    OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS = 2,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_ASSERT = 1,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_ENTER = 2,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_TICK_LOAD = 3,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_OVERFLOW_LOAD = 4,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_INTERNAL_SET = 5,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_EXIT = 6,
    OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_CAPACITY = 12
};

struct open_cfw_test_check_timeout_event {
    uint32_t kind;
    uint32_t value;
};

static int32_t open_cfw_test_candidate_overflow;
static uint32_t open_cfw_test_candidate_tick;
static int32_t open_cfw_test_oracle_overflow;
static uint32_t open_cfw_test_oracle_tick;
static struct open_cfw_test_check_timeout_event open_cfw_test_events[
    OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS
][OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_CAPACITY];
static uint32_t open_cfw_test_event_counts[
    OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS
];

static void open_cfw_test_check_timeout_record(
    uint32_t channel,
    uint32_t kind,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_event_counts[channel];

    ++open_cfw_test_event_counts[channel];
    if (index < OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_CAPACITY) {
        open_cfw_test_events[channel][index].kind = kind;
        open_cfw_test_events[channel][index].value = value;
    }
}

static void open_cfw_test_candidate_assert(int condition)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_ASSERT,
        (uint32_t)(condition != 0)
    );
}

static void open_cfw_test_candidate_enter(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_ENTER,
        0U
    );
}

static void open_cfw_test_candidate_exit(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_EXIT,
        0U
    );
}

static uint32_t open_cfw_test_candidate_tick_load(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_TICK_LOAD,
        open_cfw_test_candidate_tick
    );
    return open_cfw_test_candidate_tick;
}

static int32_t open_cfw_test_candidate_overflow_load(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_OVERFLOW_LOAD,
        (uint32_t)open_cfw_test_candidate_overflow
    );
    return open_cfw_test_candidate_overflow;
}

static void open_cfw_test_candidate_internal_set(void *timeout)
{
    int32_t *words = (int32_t *)timeout;

    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_CANDIDATE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_INTERNAL_SET,
        0U
    );
    words[0] = open_cfw_test_candidate_overflow;
    ((uint32_t *)timeout)[1] = open_cfw_test_candidate_tick;
}

#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT(condition) \
    open_cfw_test_candidate_assert((condition))
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL() \
    open_cfw_test_candidate_enter()
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL() \
    open_cfw_test_candidate_exit()
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_LOAD() \
    open_cfw_test_candidate_tick_load()
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_LOAD() \
    open_cfw_test_candidate_overflow_load()
#define OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET(timeout) \
    open_cfw_test_candidate_internal_set((timeout))

#include \
    "../../components/shared/freertos/runtime_freertos_task_check_for_timeout.c"

static void open_cfw_test_oracle_assert(int condition)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_ASSERT,
        (uint32_t)(condition != 0)
    );
}

static void open_cfw_test_oracle_enter(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_ENTER,
        0U
    );
}

static void open_cfw_test_oracle_exit(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_EXIT,
        0U
    );
}

static uint32_t open_cfw_test_oracle_tick_load(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_TICK_LOAD,
        open_cfw_test_oracle_tick
    );
    return open_cfw_test_oracle_tick;
}

static int32_t open_cfw_test_oracle_overflow_load(void)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_OVERFLOW_LOAD,
        (uint32_t)open_cfw_test_oracle_overflow
    );
    return open_cfw_test_oracle_overflow;
}

static void open_cfw_test_oracle_internal_set(
    struct open_cfw_freertos_check_timeout_state *timeout
)
{
    open_cfw_test_check_timeout_record(
        OPEN_CFW_TEST_CHECK_TIMEOUT_ORACLE,
        OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_INTERNAL_SET,
        0U
    );
    timeout->overflow_count = open_cfw_test_oracle_overflow;
    timeout->time_on_entering = open_cfw_test_oracle_tick;
}

/* Pristine V10.5.1 operation under the exact recovered G2 feature gates. */
static int32_t open_cfw_test_pristine_task_check_for_timeout(
    struct open_cfw_freertos_check_timeout_state * const timeout,
    uint32_t * const ticks_to_wait
)
{
    int32_t result;

    open_cfw_test_oracle_assert(timeout != 0);
    open_cfw_test_oracle_assert(ticks_to_wait != 0);

    open_cfw_test_oracle_enter();
    {
        const uint32_t const_tick_count = open_cfw_test_oracle_tick_load();
        const uint32_t elapsed_time =
            const_tick_count - timeout->time_on_entering;

        if (*ticks_to_wait == UINT32_MAX) {
            result = 0;
        } else if (
            (open_cfw_test_oracle_overflow_load() !=
             timeout->overflow_count) &&
            (const_tick_count >= timeout->time_on_entering)
        ) {
            result = 1;
            *ticks_to_wait = 0U;
        } else if (elapsed_time < *ticks_to_wait) {
            *ticks_to_wait -= elapsed_time;
            open_cfw_test_oracle_internal_set(timeout);
            result = 0;
        } else {
            *ticks_to_wait = 0U;
            result = 1;
        }
    }
    open_cfw_test_oracle_exit();

    return result;
}

void open_cfw_test_check_timeout_reset(int32_t overflow, uint32_t tick)
{
    uint32_t channel;
    uint32_t index;

    open_cfw_test_candidate_overflow = overflow;
    open_cfw_test_candidate_tick = tick;
    open_cfw_test_oracle_overflow = overflow;
    open_cfw_test_oracle_tick = tick;
    for (channel = 0U;
         channel < OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS;
         ++channel) {
        open_cfw_test_event_counts[channel] = 0U;
        for (index = 0U;
             index < OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_CAPACITY;
             ++index) {
            open_cfw_test_events[channel][index].kind = 0U;
            open_cfw_test_events[channel][index].value = 0U;
        }
    }
}

int32_t open_cfw_test_check_timeout_candidate(
    int32_t *overflow,
    uint32_t *time_on_entering,
    uint32_t *ticks_to_wait
)
{
    struct open_cfw_freertos_check_timeout_state timeout;
    int32_t result;

    timeout.overflow_count = *overflow;
    timeout.time_on_entering = *time_on_entering;
    result = open_cfw_freertos_task_check_for_timeout(
        &timeout,
        ticks_to_wait
    );
    *overflow = timeout.overflow_count;
    *time_on_entering = timeout.time_on_entering;
    return result;
}

int32_t open_cfw_test_check_timeout_oracle(
    int32_t *overflow,
    uint32_t *time_on_entering,
    uint32_t *ticks_to_wait
)
{
    struct open_cfw_freertos_check_timeout_state timeout;
    int32_t result;

    timeout.overflow_count = *overflow;
    timeout.time_on_entering = *time_on_entering;
    result = open_cfw_test_pristine_task_check_for_timeout(
        &timeout,
        ticks_to_wait
    );
    *overflow = timeout.overflow_count;
    *time_on_entering = timeout.time_on_entering;
    return result;
}

uint32_t open_cfw_test_check_timeout_event_count(uint32_t channel)
{
    if (channel >= OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS) {
        return 0U;
    }
    return open_cfw_test_event_counts[channel];
}

uint32_t open_cfw_test_check_timeout_event_kind(
    uint32_t channel,
    uint32_t index
)
{
    if (
        (channel >= OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS) ||
        (index >= OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_CAPACITY)
    ) {
        return 0U;
    }
    return open_cfw_test_events[channel][index].kind;
}

uint32_t open_cfw_test_check_timeout_event_value(
    uint32_t channel,
    uint32_t index
)
{
    if (
        (channel >= OPEN_CFW_TEST_CHECK_TIMEOUT_CHANNELS) ||
        (index >= OPEN_CFW_TEST_CHECK_TIMEOUT_EVENT_CAPACITY)
    ) {
        return 0U;
    }
    return open_cfw_test_events[channel][index].value;
}
