/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Native host oracle for the Apollo protected-MRAM record deactivation
 * adapter.
 */

unsigned int open_cfw_test_mram_deactivate_update(
    const unsigned char *
);
unsigned int open_cfw_test_mram_deactivate_verify(
    const unsigned char *
);

#define OPEN_CFW_MRAM_DEACTIVATE_UPDATE(record) \
    open_cfw_test_mram_deactivate_update(record)
#define OPEN_CFW_MRAM_DEACTIVATE_VERIFY(record) \
    open_cfw_test_mram_deactivate_verify(record)

#include "../../components/apollo_main/core_overlay/mram_deactivate_record.c"

unsigned int open_cfw_test_mram_deactivate_order[4];
unsigned int open_cfw_test_mram_deactivate_order_count;
open_cfw_mram_deactivate_uintptr
    open_cfw_test_mram_deactivate_update_record;
open_cfw_mram_deactivate_uintptr
    open_cfw_test_mram_deactivate_verify_record;
unsigned int open_cfw_test_mram_deactivate_update_result;
unsigned int open_cfw_test_mram_deactivate_verify_result;
unsigned int open_cfw_test_mram_deactivate_update_flags;
unsigned int open_cfw_test_mram_deactivate_verify_flags;

void open_cfw_test_mram_deactivate_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_mram_deactivate_order[index] = 0U;
    }
    open_cfw_test_mram_deactivate_order_count = 0U;
    open_cfw_test_mram_deactivate_update_record = 0U;
    open_cfw_test_mram_deactivate_verify_record = 0U;
    open_cfw_test_mram_deactivate_update_result = 0U;
    open_cfw_test_mram_deactivate_verify_result = 0U;
    open_cfw_test_mram_deactivate_update_flags = 0U;
    open_cfw_test_mram_deactivate_verify_flags = 0U;
}

unsigned int open_cfw_test_mram_deactivate_update(
    const unsigned char *record
)
{
    open_cfw_test_mram_deactivate_order[
        open_cfw_test_mram_deactivate_order_count
    ] = 1U;
    ++open_cfw_test_mram_deactivate_order_count;
    open_cfw_test_mram_deactivate_update_record =
        (open_cfw_mram_deactivate_uintptr)record;
    open_cfw_test_mram_deactivate_update_flags =
        ((unsigned int)record[0x2FU] << 8U)
        | record[0x30U];
    return open_cfw_test_mram_deactivate_update_result;
}

unsigned int open_cfw_test_mram_deactivate_verify(
    const unsigned char *record
)
{
    open_cfw_test_mram_deactivate_order[
        open_cfw_test_mram_deactivate_order_count
    ] = 2U;
    ++open_cfw_test_mram_deactivate_order_count;
    open_cfw_test_mram_deactivate_verify_record =
        (open_cfw_mram_deactivate_uintptr)record;
    open_cfw_test_mram_deactivate_verify_flags =
        ((unsigned int)record[0x2FU] << 8U)
        | record[0x30U];
    return open_cfw_test_mram_deactivate_verify_result;
}
