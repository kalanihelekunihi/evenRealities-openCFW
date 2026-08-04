/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM conditional deactivation
 * adapter.
 */

typedef __UINTPTR_TYPE__ open_cfw_test_mram_deactivate_if_uintptr;

unsigned int open_cfw_test_mram_deactivate_if_call(
    unsigned char *
);

#define OPEN_CFW_MRAM_DEACTIVATE_IF_UNCONFIRMED(record) \
    open_cfw_test_mram_deactivate_if_call(record)

#include "../../components/apollo_main/core_overlay/mram_deactivate_if_unconfirmed.c"

unsigned int open_cfw_test_mram_deactivate_if_calls;
open_cfw_test_mram_deactivate_if_uintptr
    open_cfw_test_mram_deactivate_if_record;
unsigned int open_cfw_test_mram_deactivate_if_flag;
unsigned int open_cfw_test_mram_deactivate_if_result;

void open_cfw_test_mram_deactivate_if_reset(void)
{
    open_cfw_test_mram_deactivate_if_calls = 0U;
    open_cfw_test_mram_deactivate_if_record = 0U;
    open_cfw_test_mram_deactivate_if_flag = 0U;
    open_cfw_test_mram_deactivate_if_result = 0U;
}

unsigned int open_cfw_test_mram_deactivate_if_call(
    unsigned char *record
)
{
    ++open_cfw_test_mram_deactivate_if_calls;
    open_cfw_test_mram_deactivate_if_record =
        (open_cfw_test_mram_deactivate_if_uintptr)record;
    open_cfw_test_mram_deactivate_if_flag = record[0x30U];
    return open_cfw_test_mram_deactivate_if_result;
}
