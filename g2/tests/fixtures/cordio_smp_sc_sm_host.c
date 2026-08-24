#include <stdint.h>

#define OPEN_CFW_SMP_SC_SM_HOST 1
#include "../../components/apollo_main/core_overlay/cordio_smp_sc_sm.c"

volatile struct open_cfw_smp_sc_sm_control_block
    open_cfw_smp_sc_sm_host_control_block;
static uint32_t open_cfw_smp_sc_sm_init_calls;

void open_cfw_cordio_smp_sc_init(void)
{
    ++open_cfw_smp_sc_sm_init_calls;
}

void open_cfw_smp_sc_sm_host_reset(void)
{
    open_cfw_smp_sc_sm_host_control_block.slave_interface = 0;
    open_cfw_smp_sc_sm_host_control_block.master_interface = 0;
    open_cfw_smp_sc_sm_init_calls = 0;
}

uintptr_t open_cfw_smp_sc_sm_host_master(void)
{
    return (uintptr_t)open_cfw_smp_sc_sm_host_control_block.master_interface;
}

uintptr_t open_cfw_smp_sc_sm_host_slave(void)
{
    return (uintptr_t)open_cfw_smp_sc_sm_host_control_block.slave_interface;
}

uint32_t open_cfw_smp_sc_sm_host_init_calls(void)
{
    return open_cfw_smp_sc_sm_init_calls;
}
