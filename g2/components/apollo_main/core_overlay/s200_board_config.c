/* SPDX-License-Identifier: MIT */
/* Clean-room S200 board-dependent charger initialization policy. */

#include <stdint.h>

struct open_cfw_s200_board_record {
    uint8_t charger_family;
    uint8_t hardware_revision;
    uint16_t hardware_adc_value;
};

#ifndef OPEN_CFW_S200_BOARD_CONFIG_RECORD
const struct open_cfw_s200_board_record *
open_cfw_retained_s200_board_config_record(uint32_t selector);
#define OPEN_CFW_S200_BOARD_CONFIG_RECORD(selector) \
    open_cfw_retained_s200_board_config_record((selector))
#endif

#ifndef OPEN_CFW_S200_BOARD_CONFIG_NPMX_INIT
void open_cfw_retained_s200_board_config_npmx_init(void);
#define OPEN_CFW_S200_BOARD_CONFIG_NPMX_INIT() \
    open_cfw_retained_s200_board_config_npmx_init()
#endif

#ifndef OPEN_CFW_S200_BOARD_CONFIG_BQ25180_INIT
void open_cfw_bq25180_hardware_init(void);
#define OPEN_CFW_S200_BOARD_CONFIG_BQ25180_INIT() \
    open_cfw_bq25180_hardware_init()
#endif

#ifndef OPEN_CFW_S200_BOARD_CONFIG_BQ27427_INIT
void open_cfw_bq27427_hardware_init(void);
#define OPEN_CFW_S200_BOARD_CONFIG_BQ27427_INIT() \
    open_cfw_bq27427_hardware_init()
#endif

int open_cfw_s200_board_config_initialize(void)
{
    const struct open_cfw_s200_board_record *const record =
        OPEN_CFW_S200_BOARD_CONFIG_RECORD(3u);

    if (record->charger_family == 1u) {
        OPEN_CFW_S200_BOARD_CONFIG_NPMX_INIT();
    } else if (record->charger_family == 2u) {
        OPEN_CFW_S200_BOARD_CONFIG_BQ25180_INIT();
        OPEN_CFW_S200_BOARD_CONFIG_BQ27427_INIT();
    }
    return 0;
}
