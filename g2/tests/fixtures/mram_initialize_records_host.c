/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Apollo protected-MRAM initialization wrapper.
 */

#include <string.h>

unsigned int open_cfw_test_mram_initialize_cache(
    unsigned int,
    unsigned int
);
void open_cfw_test_mram_initialize_load(unsigned char *);
void open_cfw_test_mram_initialize_sync(void);
void open_cfw_test_mram_initialize_dump(
    const unsigned char *,
    unsigned int
);

unsigned char open_cfw_test_mram_initialize_records[2000];

#define OPEN_CFW_MRAM_INITIALIZE_RECORDS \
    open_cfw_test_mram_initialize_records
#define OPEN_CFW_MRAM_INITIALIZE_CACHE(range, all) \
    open_cfw_test_mram_initialize_cache((range), (all))
#define OPEN_CFW_MRAM_INITIALIZE_LOAD(records) \
    open_cfw_test_mram_initialize_load(records)
#define OPEN_CFW_MRAM_INITIALIZE_SYNC() \
    open_cfw_test_mram_initialize_sync()
#define OPEN_CFW_MRAM_INITIALIZE_DUMP(record, index) \
    open_cfw_test_mram_initialize_dump((record), (index))

#include "../../components/apollo_main/core_overlay/mram_initialize_records.c"

unsigned int open_cfw_test_mram_initialize_order[16];
unsigned int open_cfw_test_mram_initialize_order_count;
unsigned int open_cfw_test_mram_initialize_cache_range;
unsigned int open_cfw_test_mram_initialize_cache_all;
unsigned int open_cfw_test_mram_initialize_cache_result;
unsigned char *open_cfw_test_mram_initialize_load_records;
open_cfw_mram_initialize_uintptr
    open_cfw_test_mram_initialize_dump_records[10];
unsigned int open_cfw_test_mram_initialize_dump_indices[10];
unsigned int open_cfw_test_mram_initialize_dump_count;

static void open_cfw_test_mram_initialize_order_append(unsigned int event)
{
    if (open_cfw_test_mram_initialize_order_count < 16U) {
        open_cfw_test_mram_initialize_order[
            open_cfw_test_mram_initialize_order_count
        ] = event;
    }
    ++open_cfw_test_mram_initialize_order_count;
}

void open_cfw_test_mram_initialize_reset(void)
{
    memset(
        open_cfw_test_mram_initialize_order,
        0,
        sizeof(open_cfw_test_mram_initialize_order)
    );
    memset(
        open_cfw_test_mram_initialize_dump_records,
        0,
        sizeof(open_cfw_test_mram_initialize_dump_records)
    );
    memset(
        open_cfw_test_mram_initialize_dump_indices,
        0,
        sizeof(open_cfw_test_mram_initialize_dump_indices)
    );
    open_cfw_test_mram_initialize_order_count = 0U;
    open_cfw_test_mram_initialize_cache_range = 0U;
    open_cfw_test_mram_initialize_cache_all = 0U;
    open_cfw_test_mram_initialize_cache_result = 0U;
    open_cfw_test_mram_initialize_load_records = (unsigned char *)0;
    open_cfw_test_mram_initialize_dump_count = 0U;
}

unsigned int open_cfw_test_mram_initialize_cache(
    unsigned int range,
    unsigned int all
)
{
    open_cfw_test_mram_initialize_order_append(1U);
    open_cfw_test_mram_initialize_cache_range = range;
    open_cfw_test_mram_initialize_cache_all = all;
    return open_cfw_test_mram_initialize_cache_result;
}

void open_cfw_test_mram_initialize_load(unsigned char *records)
{
    open_cfw_test_mram_initialize_order_append(2U);
    open_cfw_test_mram_initialize_load_records = records;
}

void open_cfw_test_mram_initialize_sync(void)
{
    open_cfw_test_mram_initialize_order_append(3U);
}

void open_cfw_test_mram_initialize_dump(
    const unsigned char *record,
    unsigned int index
)
{
    open_cfw_test_mram_initialize_order_append(4U + index);
    if (open_cfw_test_mram_initialize_dump_count < 10U) {
        open_cfw_test_mram_initialize_dump_records[
            open_cfw_test_mram_initialize_dump_count
        ] = (open_cfw_mram_initialize_uintptr)record;
        open_cfw_test_mram_initialize_dump_indices[
            open_cfw_test_mram_initialize_dump_count
        ] = index;
    }
    ++open_cfw_test_mram_initialize_dump_count;
}
