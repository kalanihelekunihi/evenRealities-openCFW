/* Stock Main ATT configuration: flash 0x0078d154, RAM pointer 0x200004b4. */
#include "att_api.h"

__attribute__((used, section(".g2_flash_0078d154")))
const attCfg_t g2_main_att_cfg_0078d154 = {
    15, 480, ATT_MAX_TRANS_TIMEOUT, 4
};

__attribute__((used, section(".g2_ram_200004b4")))
attCfg_t *pAttCfg = (attCfg_t *)&g2_main_att_cfg_0078d154;
