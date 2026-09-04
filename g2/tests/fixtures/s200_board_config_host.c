/* SPDX-License-Identifier: MIT */
#include "s200_board_config_host.h"

struct open_cfw_s200_board_record {
    unsigned char charger_family;
    unsigned char hardware_revision;
    unsigned short hardware_adc_value;
};

unsigned int open_cfw_test_s200_selector_calls;
unsigned int open_cfw_test_s200_selector_argument;
unsigned int open_cfw_test_s200_npmx_calls;
unsigned int open_cfw_test_s200_bq25180_calls;
unsigned int open_cfw_test_s200_bq27427_calls;
static struct open_cfw_s200_board_record open_cfw_test_s200_record;

void open_cfw_test_s200_board_reset(unsigned char charger_family,
                                    unsigned char hardware_revision,
                                    unsigned short hardware_adc_value)
{
    open_cfw_test_s200_selector_calls = 0u;
    open_cfw_test_s200_selector_argument = 0xffffffffu;
    open_cfw_test_s200_npmx_calls = 0u;
    open_cfw_test_s200_bq25180_calls = 0u;
    open_cfw_test_s200_bq27427_calls = 0u;
    open_cfw_test_s200_record.charger_family = charger_family;
    open_cfw_test_s200_record.hardware_revision = hardware_revision;
    open_cfw_test_s200_record.hardware_adc_value = hardware_adc_value;
}

const struct open_cfw_s200_board_record *
open_cfw_test_s200_board_record(unsigned int selector)
{
    ++open_cfw_test_s200_selector_calls;
    open_cfw_test_s200_selector_argument = selector;
    return &open_cfw_test_s200_record;
}

void open_cfw_test_s200_npmx_init(void) { ++open_cfw_test_s200_npmx_calls; }
void open_cfw_test_s200_bq25180_init(void) { ++open_cfw_test_s200_bq25180_calls; }
void open_cfw_test_s200_bq27427_init(void) { ++open_cfw_test_s200_bq27427_calls; }
