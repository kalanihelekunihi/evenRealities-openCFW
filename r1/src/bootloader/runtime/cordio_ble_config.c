/* Nordic DFU's resource profile on the installed source Cordio controller.
 * The lower controller reserves capacity for the larger application profile;
 * this bootloader consumes one peripheral link and a smaller GATT table. */
#include <stdbool.h>
#include <stdint.h>
#include "ble.h"
#include "nrf_error.h"
#include "nrf_sdm.h"
#include "sdk_config.h"
#include "cordio_region_init.h"

#if defined(SVCALL_AS_NORMAL_FUNCTION)
extern uint32_t __data_start__[];
/* ATT service groups and pending authorized writes must outlive each event. */
static uint64_t dfu_attribute_arena[512];

_Static_assert(NRF_SDH_BLE_PERIPHERAL_LINK_COUNT == 1 &&
               NRF_SDH_BLE_CENTRAL_LINK_COUNT == 0 &&
               NRF_SDH_BLE_TOTAL_LINK_COUNT == 1 &&
               NRF_SDH_BLE_GAP_EVENT_LENGTH == 6 &&
               NRF_SDH_BLE_GATT_MAX_MTU_SIZE == 247 &&
               NRF_SDH_BLE_VS_UUID_COUNT == 1 &&
               NRF_SDH_BLE_GATTS_ATTR_TAB_SIZE == 1408 &&
               NRF_SDH_BLE_SERVICE_CHANGED == 0,
               "Review the source DFU Cordio resource profile");
_Static_assert(NRF_SDH_CLOCK_LF_SRC == 0 &&
               NRF_SDH_CLOCK_LF_RC_CTIV == 16 &&
               NRF_SDH_CLOCK_LF_RC_TEMP_CTIV == 2 &&
               NRF_SDH_CLOCK_LF_ACCURACY == 1,
               "Review the recovered R1 DFU LFCLK profile");

uint32_t sd_softdevice_enable(nrf_clock_lf_cfg_t const *clock,
                              nrf_fault_handler_t fault_handler)
{
    return r1_bootloader_cordio_dfu_manager_enable(clock, fault_handler);
}

bool r1_bootloader_ble_cfg_ready(void)
{
    return r1_bootloader_cordio_dfu_cfg_ready();
}

uint32_t sd_ble_cfg_set(uint32_t cfg_id, ble_cfg_t const *cfg,
                        uint32_t app_ram_base)
{
    if (cfg == 0 || ((uintptr_t)cfg & 3u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if (app_ram_base != (uint32_t)(uintptr_t)__data_start__)
        return NRF_ERROR_NO_MEM;

    return r1_bootloader_cordio_dfu_cfg_set(cfg_id, cfg);
}

uint32_t sd_ble_enable(uint32_t *app_ram_base)
{
    if (app_ram_base == 0 || ((uintptr_t)app_ram_base & 3u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    uint32_t required = (uint32_t)(uintptr_t)__data_start__;
    if (*app_ram_base != required) {
        *app_ram_base = required;
        return NRF_ERROR_NO_MEM;
    }
    return r1_bootloader_cordio_dfu_ble_enable(
        dfu_attribute_arena, sizeof(dfu_attribute_arena));
}

uint32_t sd_ble_user_mem_reply(uint16_t conn_handle,
                                ble_user_mem_block_t const *block)
{
    if (conn_handle != 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (block != 0 && (block->p_mem == 0 || block->len == 0u))
        return NRF_ERROR_INVALID_LENGTH;
    /* The DFU profile has no queued-write memory request and never issues
     * BLE_EVT_USER_MEM_REQUEST. No borrowed buffer can be accepted here. */
    return NRF_ERROR_INVALID_STATE;
}
#endif
