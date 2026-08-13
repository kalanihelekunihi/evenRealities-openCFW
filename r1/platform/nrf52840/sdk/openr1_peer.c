#include "openr1_peer.h"

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "ble_gap.h"
#include "nrf_error.h"
#include "peer_manager.h"
#include "peer_manager_handler.h"

#include "openr1/r1_runtime.h"

static uint32_t last_error;

extern r1_runtime *openr1_platform_runtime(void);

static r1_error on_role_selected(void *context, uint16_t connection,
                                 r1_peer_role role) {
    (void)context;
    if (role != R1_ROLE_PHONE) {
        return R1_OK;
    }
    pm_conn_sec_status_t status;
    ret_code_t error = pm_conn_sec_status_get(connection, &status);
    if (error != NRF_SUCCESS) {
        last_error = error;
        return R1_ERROR_STATE;
    }
    (void)r1_runtime_set_security(openr1_platform_runtime(), connection,
                                  status.encrypted != 0u,
                                  status.bonded != 0u,
                                  false);
    if (status.encrypted != 0u) {
        return R1_OK;
    }
    error = pm_conn_secure(connection, false);
    if (error == NRF_SUCCESS || error == NRF_ERROR_BUSY) {
        return R1_OK;
    }
    last_error = error;
    return R1_ERROR_STATE;
}

static void synchronize_runtime_security(uint16_t connection) {
    pm_conn_sec_status_t status;
    const ret_code_t error = pm_conn_sec_status_get(connection, &status);
    if (error != NRF_SUCCESS) {
        last_error = error;
        return;
    }
    /* Bond state is transport identity, not product authorization. */
    (void)r1_runtime_set_security(openr1_platform_runtime(), connection,
                                  status.encrypted != 0u,
                                  status.bonded != 0u,
                                  false);
}

static void on_peer_event(pm_evt_t const *event) {
    /* Keep Nordic's standard security/error and FDS recovery behavior upstream. */
    pm_handler_on_pm_evt(event);
    pm_handler_flash_clean(event);

    switch (event->evt_id) {
        case PM_EVT_CONN_SEC_CONFIG_REQ: {
            pm_conn_sec_config_t configuration = {.allow_repairing = true};
            pm_conn_sec_config_reply(event->conn_handle, &configuration);
            break;
        }
        case PM_EVT_BONDED_PEER_CONNECTED:
        case PM_EVT_CONN_SEC_SUCCEEDED:
        case PM_EVT_CONN_SEC_FAILED:
            synchronize_runtime_security(event->conn_handle);
            break;
        case PM_EVT_ERROR_UNEXPECTED:
            last_error = event->params.error_unexpected.error;
            break;
        case PM_EVT_PEER_DATA_UPDATE_FAILED:
            last_error = event->params.peer_data_update_failed.error;
            break;
        case PM_EVT_PEER_DELETE_FAILED:
            last_error = event->params.peer_delete_failed.error;
            break;
        case PM_EVT_PEERS_DELETE_FAILED:
            last_error = event->params.peers_delete_failed_evt.error;
            break;
        case PM_EVT_FLASH_GARBAGE_COLLECTION_FAILED:
            last_error = event->params.garbage_collection_failed.error;
            break;
        default:
            break;
    }
}

uint32_t openr1_peer_initialize(void) {
    ble_gap_sec_params_t security;
    memset(&security, 0, sizeof security);
    security.bond = 1u;
    security.mitm = 0u;
    security.lesc = 0u;
    security.keypress = 0u;
    security.io_caps = BLE_GAP_IO_CAPS_NONE;
    security.oob = 0u;
    security.min_key_size = 7u;
    security.max_key_size = 16u;
    security.kdist_own.enc = 1u;
    security.kdist_own.id = 1u;
    security.kdist_peer.enc = 1u;
    security.kdist_peer.id = 1u;

    ret_code_t error = pm_init();
    if (error == NRF_SUCCESS) {
        error = pm_sec_params_set(&security);
    }
    if (error == NRF_SUCCESS) {
        error = pm_register(on_peer_event);
    }
    if (error == NRF_SUCCESS) {
        r1_runtime_set_role_handler(
            openr1_platform_runtime(), on_role_selected, NULL);
    }
    last_error = error;
    return error;
}

uint32_t openr1_peer_last_error(void) {
    return last_error;
}
