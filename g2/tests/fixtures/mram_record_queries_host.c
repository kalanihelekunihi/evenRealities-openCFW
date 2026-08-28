/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Apollo protected-MRAM record query helpers.
 */

#include <string.h>

extern unsigned char open_cfw_test_mram_query_records[2000];

#define OPEN_CFW_MRAM_QUERY_RECORDS_ADDRESS \
    ((open_cfw_mram_query_uintptr) \
        (void *)open_cfw_test_mram_query_records)

#include "../../components/apollo_main/core_overlay/mram_record_queries.c"

unsigned char open_cfw_test_mram_query_records[2000];

void open_cfw_test_mram_query_reset(void)
{
    memset(
        open_cfw_test_mram_query_records,
        0,
        sizeof(open_cfw_test_mram_query_records)
    );
}
