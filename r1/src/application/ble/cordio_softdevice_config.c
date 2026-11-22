/* R1's Nordic BLE resource contract for the source-built Cordio candidate.
 * This owns only configuration and enable; BLE services/events still require
 * a real adapter before the image can operate on hardware. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stdint.h>

#include "ble.h"
#include "nrf_error.h"
#include "nrf_sdm.h"
#include "nrf_sdh.h"
#include "sdk_config.h"
#include "cordio_controller_bootstrap.h"
#include "cordio_lifecycle_hw.h"
#include "cordio_host_bootstrap.h"
#include "r1_wsf_task.h"
#include "r1_flash_cordio.h"

extern uint32_t __data_start__[];
extern void LlGetVersion(uint16_t *company_id, uint8_t *bluetooth_version,
                         uint16_t *implementation_revision);

_Static_assert(NRF_SDH_BLE_PERIPHERAL_LINK_COUNT == 3 &&
               NRF_SDH_BLE_CENTRAL_LINK_COUNT == 0 &&
               NRF_SDH_BLE_TOTAL_LINK_COUNT == 3 &&
               NRF_SDH_BLE_GAP_EVENT_LENGTH == 6 &&
               NRF_SDH_BLE_GATT_MAX_MTU_SIZE == 247 &&
               NRF_SDH_BLE_VS_UUID_COUNT == 2 &&
               NRF_SDH_BLE_GATTS_ATTR_TAB_SIZE == 2048 &&
               NRF_SDH_BLE_SERVICE_CHANGED == 1,
               "R1 Nordic resources changed; review the Cordio allocation");
_Static_assert(NRF_SDH_CLOCK_LF_SRC == 0 &&
               NRF_SDH_CLOCK_LF_RC_CTIV == 16 &&
               NRF_SDH_CLOCK_LF_RC_TEMP_CTIV == 2 &&
               NRF_SDH_CLOCK_LF_ACCURACY == 1,
               "R1 RC LFCLK contract changed; review the Cordio clock owner");

enum {
    CFG_GAP = 1u << 0,
    CFG_ROLES = 1u << 1,
    CFG_GATT = 1u << 2,
    CFG_UUID = 1u << 3,
    CFG_ATTRS = 1u << 4,
    CFG_CHANGED = 1u << 5,
    CFG_GATTS = 1u << 6,
    CFG_REQUIRED = (1u << 7) - 1u
};

static uint8_t configured;
static bool manager_enabled;
static bool enabled;
static bool enable_attempted;
static bool shutdown_pending;
static bool shutdown_ready;
static nrf_fault_handler_t manager_fault_handler;

static bool r1_cordio_disable_request(nrf_sdh_req_evt_t request,
                                       void *context)
{
    (void)context;
    if (request != NRF_SDH_EVT_DISABLE_REQUEST || !enabled ||
        shutdown_ready) return true;
    if (r1_cordio_flash_busy()) {
        r1_cordio_flash_wait_for_shutdown();
        return false;
    }
    if (!shutdown_pending) {
        shutdown_pending = true;
        r1_cordio_host_request_shutdown();
    }
    return false;
}

NRF_SDH_REQUEST_OBSERVER(r1_cordio_shutdown_observer, 0) = {
    .handler = r1_cordio_disable_request,
    .p_context = 0,
};

void r1_cordio_softdevice_reset_complete(void)
{
    if (!shutdown_pending) return;
    shutdown_ready = true;
    /* The reset callback runs in WSF task context, not an interrupt.
     * Nordic will reissue the disable request before entering its critical
     * region and the observer above will now allow it to proceed. */
    if (nrf_sdh_request_continue() == NRF_SUCCESS && !manager_enabled)
        r1_cordio_wsf_task_stop_request();
}

uint32_t sd_softdevice_enable(nrf_clock_lf_cfg_t const *clock,
                              nrf_fault_handler_t fault_handler)
{
    if (manager_enabled) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (clock == 0 || ((uintptr_t)clock & 3u) != 0u ||
        fault_handler == 0) {
        return NRF_ERROR_INVALID_ADDR;
    }
    if (clock->source != NRF_SDH_CLOCK_LF_SRC ||
        clock->rc_ctiv != NRF_SDH_CLOCK_LF_RC_CTIV ||
        clock->rc_temp_ctiv != NRF_SDH_CLOCK_LF_RC_TEMP_CTIV ||
        clock->accuracy != NRF_SDH_CLOCK_LF_ACCURACY) {
        return NRF_ERROR_INVALID_PARAM;
    }
    /* The R1 FreeRTOS RTC0 tick requested LFCLK before the manager thread
     * reached this function. A clock-start wait inside the SDK critical
     * region could deadlock, so fail if that startup contract was broken. */
    if (!r1_cordio_lfclk_is_running()) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (!r1_cordio_sd_evt_irq_prepare()) {
        return NRF_ERROR_SDM_INCORRECT_INTERRUPT_CONFIGURATION;
    }
    manager_fault_handler = fault_handler;
    manager_enabled = true;
    return NRF_SUCCESS;
}

uint32_t sd_ble_cfg_set(uint32_t cfg_id, ble_cfg_t const *cfg,
                        uint32_t app_ram_base)
{
    if (!manager_enabled || enabled || enable_attempted) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (cfg == 0 || ((uintptr_t)cfg & 3u) != 0u) {
        return NRF_ERROR_INVALID_ADDR;
    }
    if (app_ram_base != (uint32_t)(uintptr_t)__data_start__) {
        return NRF_ERROR_NO_MEM;
    }

    uint8_t bit;
    switch (cfg_id) {
    case BLE_CONN_CFG_GAP:
        bit = CFG_GAP;
        if (cfg->conn_cfg.conn_cfg_tag != 1u ||
            cfg->conn_cfg.params.gap_conn_cfg.conn_count != 3u ||
            cfg->conn_cfg.params.gap_conn_cfg.event_length != 6u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    case BLE_GAP_CFG_ROLE_COUNT:
        bit = CFG_ROLES;
        if (cfg->gap_cfg.role_count_cfg.periph_role_count != 3u ||
            cfg->gap_cfg.role_count_cfg.central_role_count != 0u ||
            cfg->gap_cfg.role_count_cfg.central_sec_count != 0u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    case BLE_CONN_CFG_GATT:
        bit = CFG_GATT;
        if (cfg->conn_cfg.conn_cfg_tag != 1u ||
            cfg->conn_cfg.params.gatt_conn_cfg.att_mtu != 247u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    case BLE_COMMON_CFG_VS_UUID:
        bit = CFG_UUID;
        if (cfg->common_cfg.vs_uuid_cfg.vs_uuid_count != 2u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    case BLE_GATTS_CFG_ATTR_TAB_SIZE:
        bit = CFG_ATTRS;
        if (cfg->gatts_cfg.attr_tab_size.attr_tab_size != 2048u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    case BLE_GATTS_CFG_SERVICE_CHANGED:
        bit = CFG_CHANGED;
        if (cfg->gatts_cfg.service_changed.service_changed != 1u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    case BLE_CONN_CFG_GATTS:
        bit = CFG_GATTS;
        if (cfg->conn_cfg.conn_cfg_tag != 1u ||
            cfg->conn_cfg.params.gatts_conn_cfg.hvn_tx_queue_size != 4u) {
            return NRF_ERROR_INVALID_PARAM;
        }
        break;
    default:
        return NRF_ERROR_INVALID_PARAM;
    }
    configured |= bit;
    return NRF_SUCCESS;
}

uint32_t sd_ble_enable(uint32_t *app_ram_base)
{
    if (!manager_enabled || enabled || enable_attempted) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (app_ram_base == 0 || ((uintptr_t)app_ram_base & 3u) != 0u) {
        return NRF_ERROR_INVALID_ADDR;
    }
    const uint32_t required_start = (uint32_t)(uintptr_t)__data_start__;
    if (*app_ram_base != required_start) {
        *app_ram_base = required_start;
        return NRF_ERROR_NO_MEM;
    }
    if (configured != CFG_REQUIRED) {
        return NRF_ERROR_INVALID_STATE;
    }
    enable_attempted = true;
    if (!r1_cordio_controller_bootstrap()) {
        return NRF_ERROR_NO_MEM;
    }
    /* Flash scheduling belongs to the active image. The lower controller
     * bootstrap is also used by the source DFU bootloader, which cannot
     * call this application's flash service while updating its image. */
    r1_cordio_flash_register();
    r1_cordio_host_bootstrap();
    if (!r1_cordio_wsf_task_start()) {
        return NRF_ERROR_NO_MEM;
    }
    if (!r1_cordio_wsf_wait_until(r1_cordio_host_ready, 512u)) {
        return NRF_ERROR_TIMEOUT;
    }
    enabled = true;
    return NRF_SUCCESS;
}

uint32_t sd_ble_version_get(ble_version_t *version)
{
    if (!enabled) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (version == 0 || ((uintptr_t)version & 3u) != 0u) {
        return NRF_ERROR_INVALID_ADDR;
    }
    LlGetVersion(&version->company_id, &version->version_number,
                 &version->subversion_number);
    return NRF_SUCCESS;
}

uint32_t sd_softdevice_disable(void)
{
    if (!manager_enabled) return NRF_ERROR_INVALID_STATE;
    if (enabled && !shutdown_ready) return NRF_ERROR_BUSY;
    /* Cordio's DM_RESET_CMPL_IND follows the HCI/controller reset sequence.
     * It has closed links and stopped radio procedures before this call. */
    enabled = false;
    manager_enabled = false;
    shutdown_pending = false;
    shutdown_ready = false;
    return NRF_SUCCESS;
}
#endif
