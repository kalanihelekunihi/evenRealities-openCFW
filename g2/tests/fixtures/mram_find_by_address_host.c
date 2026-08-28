/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for Cordio AppDbFindByAddr.
 */

unsigned int open_cfw_test_mram_find_map_owner(unsigned int);
unsigned int open_cfw_test_mram_find_compare(
    const void *,
    const void *
);

unsigned char open_cfw_test_mram_find_records[10U * 200U];
volatile unsigned int open_cfw_test_mram_find_counter;

#define OPEN_CFW_MRAM_FIND_RECORDS open_cfw_test_mram_find_records
#define OPEN_CFW_MRAM_FIND_COUNTER (&open_cfw_test_mram_find_counter)
#define OPEN_CFW_MRAM_FIND_MAP_OWNER(owner) \
    open_cfw_test_mram_find_map_owner(owner)
#define OPEN_CFW_MRAM_FIND_COMPARE(record, address) \
    open_cfw_test_mram_find_compare((record), (address))

#include "../../components/apollo_main/core_overlay/mram_find_by_address.c"

unsigned int open_cfw_test_mram_find_mapping_enabled;
unsigned int open_cfw_test_mram_find_map_calls;
unsigned int open_cfw_test_mram_find_map_input;
unsigned int open_cfw_test_mram_find_map_output;
unsigned int open_cfw_test_mram_find_compare_calls;
unsigned int open_cfw_test_mram_find_compare_indices[10U];
unsigned int open_cfw_test_mram_find_null_compare_calls;

void open_cfw_test_mram_find_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 10U * 200U; ++index) {
        open_cfw_test_mram_find_records[index] = 0U;
    }
    for (index = 0U; index < 10U; ++index) {
        open_cfw_test_mram_find_compare_indices[index] = 0U;
    }
    open_cfw_test_mram_find_counter = 0U;
    open_cfw_test_mram_find_mapping_enabled = 0U;
    open_cfw_test_mram_find_map_calls = 0U;
    open_cfw_test_mram_find_map_input = 0U;
    open_cfw_test_mram_find_map_output = 0U;
    open_cfw_test_mram_find_compare_calls = 0U;
    open_cfw_test_mram_find_null_compare_calls = 0U;
}

unsigned int open_cfw_test_mram_find_map_owner(unsigned int owner)
{
    unsigned int result = (unsigned char)owner;

    ++open_cfw_test_mram_find_map_calls;
    open_cfw_test_mram_find_map_input = owner;
    if (open_cfw_test_mram_find_mapping_enabled != 0U) {
        if (result == 2U) {
            result = 0U;
        } else if (result == 3U) {
            result = 1U;
        }
    }
    open_cfw_test_mram_find_map_output = result;
    return result;
}

unsigned int open_cfw_test_mram_find_compare(
    const void *record_pointer,
    const void *address_pointer
)
{
    const unsigned char *record =
        (const unsigned char *)record_pointer;
    const unsigned char *address =
        (const unsigned char *)address_pointer;
    unsigned int record_index = (unsigned int)(
        record - open_cfw_test_mram_find_records
    ) / 200U;
    unsigned int index;

    if (open_cfw_test_mram_find_compare_calls < 10U) {
        open_cfw_test_mram_find_compare_indices[
            open_cfw_test_mram_find_compare_calls
        ] = record_index;
    }
    ++open_cfw_test_mram_find_compare_calls;
    if (address == (const unsigned char *)0) {
        ++open_cfw_test_mram_find_null_compare_calls;
        return 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        if (record[index] != address[index]) {
            return 0U;
        }
    }
    return 1U;
}
