/* One-link Nordic DFU resource contract carried in source-built lower flash.
 * The controller reserves the larger application's resources; this records
 * the bootloader's requested subset before its host is initialized. */
#if defined(R1_CORDIO_RTC0)
#include "cordio_dfu_config.h"
#include "nrf.h"
#include "nrf_drv_clock.h"
#include "nrf_error.h"
#include "nrf_soc.h"
#include "cordio_dfu_host.h"

enum {
    CFG_GAP = 1u << 0,
    CFG_ROLES = 1u << 1,
    CFG_GATT = 1u << 2,
    CFG_UUID = 1u << 3,
    CFG_ATTRS = 1u << 4,
    CFG_CHANGED = 1u << 5,
    CFG_REQUIRED = (1u << 6) - 1u
};

static uint8_t configured;
static bool manager_enabled;

uint32_t r1_cordio_dfu_manager_enable(nrf_clock_lf_cfg_t const *clock,
                                      nrf_fault_handler_t fault_handler)
{
    if (manager_enabled) return NRF_ERROR_INVALID_STATE;
    if (clock == 0 || ((uintptr_t)clock & 3u) != 0u ||
        fault_handler == 0) return NRF_ERROR_INVALID_ADDR;
    if (clock->source != 0u || clock->rc_ctiv != 16u ||
        clock->rc_temp_ctiv != 2u || clock->accuracy != 1u)
        return NRF_ERROR_INVALID_PARAM;
    if (NVIC_GetEnableIRQ(SD_EVT_IRQn) != 0u)
        return NRF_ERROR_SDM_INCORRECT_INTERRUPT_CONFIGURATION;
    NVIC_SetPriority(SD_EVT_IRQn, 6u);
    NVIC_ClearPendingIRQ(SD_EVT_IRQn);
    if (nrf_drv_clock_init() != NRF_SUCCESS)
        return NRF_ERROR_INVALID_STATE;
    nrf_drv_clock_lfclk_request(0);
    for (uint32_t remaining = 10000000u; remaining != 0u; --remaining) {
        if (nrf_drv_clock_lfclk_is_running()) {
            configured = 0u;
            manager_enabled = true;
            return NRF_SUCCESS;
        }
    }
    nrf_drv_clock_lfclk_release();
    return NRF_ERROR_TIMEOUT;
}

uint32_t r1_cordio_dfu_manager_disable(void)
{
    if (!manager_enabled) return NRF_ERROR_INVALID_STATE;
    /* Nordic calls this with interrupts masked. Disconnect and advertising
     * stop must already have drained through the DFU host's WSF dispatcher. */
    if (!r1_cordio_dfu_host_idle()) return NRF_ERROR_BUSY;
    NRF_RADIO->TASKS_DISABLE = 1u;
    uint32_t remaining = 100000u;
    while (NRF_RADIO->STATE != RADIO_STATE_STATE_Disabled && remaining != 0u)
        --remaining;
    if (remaining == 0u) return NRF_ERROR_BUSY;
    NRF_TIMER0->TASKS_STOP = 1u;
    NRF_TIMER1->TASKS_STOP = 1u;
    NRF_RTC1->TASKS_STOP = 1u;
    nrf_drv_clock_lfclk_release();
    NVIC_DisableIRQ(RADIO_IRQn);
    NVIC_DisableIRQ(TIMER0_IRQn);
    NVIC_DisableIRQ(TIMER1_IRQn);
    NVIC_DisableIRQ(CCM_AAR_IRQn);
    NVIC_DisableIRQ(RTC1_IRQn);
    NVIC_DisableIRQ(SD_EVT_IRQn);
    NVIC_ClearPendingIRQ(RADIO_IRQn);
    NVIC_ClearPendingIRQ(TIMER0_IRQn);
    NVIC_ClearPendingIRQ(TIMER1_IRQn);
    NVIC_ClearPendingIRQ(CCM_AAR_IRQn);
    NVIC_ClearPendingIRQ(RTC1_IRQn);
    NVIC_ClearPendingIRQ(SD_EVT_IRQn);
    configured = 0u;
    manager_enabled = false;
    return NRF_SUCCESS;
}

bool r1_cordio_dfu_cfg_ready(void)
{
    return manager_enabled && configured == CFG_REQUIRED;
}

uint32_t r1_cordio_dfu_cfg_set(uint32_t cfg_id, ble_cfg_t const *cfg)
{
    if (!manager_enabled) return NRF_ERROR_INVALID_STATE;
    if (cfg == 0) return NRF_ERROR_INVALID_ADDR;
    uint8_t bit;
    switch (cfg_id) {
    case BLE_CONN_CFG_GAP:
        bit = CFG_GAP;
        if (cfg->conn_cfg.conn_cfg_tag != 1u ||
            cfg->conn_cfg.params.gap_conn_cfg.conn_count != 1u ||
            cfg->conn_cfg.params.gap_conn_cfg.event_length != 6u)
            return NRF_ERROR_INVALID_PARAM;
        break;
    case BLE_GAP_CFG_ROLE_COUNT:
        bit = CFG_ROLES;
        if (cfg->gap_cfg.role_count_cfg.periph_role_count != 1u ||
            cfg->gap_cfg.role_count_cfg.central_role_count != 0u ||
            cfg->gap_cfg.role_count_cfg.central_sec_count != 0u)
            return NRF_ERROR_INVALID_PARAM;
        break;
    case BLE_CONN_CFG_GATT:
        bit = CFG_GATT;
        if (cfg->conn_cfg.conn_cfg_tag != 1u ||
            cfg->conn_cfg.params.gatt_conn_cfg.att_mtu != 247u)
            return NRF_ERROR_INVALID_PARAM;
        break;
    case BLE_COMMON_CFG_VS_UUID:
        bit = CFG_UUID;
        if (cfg->common_cfg.vs_uuid_cfg.vs_uuid_count != 1u)
            return NRF_ERROR_INVALID_PARAM;
        break;
    case BLE_GATTS_CFG_ATTR_TAB_SIZE:
        bit = CFG_ATTRS;
        if (cfg->gatts_cfg.attr_tab_size.attr_tab_size != 1408u)
            return NRF_ERROR_INVALID_PARAM;
        break;
    case BLE_GATTS_CFG_SERVICE_CHANGED:
        bit = CFG_CHANGED;
        if (cfg->gatts_cfg.service_changed.service_changed != 0u)
            return NRF_ERROR_INVALID_PARAM;
        break;
    default:
        return NRF_ERROR_INVALID_PARAM;
    }
    configured |= bit;
    return NRF_SUCCESS;
}
#endif
