#include <assert.h>
#include <stdint.h>
#define OPEN_CFW_SMP_LEGACY_SM_HOST 1
#include "../../components/apollo_main/core_overlay/cordio_smp_legacy_sm.c"

volatile struct open_cfw_smp_legacy_sm_control_block
    open_cfw_smp_legacy_sm_host_control_block;

uint8_t open_cfw_cordio_smp_act_process_pairing(
    void *ccb, uint8_t *oob, uint8_t *display)
{ (void)ccb; *oob = 0U; *display = 0U; return 1U; }
void open_cfw_cordio_smp_act_authentication_request(
    void *ccb, uint8_t oob, uint8_t display)
{ (void)ccb; (void)oob; (void)display; }

int main(void)
{
    open_cfw_cordio_smpi_initialize();
    assert((uintptr_t)open_cfw_smp_legacy_sm_host_control_block.master_interface ==
        0x0078C344U);
    assert(open_cfw_smp_legacy_sm_host_control_block.process_pairing ==
        open_cfw_cordio_smp_act_process_pairing);
    assert(open_cfw_smp_legacy_sm_host_control_block.process_authentication ==
        open_cfw_cordio_smp_act_authentication_request);
    open_cfw_cordio_smpr_initialize();
    assert((uintptr_t)open_cfw_smp_legacy_sm_host_control_block.slave_interface ==
        0x0078C4ACU);
    assert(open_cfw_cordio_smp_legacy_dispatch[0] == 0xE8U);
    assert(open_cfw_cordio_smp_legacy_dispatch[704] == 0U);
    return 0;
}
