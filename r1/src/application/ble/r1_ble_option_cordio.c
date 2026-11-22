/* R1's one BLE option on the source-built Cordio controller. */
#if defined(R1_CORDIO_RTC0)
#include "ble.h"
#include "nrf_error.h"

uint32_t sd_ble_opt_set(uint32_t option_id, ble_opt_t const *option)
{
    if (option == 0) return NRF_ERROR_INVALID_ADDR;
    if (option_id != BLE_COMMON_OPT_CONN_EVT_EXT)
        return NRF_ERROR_NOT_SUPPORTED;
    if (option->common_opt.conn_evt_ext.enable != 1u)
        return NRF_ERROR_NOT_SUPPORTED;
    /* Cordio's lctrExceededMaxDur checks time remaining before the next
     * scheduled radio operation for every packet. That is the extended
     * connection-event behavior R1 requests during BLE initialization. */
    return NRF_SUCCESS;
}
#endif
