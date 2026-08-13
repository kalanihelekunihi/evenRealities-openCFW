/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Cordio all-record diagnostic iterator.
 */

#include <string.h>

unsigned char *open_cfw_test_mram_dump_all_base(void);
void open_cfw_test_mram_dump_all_dump(
    const unsigned char *,
    unsigned int
);

#define OPEN_CFW_MRAM_DUMP_ALL_RECORDS_BASE() \
    open_cfw_test_mram_dump_all_base()
#define OPEN_CFW_MRAM_DUMP_ALL_RECORD(record, index) \
    open_cfw_test_mram_dump_all_dump((record), (index))

#include "../../components/apollo_main/core_overlay/mram_dump_all_records.c"

unsigned char open_cfw_test_mram_dump_all_records[2000];
unsigned int open_cfw_test_mram_dump_all_base_count;
open_cfw_mram_dump_all_uintptr
open_cfw_test_mram_dump_all_record_pointers[10];
unsigned int open_cfw_test_mram_dump_all_indices[10];
unsigned int open_cfw_test_mram_dump_all_dump_count;

void open_cfw_test_mram_dump_all_reset(void)
{
    memset(
        open_cfw_test_mram_dump_all_records,
        0,
        sizeof(open_cfw_test_mram_dump_all_records)
    );
    memset(
        open_cfw_test_mram_dump_all_record_pointers,
        0,
        sizeof(open_cfw_test_mram_dump_all_record_pointers)
    );
    memset(
        open_cfw_test_mram_dump_all_indices,
        0,
        sizeof(open_cfw_test_mram_dump_all_indices)
    );
    open_cfw_test_mram_dump_all_base_count = 0U;
    open_cfw_test_mram_dump_all_dump_count = 0U;
}

unsigned char *open_cfw_test_mram_dump_all_base(void)
{
    ++open_cfw_test_mram_dump_all_base_count;
    return open_cfw_test_mram_dump_all_records;
}

void open_cfw_test_mram_dump_all_dump(
    const unsigned char *record,
    unsigned int index
)
{
    unsigned int call = open_cfw_test_mram_dump_all_dump_count;

    if (call < 10U) {
        open_cfw_test_mram_dump_all_record_pointers[call] =
            (open_cfw_mram_dump_all_uintptr)record;
        open_cfw_test_mram_dump_all_indices[call] = index;
    }
    ++open_cfw_test_mram_dump_all_dump_count;
}
