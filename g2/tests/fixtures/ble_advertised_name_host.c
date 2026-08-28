/* SPDX-License-Identifier: MIT */

static const unsigned char *open_cfw_test_serial_record;

unsigned char open_cfw_test_adv_recorded[32];
unsigned int open_cfw_test_adv_recorded_length;
unsigned int open_cfw_test_adv_call_count;

static void open_cfw_test_adv_stock_memcpy(
    void *destination,
    const void *source,
    unsigned int length
)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    unsigned int index;

    ++open_cfw_test_adv_call_count;
    open_cfw_test_adv_recorded_length = length;
    for (index = 0U; index < length; ++index) {
        output[index] = input[index];
    }
}

#define OPEN_CFW_ADV_NAME_STOCK_MEMCPY(destination, source, length) \
    open_cfw_test_adv_stock_memcpy((destination), (source), (length))
#define OPEN_CFW_ADV_NAME_SERIAL_RECORD_POINTER \
    (&open_cfw_test_serial_record)

#include "../../components/apollo_main/core_overlay/ble_advertised_name.c"

void open_cfw_test_adv_reset(void)
{
    unsigned int index;

    open_cfw_test_serial_record = (const unsigned char *)0;
    open_cfw_test_adv_recorded_length = 0U;
    open_cfw_test_adv_call_count = 0U;
    for (index = 0U; index < sizeof(open_cfw_test_adv_recorded); ++index) {
        open_cfw_test_adv_recorded[index] = 0xA5U;
    }
}

void open_cfw_test_adv_set_serial_record(const unsigned char *record)
{
    open_cfw_test_serial_record = record;
}

void open_cfw_test_adv_execute(
    const unsigned char *stock_suffix,
    unsigned int length
)
{
    open_cfw_copy_advertised_name_pair_suffix(
        open_cfw_test_adv_recorded,
        stock_suffix,
        length
    );
}
