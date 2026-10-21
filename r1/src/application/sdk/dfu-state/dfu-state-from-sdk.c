#include "nrf_sdh.h"
#include "nrf_power.h"
#include "nrf_pwr_mgmt.h"
#include "nrf_bootloader_info.h"
static void buttonless_dfu_sdh_state_observer(nrf_sdh_state_evt_t state, void * p_context)
{
    if (state == NRF_SDH_EVT_STATE_DISABLED)
    {
        // Softdevice was disabled before going into reset. Inform bootloader to skip CRC on next boot.
        nrf_power_gpregret2_set(BOOTLOADER_DFU_SKIP_CRC);

        //Go to system off.
        nrf_pwr_mgmt_shutdown(NRF_PWR_MGMT_SHUTDOWN_GOTO_SYSOFF);
    }
}

void (*const r1_dfu_state_compile_anchor)(nrf_sdh_state_evt_t,void *)=buttonless_dfu_sdh_state_observer;
