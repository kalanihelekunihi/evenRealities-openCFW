/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the Cordio AppDbFindByLtkReq-style lookup.
 */

int open_cfw_test_mram_ltk_compare(
    const void *,
    const void *,
    unsigned int
);

unsigned char open_cfw_test_mram_ltk_records[10U * 200U];
volatile unsigned int open_cfw_test_mram_ltk_counter;

#define OPEN_CFW_MRAM_LTK_RECORDS open_cfw_test_mram_ltk_records
#define OPEN_CFW_MRAM_LTK_COUNTER (&open_cfw_test_mram_ltk_counter)
#define OPEN_CFW_MRAM_LTK_COMPARE(left, right, length) \
    open_cfw_test_mram_ltk_compare((left), (right), (length))

#include "../../components/apollo_main/core_overlay/mram_find_by_ltk_request.c"

unsigned int open_cfw_test_mram_ltk_compare_calls;
unsigned int open_cfw_test_mram_ltk_compare_indices[10U];
unsigned int open_cfw_test_mram_ltk_compare_lengths[10U];
unsigned int open_cfw_test_mram_ltk_null_compare_calls;

void open_cfw_test_mram_ltk_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 10U * 200U; ++index) {
        open_cfw_test_mram_ltk_records[index] = 0U;
    }
    for (index = 0U; index < 10U; ++index) {
        open_cfw_test_mram_ltk_compare_indices[index] = 0U;
        open_cfw_test_mram_ltk_compare_lengths[index] = 0U;
    }
    open_cfw_test_mram_ltk_counter = 0U;
    open_cfw_test_mram_ltk_compare_calls = 0U;
    open_cfw_test_mram_ltk_null_compare_calls = 0U;
}

int open_cfw_test_mram_ltk_compare(
    const void *left_pointer,
    const void *right_pointer,
    unsigned int length
)
{
    const unsigned char *left =
        (const unsigned char *)left_pointer;
    const unsigned char *right =
        (const unsigned char *)right_pointer;
    unsigned int record_index = (unsigned int)(
        left - open_cfw_test_mram_ltk_records - 0x44U
    ) / 200U;
    unsigned int index;

    if (open_cfw_test_mram_ltk_compare_calls < 10U) {
        open_cfw_test_mram_ltk_compare_indices[
            open_cfw_test_mram_ltk_compare_calls
        ] = record_index;
        open_cfw_test_mram_ltk_compare_lengths[
            open_cfw_test_mram_ltk_compare_calls
        ] = length;
    }
    ++open_cfw_test_mram_ltk_compare_calls;
    if (right == (const unsigned char *)0) {
        ++open_cfw_test_mram_ltk_null_compare_calls;
        return 1;
    }
    for (index = 0U; index < length; ++index) {
        if (left[index] != right[index]) {
            return (int)left[index] - (int)right[index];
        }
    }
    return 0;
}
