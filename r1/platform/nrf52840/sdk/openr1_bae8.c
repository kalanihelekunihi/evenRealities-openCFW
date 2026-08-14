#include "openr1_bae8.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "ble.h"
#include "ble_srv_common.h"
#include "ble_conn_state.h"
#include "nrf_error.h"
#include "nrf_sdh_ble.h"

#include "openr1/r1_protocol.h"
#include "openr1/r1_connection_params.h"
#include "openr1/r1_runtime.h"
#include "openr1_advertising.h"
#include "openr1_scheduler.h"

#define OPENR1_BAE8_SERVICE_UUID UINT16_C(0x0001)
#define OPENR1_BAE8_CHANNEL1_RX_UUID UINT16_C(0x0010)
#define OPENR1_BAE8_CHANNEL1_TX_UUID UINT16_C(0x0011)
#define OPENR1_BAE8_CHANNEL2_RX_UUID UINT16_C(0x0012)
#define OPENR1_BAE8_CHANNEL2_TX_UUID UINT16_C(0x0013)
#define OPENR1_BAE8_OBSERVER_PRIORITY 2

typedef struct {
    bool active;
    bool channel1_notify;
    bool channel2_notify;
    uint16_t connection;
} openr1_ble_link;

typedef struct {
    uint8_t uuid_type;
    uint16_t service_handle;
    ble_gatts_char_handles_t channel1_rx;
    ble_gatts_char_handles_t channel1_tx;
    ble_gatts_char_handles_t channel2_rx;
    ble_gatts_char_handles_t channel2_tx;
    openr1_ble_link links[R1_RUNTIME_LINK_MAX];
    uint32_t last_error;
} openr1_bae8_service;

static openr1_bae8_service service;

extern r1_runtime *openr1_platform_runtime(void);

static openr1_ble_link *find_link(uint16_t connection) {
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        if (service.links[index].active &&
            service.links[index].connection == connection) {
            return &service.links[index];
        }
    }
    return NULL;
}

static openr1_ble_link *allocate_link(uint16_t connection) {
    openr1_ble_link *existing = find_link(connection);
    if (existing != NULL) {
        return existing;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        openr1_ble_link *link = &service.links[index];
        if (!link->active) {
            memset(link, 0, sizeof *link);
            link->active = true;
            link->connection = connection;
            return link;
        }
    }
    return NULL;
}

static void release_link(uint16_t connection) {
    openr1_ble_link *link = find_link(connection);
    if (link != NULL) {
        memset(link, 0, sizeof *link);
        link->connection = BLE_CONN_HANDLE_INVALID;
    }
}

static uint32_t add_characteristic(uint16_t uuid, bool write_without_response,
                                   bool notify, ble_gatts_char_handles_t *handles) {
    uint8_t initial = 0u;
    ble_add_char_params_t parameters;
    memset(&parameters, 0, sizeof parameters);
    parameters.uuid = uuid;
    parameters.uuid_type = service.uuid_type;
    parameters.max_len = R1_BLE_VALUE_MAX;
    parameters.init_len = 1u;
    parameters.p_init_value = &initial;
    parameters.is_var_len = true;
    parameters.char_props.write_wo_resp = write_without_response ? 1u : 0u;
    parameters.char_props.notify = notify ? 1u : 0u;
    parameters.read_access = SEC_NO_ACCESS;
    parameters.write_access = write_without_response ? SEC_OPEN : SEC_NO_ACCESS;
    parameters.cccd_write_access = notify ? SEC_OPEN : SEC_NO_ACCESS;
    return characteristic_add(service.service_handle, &parameters, handles);
}

static r1_tx_status transmit(void *context, const r1_tx_event *event) {
    (void)context;
    return openr1_bae8_transmit(event);
}

r1_tx_status openr1_bae8_transmit(const r1_tx_event *event) {
    if (event == NULL) {
        return R1_TX_DROP;
    }
    openr1_ble_link *link = find_link(event->connection);
    if (link == NULL || (event->channel != 1u && event->channel != 2u)) {
        return R1_TX_DROP;
    }
    const ble_gatts_char_handles_t *tx = event->channel == 1u
        ? &service.channel1_tx : &service.channel2_tx;
    uint8_t cccd[BLE_CCCD_VALUE_LEN] = {0u};
    ble_gatts_value_t cccd_value;
    memset(&cccd_value, 0, sizeof cccd_value);
    cccd_value.len = sizeof cccd;
    cccd_value.p_value = cccd;
    const uint32_t cccd_error = sd_ble_gatts_value_get(
        event->connection, tx->cccd_handle, &cccd_value);
    if (cccd_error != NRF_SUCCESS) {
        service.last_error = cccd_error;
        return R1_TX_DROP;
    }
    const bool notify = ble_srv_is_notification_enabled(cccd);
    if (event->channel == 1u) {
        link->channel1_notify = notify;
    } else {
        link->channel2_notify = notify;
    }
    if (!notify) {
        return R1_TX_DROP;
    }
    uint16_t length = (uint16_t)event->length;
    ble_gatts_hvx_params_t parameters;
    memset(&parameters, 0, sizeof parameters);
    parameters.handle = tx->value_handle;
    parameters.type = BLE_GATT_HVX_NOTIFICATION;
    parameters.p_len = &length;
    parameters.p_data = event->bytes;
    const uint32_t error = sd_ble_gatts_hvx(event->connection, &parameters);
    if (error == NRF_SUCCESS) {
        return R1_TX_SENT;
    }
    if (error == NRF_ERROR_RESOURCES) {
        return R1_TX_RESOURCES;
    }
    service.last_error = error;
    return R1_TX_DROP;
}

uint32_t openr1_bae8_request_phy_update(
    uint16_t connection, uint8_t transmit_phy, uint8_t receive_phy) {
    r1_phy_update_plan plan;
    const r1_error error = r1_connection_phy_update_plan(
        connection, ble_conn_state_status(connection) == BLE_CONN_STATUS_CONNECTED,
        transmit_phy, receive_phy, &plan);
    if (error != R1_OK || !plan.request_update) {
        return NRF_ERROR_INVALID_STATE;
    }
    const ble_gap_phys_t phys = {
        .tx_phys = plan.transmit_phy,
        .rx_phys = plan.receive_phy,
    };
    return sd_ble_gap_phy_update(plan.connection, &phys);
}

static bool is_cccd_write(const ble_gatts_evt_write_t *write,
                          const ble_gatts_char_handles_t *handles) {
    return write->handle == handles->cccd_handle && write->len == BLE_CCCD_VALUE_LEN;
}

static void on_write(uint16_t connection, const ble_gatts_evt_write_t *write) {
    openr1_ble_link *link = find_link(connection);
    if (link == NULL) {
        return;
    }
    if (write->handle == service.channel2_rx.value_handle) {
        if (write->op == BLE_GATTS_OP_WRITE_CMD && write->offset == 0u &&
            write->len <= R1_BLE_VALUE_MAX) {
            (void)r1_runtime_receive_eus(
                openr1_platform_runtime(), connection, write->data, write->len);
        }
        return;
    }
    if (write->handle == service.channel1_rx.value_handle) {
        /* Channel 1 stays unavailable until its bounded BC/eAT parser and policy are complete. */
        return;
    }
    if (is_cccd_write(write, &service.channel1_tx)) {
        link->channel1_notify = ble_srv_is_notification_enabled(write->data);
    } else if (is_cccd_write(write, &service.channel2_tx)) {
        link->channel2_notify = ble_srv_is_notification_enabled(write->data);
    }
}

static bool is_queued_write(uint8_t operation) {
    return operation == BLE_GATTS_OP_PREP_WRITE_REQ ||
           operation == BLE_GATTS_OP_EXEC_WRITE_REQ_NOW ||
           operation == BLE_GATTS_OP_EXEC_WRITE_REQ_CANCEL;
}

static void reject_queued_write(const ble_gatts_evt_t *gatts_event) {
    const ble_gatts_evt_rw_authorize_request_t *request =
        &gatts_event->params.authorize_request;
    if (request->type != BLE_GATTS_AUTHORIZE_TYPE_WRITE ||
        !is_queued_write(request->request.write.op)) {
        return;
    }
    ble_gatts_rw_authorize_reply_params_t reply;
    memset(&reply, 0, sizeof reply);
    reply.type = BLE_GATTS_AUTHORIZE_TYPE_WRITE;
    reply.params.write.gatt_status = BLE_GATT_STATUS_ATTERR_REQUEST_NOT_SUPPORTED;
    const uint32_t error = sd_ble_gatts_rw_authorize_reply(gatts_event->conn_handle, &reply);
    if (error != NRF_SUCCESS) {
        service.last_error = error;
    }
}

static void on_ble_event(ble_evt_t const *event, void *context) {
    (void)context;
    const uint16_t connection = event->evt.gap_evt.conn_handle;
    switch (event->header.evt_id) {
        case BLE_GAP_EVT_CONNECTED: {
            openr1_advertising_connection_established(
                event->evt.gap_evt.params.connected.role == BLE_GAP_ROLE_PERIPH);
            openr1_ble_link *link = allocate_link(connection);
            if (link == NULL ||
                r1_runtime_connect(openr1_platform_runtime(), connection) != R1_OK) {
                service.last_error = NRF_ERROR_NO_MEM;
            }
            break;
        }
        case BLE_GAP_EVT_DISCONNECTED: {
            openr1_scheduler_reset_credits(r1_runtime_connection_role(
                openr1_platform_runtime(), connection));
            r1_runtime_disconnect(openr1_platform_runtime(), connection);
            release_link(connection);
            /* A disconnected link frees its role; the recovered policy
               advertises while either role is unoccupied. */
            bool phone_occupied = false;
            bool glasses_occupied = false;
            r1_runtime_role_occupancy(openr1_platform_runtime(),
                                      &phone_occupied, &glasses_occupied);
            const uint32_t advertising_error =
                openr1_advertising_set_role_occupancy(
                    phone_occupied, glasses_occupied);
            if (advertising_error != NRF_SUCCESS) {
                service.last_error = advertising_error;
            }
            break;
        }
        case BLE_GATTS_EVT_WRITE:
            on_write(event->evt.gatts_evt.conn_handle,
                     &event->evt.gatts_evt.params.write);
            break;
        case BLE_GATTS_EVT_HVN_TX_COMPLETE:
            openr1_scheduler_complete_credits(
                r1_runtime_connection_role(openr1_platform_runtime(), connection),
                event->evt.gatts_evt.params.hvn_tx_complete.count);
            r1_runtime_hvn_complete(
                openr1_platform_runtime(),
                event->evt.gatts_evt.params.hvn_tx_complete.count);
            break;
        case BLE_GATTS_EVT_RW_AUTHORIZE_REQUEST:
            reject_queued_write(&event->evt.gatts_evt);
            break;
        default:
            break;
    }
}

NRF_SDH_BLE_OBSERVER(openr1_bae8_observer, OPENR1_BAE8_OBSERVER_PRIORITY,
                     on_ble_event, NULL);

uint32_t openr1_bae8_initialize(void) {
    static const ble_uuid128_t base = {
        .uuid128 = {0x1f, 0x9d, 0x32, 0xf7, 0xf1, 0x3a, 0x65, 0x8e,
                    0x03, 0x45, 0x05, 0x4f, 0x00, 0x00, 0xe8, 0xba}
    };
    memset(&service, 0, sizeof service);
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        service.links[index].connection = BLE_CONN_HANDLE_INVALID;
    }
    uint32_t error = sd_ble_uuid_vs_add(&base, &service.uuid_type);
    if (error != NRF_SUCCESS) {
        return error;
    }
    ble_uuid_t service_uuid = {
        .uuid = OPENR1_BAE8_SERVICE_UUID,
        .type = service.uuid_type,
    };
    error = sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY, &service_uuid,
                                     &service.service_handle);
    if (error == NRF_SUCCESS) {
        error = add_characteristic(OPENR1_BAE8_CHANNEL1_RX_UUID, true, false,
                                   &service.channel1_rx);
    }
    if (error == NRF_SUCCESS) {
        error = add_characteristic(OPENR1_BAE8_CHANNEL1_TX_UUID, false, true,
                                   &service.channel1_tx);
    }
    if (error == NRF_SUCCESS) {
        error = add_characteristic(OPENR1_BAE8_CHANNEL2_RX_UUID, true, false,
                                   &service.channel2_rx);
    }
    if (error == NRF_SUCCESS) {
        error = add_characteristic(OPENR1_BAE8_CHANNEL2_TX_UUID, false, true,
                                   &service.channel2_tx);
    }
    if (error == NRF_SUCCESS) {
        r1_runtime_set_transmit(openr1_platform_runtime(), transmit, NULL);
    }
    service.last_error = error;
    return error;
}

uint32_t openr1_bae8_last_error(void) {
    return service.last_error;
}
