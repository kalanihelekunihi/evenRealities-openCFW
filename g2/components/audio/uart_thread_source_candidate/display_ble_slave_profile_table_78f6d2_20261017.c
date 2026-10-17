/* Stock appSlaveCfg_t at Main ROM 0x78f6d2: connMax = 1. */
#include <stdint.h>
#include "app_api.h"

_Static_assert(sizeof(appSlaveCfg_t) == 1u, "Cordio slave config ABI");

__attribute__((used, section(".g2_flash_0078f6d2")))
const uint8_t audio_ble_slave_profile_table[sizeof(appSlaveCfg_t)] = {1u};
