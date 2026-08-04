/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded Apollo protected-MRAM record query helpers matched to stock entries
 * 0x0047A5D0, 0x0047A600, 0x0047A630, 0x0047A676, and 0x0047A6B4.
 */

typedef __UINTPTR_TYPE__ open_cfw_mram_query_uintptr;

#ifndef OPEN_CFW_MRAM_QUERY_RECORDS_ADDRESS
#define OPEN_CFW_MRAM_QUERY_RECORDS_ADDRESS 0x20067A30U
#endif

#define OPEN_CFW_MRAM_QUERY_RECORD_COUNT 10U
#define OPEN_CFW_MRAM_QUERY_RECORD_SIZE 200U

typedef struct {
    unsigned char bytes[0xC4U];
    unsigned int timestamp;
} open_cfw_mram_query_record;

static __attribute__((always_inline)) inline open_cfw_mram_query_record *
open_cfw_mram_query_records(void)
{
    return (open_cfw_mram_query_record *)
        (open_cfw_mram_query_uintptr)
        OPEN_CFW_MRAM_QUERY_RECORDS_ADDRESS;
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_record_is_active(
    const unsigned char *record
)
{
    open_cfw_mram_query_record *records = open_cfw_mram_query_records();
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_QUERY_RECORD_COUNT; ++index) {
        if (
            records[index].bytes[0x2FU] != 0U
            && records[index].bytes[0x30U] != 0U
            && (const unsigned char *)(const void *)&records[index] == record
        ) {
            return 1U;
        }
    }
    return 0U;
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_has_untyped_record(void)
{
    open_cfw_mram_query_record *records = open_cfw_mram_query_records();
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_QUERY_RECORD_COUNT; ++index) {
        if (
            records[index].bytes[0x2FU] != 0U
            && records[index].bytes[0xC3U] == 0U
        ) {
            return 1U;
        }
    }
    return 0U;
}

__attribute__((used, noinline))
unsigned char *open_cfw_mram_next_active_record(unsigned char *record)
{
    unsigned char *candidate;
    unsigned int count;
    unsigned int index;

    if (record == (unsigned char *)0) {
        candidate = (unsigned char *)(void *)open_cfw_mram_query_records();
        count = OPEN_CFW_MRAM_QUERY_RECORD_COUNT;
    }
    else {
        candidate = record + OPEN_CFW_MRAM_QUERY_RECORD_SIZE;
        count = OPEN_CFW_MRAM_QUERY_RECORD_COUNT - 1U;
    }

#pragma clang loop unroll(disable)
    for (index = 0U; index < count; ++index) {
        if (candidate[0x2FU] != 0U) {
            return candidate;
        }
        candidate += OPEN_CFW_MRAM_QUERY_RECORD_SIZE;
    }
    return (unsigned char *)0;
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_count_active_type(unsigned int type)
{
    open_cfw_mram_query_record *records = open_cfw_mram_query_records();
    unsigned char expected_type = (unsigned char)type;
    unsigned int count = 0U;
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_QUERY_RECORD_COUNT; ++index) {
        if (
            records[index].bytes[0x2FU] != 0U
            && records[index].bytes[0xC3U] == expected_type
        ) {
            ++count;
        }
    }
    return (unsigned char)count;
}

__attribute__((used, noinline))
unsigned char *open_cfw_mram_oldest_active_type(unsigned int type)
{
    open_cfw_mram_query_record *records = open_cfw_mram_query_records();
    open_cfw_mram_query_record *selected = (open_cfw_mram_query_record *)0;
    unsigned int oldest = 0xFFFFFFFFU;
    unsigned char expected_type = (unsigned char)type;
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < OPEN_CFW_MRAM_QUERY_RECORD_COUNT; ++index) {
        if (
            records[index].bytes[0x2FU] != 0U
            && records[index].bytes[0x30U] != 0U
            && records[index].bytes[0xC3U] == expected_type
            && records[index].timestamp < oldest
        ) {
            oldest = records[index].timestamp;
            selected = &records[index];
        }
    }
    return (unsigned char *)(void *)selected;
}
