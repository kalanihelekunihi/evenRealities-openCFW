/* SPDX-License-Identifier: GPL-3.0-only */

#include <stdint.h>
#include <string.h>

#include "../../components/shared/easylogger/runtime_easylogger_hexdump_seams.c"

volatile open_cfw_easylogger_hexdump_seam_u8
    open_cfw_retained_easylogger_async_ready;
volatile open_cfw_easylogger_hexdump_seam_u8
    open_cfw_retained_easylogger_async_default_metadata;

static struct open_cfw_easylogger_hexdump_record open_cfw_test_record;
static uint32_t open_cfw_test_allocate_enabled;
static uint32_t open_cfw_test_enqueue_result;
static uint32_t open_cfw_test_allocate_calls_value;
static uint32_t open_cfw_test_enqueue_calls_value;
static uint32_t open_cfw_test_recycle_calls_value;
static uint32_t open_cfw_test_double_recycle_calls_value;
static uint32_t open_cfw_test_free_list_count_value;
static uint32_t open_cfw_test_record_owner_value;
static uint32_t open_cfw_test_diagnostic_calls_value;
static char open_cfw_test_diagnostic_value[80];

enum {
    OPEN_CFW_TEST_RECORD_FREE = 0U,
    OPEN_CFW_TEST_RECORD_BUILDER = 1U,
    OPEN_CFW_TEST_RECORD_QUEUE = 2U
};

static void open_cfw_test_easylogger_hexdump_record_recycle_once(
    struct open_cfw_easylogger_hexdump_record *record
)
{
    if (
        record != &open_cfw_test_record
        || open_cfw_test_record_owner_value == OPEN_CFW_TEST_RECORD_FREE
    ) {
        open_cfw_test_double_recycle_calls_value++;
        return;
    }
    open_cfw_test_record_owner_value = OPEN_CFW_TEST_RECORD_FREE;
    open_cfw_test_free_list_count_value++;
    open_cfw_test_recycle_calls_value++;
}

struct open_cfw_easylogger_hexdump_record *
open_cfw_retained_easylogger_async_record_allocate(void)
{
    open_cfw_test_allocate_calls_value++;
    if (
        open_cfw_test_allocate_enabled == 0U
        || open_cfw_test_free_list_count_value == 0U
        || open_cfw_test_record_owner_value != OPEN_CFW_TEST_RECORD_FREE
    ) {
        return (struct open_cfw_easylogger_hexdump_record *)0;
    }
    open_cfw_test_free_list_count_value--;
    open_cfw_test_record_owner_value = OPEN_CFW_TEST_RECORD_BUILDER;
    return &open_cfw_test_record;
}

open_cfw_easylogger_hexdump_seam_u32
open_cfw_retained_easylogger_async_record_enqueue(
    struct open_cfw_easylogger_hexdump_record *record
)
{
    open_cfw_test_enqueue_calls_value++;
    if (
        record != &open_cfw_test_record
        || open_cfw_test_record_owner_value != OPEN_CFW_TEST_RECORD_BUILDER
    ) {
        open_cfw_test_double_recycle_calls_value++;
        return 0U;
    }
    if (open_cfw_test_enqueue_result == 0U) {
        /* The retained enqueue consumes and recycles a rejected record. */
        open_cfw_test_easylogger_hexdump_record_recycle_once(record);
    } else {
        open_cfw_test_record_owner_value = OPEN_CFW_TEST_RECORD_QUEUE;
    }
    return open_cfw_test_enqueue_result;
}

void open_cfw_retained_easylogger_async_diagnostic(const char *message)
{
    uint32_t index;
    open_cfw_test_diagnostic_calls_value++;
    for (index = 0U; index + 1U < sizeof(open_cfw_test_diagnostic_value); index++) {
        open_cfw_test_diagnostic_value[index] = message[index];
        if (message[index] == '\0') {
            return;
        }
    }
    open_cfw_test_diagnostic_value[sizeof(open_cfw_test_diagnostic_value) - 1U] =
        '\0';
}

void open_cfw_test_easylogger_hexdump_seams_reset(
    uint32_t ready,
    uint32_t default_metadata,
    uint32_t allocate_enabled,
    uint32_t enqueue_result
)
{
    open_cfw_retained_easylogger_async_ready =
        (open_cfw_easylogger_hexdump_seam_u8)ready;
    open_cfw_retained_easylogger_async_default_metadata =
        (open_cfw_easylogger_hexdump_seam_u8)default_metadata;
    open_cfw_test_allocate_enabled = allocate_enabled;
    open_cfw_test_enqueue_result = enqueue_result;
    open_cfw_test_allocate_calls_value = 0U;
    open_cfw_test_enqueue_calls_value = 0U;
    open_cfw_test_recycle_calls_value = 0U;
    open_cfw_test_double_recycle_calls_value = 0U;
    open_cfw_test_free_list_count_value = 1U;
    open_cfw_test_record_owner_value = OPEN_CFW_TEST_RECORD_FREE;
    open_cfw_test_diagnostic_calls_value = 0U;
    memset(&open_cfw_test_record, 0xA5, sizeof(open_cfw_test_record));
    memset(open_cfw_test_diagnostic_value, 0, sizeof(open_cfw_test_diagnostic_value));
}

void *open_cfw_test_easylogger_hexdump_fill(
    void *destination,
    uint32_t count,
    uint32_t value
)
{
    return open_cfw_easylogger_hexdump_fill_source(destination, count, value);
}

int open_cfw_test_easylogger_hexdump_format_header(
    char *buffer,
    uint32_t size,
    const char *name,
    uint32_t offset,
    uint32_t end
)
{
    return open_cfw_easylogger_hexdump_format_header_source(
        buffer,
        size,
        name,
        offset,
        end
    );
}

void open_cfw_test_easylogger_hexdump_format_hex(char *buffer, uint32_t value)
{
    open_cfw_easylogger_hexdump_format_hex_source(
        buffer,
        (open_cfw_easylogger_hexdump_seam_u8)value
    );
}

void open_cfw_test_easylogger_hexdump_format_character(
    char *buffer,
    uint32_t value
)
{
    open_cfw_easylogger_hexdump_format_character_source(
        buffer,
        (open_cfw_easylogger_hexdump_seam_u8)value
    );
}

void open_cfw_test_easylogger_hexdump_blank_hex(char *buffer)
{
    open_cfw_easylogger_hexdump_blank_hex_source(buffer);
}

void open_cfw_test_easylogger_hexdump_raw_submit(
    const char *buffer,
    uint32_t length
)
{
    open_cfw_easylogger_hexdump_raw_submit_source(buffer, length);
}

uint32_t open_cfw_test_easylogger_hexdump_build_level_less(
    const char *buffer,
    uint32_t length,
    uint32_t metadata
)
{
    return open_cfw_g2_easylogger_async_record_build_level_less(
        buffer,
        length,
        metadata
    );
}

uint32_t open_cfw_test_easylogger_hexdump_record_length(void)
{
    return open_cfw_test_record.length;
}

uint32_t open_cfw_test_easylogger_hexdump_record_metadata(void)
{
    return open_cfw_test_record.metadata;
}

uint32_t open_cfw_test_easylogger_hexdump_record_reserved_level(void)
{
    return open_cfw_test_record.reserved_level;
}

const char *open_cfw_test_easylogger_hexdump_record_payload(void)
{
    return open_cfw_test_record.payload;
}

uint32_t open_cfw_test_easylogger_hexdump_record_payload_offset(void)
{
    return (uint32_t)(
        (uintptr_t)open_cfw_test_record.payload
        - (uintptr_t)&open_cfw_test_record
    );
}

uint32_t open_cfw_test_easylogger_hexdump_allocate_calls(void)
{
    return open_cfw_test_allocate_calls_value;
}

uint32_t open_cfw_test_easylogger_hexdump_enqueue_calls(void)
{
    return open_cfw_test_enqueue_calls_value;
}

uint32_t open_cfw_test_easylogger_hexdump_recycle_calls(void)
{
    return open_cfw_test_recycle_calls_value;
}

uint32_t open_cfw_test_easylogger_hexdump_double_recycle_calls(void)
{
    return open_cfw_test_double_recycle_calls_value;
}

uint32_t open_cfw_test_easylogger_hexdump_free_list_count(void)
{
    return open_cfw_test_free_list_count_value;
}

uint32_t open_cfw_test_easylogger_hexdump_record_owner(void)
{
    return open_cfw_test_record_owner_value;
}

uint32_t open_cfw_test_easylogger_hexdump_diagnostic_calls(void)
{
    return open_cfw_test_diagnostic_calls_value;
}

const char *open_cfw_test_easylogger_hexdump_diagnostic(void)
{
    return open_cfw_test_diagnostic_value;
}
