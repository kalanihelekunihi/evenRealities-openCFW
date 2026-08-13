/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Deterministic host oracle for the retained G2 EasyLogger record allocator,
 * enqueue retry limit, recycler ownership, and diagnostic seams.
 */

#include <stdint.h>
#include <string.h>

struct open_cfw_g2_easylogger_async_record;

struct open_cfw_g2_easylogger_async_record *
open_cfw_retained_easylogger_async_record_allocate(void);
void open_cfw_retained_easylogger_async_record_recycle(
    struct open_cfw_g2_easylogger_async_record *record
);
uint32_t open_cfw_retained_easylogger_async_record_enqueue(
    struct open_cfw_g2_easylogger_async_record *record
);
void open_cfw_retained_easylogger_async_diagnostic(const char *message);

volatile uint8_t open_cfw_retained_easylogger_async_ready;
volatile uint8_t open_cfw_retained_easylogger_async_default_metadata;

#if defined(OPEN_CFW_TEST_EASYLOGGER_ASYNC_SINGLE_OWNER)
#include "../../components/apollo_main/core_overlay/runtime_easylogger_async_record_build_single_owner.c"
#define OPEN_CFW_TEST_EASYLOGGER_ASYNC_BUILD( \
    buffer, length, metadata, level \
) \
    open_cfw_g2_easylogger_async_record_build_single_owner( \
        (buffer), (length), (metadata), (level) \
    )
#else
#include "../../components/apollo_main/core_overlay/runtime_easylogger_async_record_build_stock.c"
#define OPEN_CFW_TEST_EASYLOGGER_ASYNC_BUILD( \
    buffer, length, metadata, level \
) \
    open_cfw_g2_easylogger_async_record_build_stock( \
        (buffer), (length), (metadata), (level) \
    )
#endif

enum {
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_ALLOCATE = 1U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_ENQUEUE = 2U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_RECYCLE = 3U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_DIAGNOSTIC = 4U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_RECORD_TOKEN = 0xA1100001U,
    OPEN_CFW_TEST_EASYLOGGER_ASYNC_ENQUEUE_LIMIT = 10000U
};

struct open_cfw_g2_easylogger_async_record
    open_cfw_test_easylogger_async_record;
uint32_t open_cfw_test_easylogger_async_allocate_available;
uint32_t open_cfw_test_easylogger_async_allocate_calls;
uint32_t open_cfw_test_easylogger_async_enqueue_calls;
uint32_t open_cfw_test_easylogger_async_enqueue_attempts;
uint32_t open_cfw_test_easylogger_async_enqueue_success_attempt;
uint32_t open_cfw_test_easylogger_async_enqueue_retry_limit_count;
uint32_t open_cfw_test_easylogger_async_enqueue_drop_count;
uint32_t open_cfw_test_easylogger_async_recycle_calls;
uint32_t open_cfw_test_easylogger_async_free_head;
uint32_t open_cfw_test_easylogger_async_diagnostic_calls;
char open_cfw_test_easylogger_async_diagnostic_message[96];
uint32_t open_cfw_test_easylogger_async_event_count;
uint32_t open_cfw_test_easylogger_async_events[8];

static void open_cfw_test_easylogger_async_record_event(uint32_t event)
{
    if (open_cfw_test_easylogger_async_event_count < 8U) {
        open_cfw_test_easylogger_async_events[
            open_cfw_test_easylogger_async_event_count
        ] = event;
    }
    open_cfw_test_easylogger_async_event_count++;
}

struct open_cfw_g2_easylogger_async_record *
open_cfw_retained_easylogger_async_record_allocate(void)
{
    open_cfw_test_easylogger_async_record_event(
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_ALLOCATE
    );
    open_cfw_test_easylogger_async_allocate_calls++;
    if (open_cfw_test_easylogger_async_allocate_available == 0U) {
        return (struct open_cfw_g2_easylogger_async_record *)0;
    }
    open_cfw_test_easylogger_async_record.next = 0U;
    open_cfw_test_easylogger_async_record.state = 1U;
    return &open_cfw_test_easylogger_async_record;
}

void open_cfw_retained_easylogger_async_record_recycle(
    struct open_cfw_g2_easylogger_async_record *record
)
{
    open_cfw_test_easylogger_async_record_event(
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_RECYCLE
    );
    open_cfw_test_easylogger_async_recycle_calls++;
    record->state = 0U;
    record->next = open_cfw_test_easylogger_async_free_head;
    open_cfw_test_easylogger_async_free_head =
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_RECORD_TOKEN;
}

uint32_t open_cfw_retained_easylogger_async_record_enqueue(
    struct open_cfw_g2_easylogger_async_record *record
)
{
    uint32_t attempt;

    open_cfw_test_easylogger_async_record_event(
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_ENQUEUE
    );
    open_cfw_test_easylogger_async_enqueue_calls++;
    record->state = 2U;

    for (
        attempt = 1U;
        attempt <= OPEN_CFW_TEST_EASYLOGGER_ASYNC_ENQUEUE_LIMIT;
        attempt++
    ) {
        open_cfw_test_easylogger_async_enqueue_attempts++;
        if (
            open_cfw_test_easylogger_async_enqueue_success_attempt ==
                attempt
        ) {
            return 1U;
        }
    }

    open_cfw_test_easylogger_async_enqueue_retry_limit_count++;
    open_cfw_test_easylogger_async_enqueue_drop_count++;
    open_cfw_retained_easylogger_async_record_recycle(record);
    return 0U;
}

void open_cfw_retained_easylogger_async_diagnostic(const char *message)
{
    open_cfw_test_easylogger_async_record_event(
        OPEN_CFW_TEST_EASYLOGGER_ASYNC_EVENT_DIAGNOSTIC
    );
    open_cfw_test_easylogger_async_diagnostic_calls++;
    strncpy(
        open_cfw_test_easylogger_async_diagnostic_message,
        message,
        sizeof(open_cfw_test_easylogger_async_diagnostic_message) - 1U
    );
    open_cfw_test_easylogger_async_diagnostic_message[
        sizeof(open_cfw_test_easylogger_async_diagnostic_message) - 1U
    ] = '\0';
}

void open_cfw_test_easylogger_async_record_build_reset(
    uint32_t ready,
    uint32_t default_metadata,
    uint32_t allocate_available,
    uint32_t enqueue_success_attempt,
    uint32_t free_head
)
{
    memset(
        &open_cfw_test_easylogger_async_record,
        0xA5,
        sizeof(open_cfw_test_easylogger_async_record)
    );
    open_cfw_retained_easylogger_async_ready = (uint8_t)ready;
    open_cfw_retained_easylogger_async_default_metadata =
        (uint8_t)default_metadata;
    open_cfw_test_easylogger_async_allocate_available =
        allocate_available;
    open_cfw_test_easylogger_async_allocate_calls = 0U;
    open_cfw_test_easylogger_async_enqueue_calls = 0U;
    open_cfw_test_easylogger_async_enqueue_attempts = 0U;
    open_cfw_test_easylogger_async_enqueue_success_attempt =
        enqueue_success_attempt;
    open_cfw_test_easylogger_async_enqueue_retry_limit_count = 0U;
    open_cfw_test_easylogger_async_enqueue_drop_count = 0U;
    open_cfw_test_easylogger_async_recycle_calls = 0U;
    open_cfw_test_easylogger_async_free_head = free_head;
    open_cfw_test_easylogger_async_diagnostic_calls = 0U;
    open_cfw_test_easylogger_async_diagnostic_message[0] = '\0';
    open_cfw_test_easylogger_async_event_count = 0U;
    memset(
        open_cfw_test_easylogger_async_events,
        0,
        sizeof(open_cfw_test_easylogger_async_events)
    );
}

uint32_t open_cfw_test_easylogger_async_record_build(
    const char *buffer,
    uint32_t length,
    uint32_t metadata,
    uint32_t level
)
{
    return OPEN_CFW_TEST_EASYLOGGER_ASYNC_BUILD(
        buffer,
        length,
        metadata,
        level
    );
}

#undef OPEN_CFW_TEST_EASYLOGGER_ASYNC_BUILD
