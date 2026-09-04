/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_TEST_S200_BOARD_CONFIG_HOST_H
#define OPEN_CFW_TEST_S200_BOARD_CONFIG_HOST_H

struct open_cfw_s200_board_record;

extern unsigned int open_cfw_test_s200_selector_calls;
extern unsigned int open_cfw_test_s200_selector_argument;
extern unsigned int open_cfw_test_s200_npmx_calls;
extern unsigned int open_cfw_test_s200_bq25180_calls;
extern unsigned int open_cfw_test_s200_bq27427_calls;

void open_cfw_test_s200_board_reset(unsigned char charger_family,
                                    unsigned char hardware_revision,
                                    unsigned short hardware_adc_value);
const struct open_cfw_s200_board_record *
open_cfw_test_s200_board_record(unsigned int selector);
void open_cfw_test_s200_npmx_init(void);
void open_cfw_test_s200_bq25180_init(void);
void open_cfw_test_s200_bq27427_init(void);

#define OPEN_CFW_S200_BOARD_CONFIG_RECORD(selector) \
    open_cfw_test_s200_board_record((selector))
#define OPEN_CFW_S200_BOARD_CONFIG_NPMX_INIT() open_cfw_test_s200_npmx_init()
#define OPEN_CFW_S200_BOARD_CONFIG_BQ25180_INIT() open_cfw_test_s200_bq25180_init()
#define OPEN_CFW_S200_BOARD_CONFIG_BQ27427_INIT() open_cfw_test_s200_bq27427_init()

#endif
