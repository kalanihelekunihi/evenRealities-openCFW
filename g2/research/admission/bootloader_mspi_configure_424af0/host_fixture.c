/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_configure_candidate.h"

static uint8_t states[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_STATE_BYTES];
static open_cfw_mspi_registers registers[OPEN_CFW_MSPI_CONFIG_MODULES];
static open_cfw_mspi_config config;
static uint32_t handle_module;

static void put32(uint8_t *p,uint32_t v)
{ p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8U);p[2]=(uint8_t)(v>>16U);p[3]=(uint8_t)(v>>24U); }

void open_cfw_test_mspi_configure_reset(uint32_t module,uint32_t prefix,
                                        uint32_t size,uint32_t tcb,uint32_t clock_on_d4,
                                        uint32_t xip,uint32_t scrambling,uint32_t axi)
{
    uint32_t i,j;
    for(i=0U;i<OPEN_CFW_MSPI_CONFIG_MODULES;i++) {
        for(j=0U;j<OPEN_CFW_MSPI_CONFIG_STATE_BYTES;j++) states[i][j]=0xA5U;
        registers[i].dev0xip=xip;registers[i].dev0scrambling=scrambling;registers[i].dev0axi=axi;
    }
    handle_module=module;
    if(module<OPEN_CFW_MSPI_CONFIG_MODULES){put32(states[module],prefix);put32(states[module]+4U,module);}
    config.tcb_size_words=size;config.tcb_address=tcb;config.clock_on_d4=(uint8_t)clock_on_d4;
}

uint32_t open_cfw_test_mspi_configure_run(uint32_t null_handle)
{
    uint8_t *handle=(null_handle || handle_module>=OPEN_CFW_MSPI_CONFIG_MODULES)?(uint8_t *)0:states[handle_module];
    return open_cfw_bootloader_mspi_configure_424af0(handle,&config,states,registers);
}

uint32_t open_cfw_test_mspi_configure_state(uint32_t module,uint32_t offset,uint32_t width)
{
    uint8_t *p;if(module>=OPEN_CFW_MSPI_CONFIG_MODULES||offset>=OPEN_CFW_MSPI_CONFIG_STATE_BYTES)return 0xffffffffU;p=&states[module][offset];
    if(width==1U)return p[0];if(width==4U&&offset+4U<=OPEN_CFW_MSPI_CONFIG_STATE_BYTES)return (uint32_t)p[0]|((uint32_t)p[1]<<8U)|((uint32_t)p[2]<<16U)|((uint32_t)p[3]<<24U);return 0xffffffffU;
}

uint32_t open_cfw_test_mspi_configure_register(uint32_t module,uint32_t selector)
{
    if(module>=OPEN_CFW_MSPI_CONFIG_MODULES)return 0xffffffffU;
    if(selector==0U)return registers[module].dev0axi;if(selector==1U)return registers[module].dev0xip;if(selector==2U)return registers[module].dev0scrambling;return 0xffffffffU;
}
