/* WFE service for the source-built application and DFU bootloader.
 * Mirrors the pinned Nordic no-SoftDevice implementation. The stock
 * SoftDevice build continues to use its SVC gateway instead. */
#include "nrf_soc.h"
#include "nrf_error.h"

#if defined(SVCALL_AS_NORMAL_FUNCTION)
uint32_t sd_app_evt_wait(void)
{
    __WFE();
    return NRF_SUCCESS;
}
#endif
