/* C replacement for the S140 interrupt-vector forwarding service.
 * With a source-built controller there is no MBR/SoftDevice vector relay;
 * the Cortex-M4 VTOR directly selects the active application or DFU table.
 */
#include "nrf_sdm.h"
#include "nrf.h"
#include "nrf_error.h"

#if defined(SVCALL_AS_NORMAL_FUNCTION)
uint32_t sd_softdevice_vector_table_base_set(uint32_t address)
{
    uint32_t interrupt_mask = __get_PRIMASK();
    __disable_irq();
    SCB->VTOR = address;
    __DSB();
    __ISB();
    __set_PRIMASK(interrupt_mask);
    return NRF_SUCCESS;
}
#endif
