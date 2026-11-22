/* Initial Cordio DM to Nordic GAP event path for the R1 source candidate. */
#if defined(R1_CORDIO_RTC0)
#include <string.h>

#include "ble.h"
#include "nrf_error.h"
#include "nrf_soc.h"
#include "FreeRTOS.h"
#include "task.h"
#include "cordio_ble_event_bridge.h"
#include "r1_adv_bridge.h"
#include "r1_gap_service.h"

enum { R1_LINKS = 3, R1_EVENT_SLOTS = 8, R1_GAP_NAME = 3,
       R1_GATT_SC = 10, R1_GATT_SC_CCC = 11, R1_INITIAL_USER_HANDLE = 12,
       R1_EVENT_MAX_BYTES = BLE_EVT_LEN_MAX(247) };
typedef struct {
    uint8_t *event;
    uint16_t length;
} r1_event_slot_t;

/* Single producer: Cordio's WSF task. SDK polling is task-context, but both
 * BLE IO and the flash wait path may consume, so removal takes a short task
 * critical section. Release/acquire indices still protect producer handoff. */
static r1_event_slot_t slots[R1_EVENT_SLOTS];
static uint8_t head;
static uint8_t tail;
static uint16_t hci_handles[R1_LINKS];
static uint8_t active[R1_LINKS];
static uint8_t mtu_outbound[R1_LINKS];
static uint8_t mtu_inbound[R1_LINKS];
static uint8_t client_read_kind[R1_LINKS];
static uint16_t client_read_handle[R1_LINKS];
static uint16_t client_read_offset[R1_LINKS];
/* WSF is the sole producer. Keep its 2 KiB task stack clear of ATT payloads. */
static uint32_t read_event_words[R1_EVENT_MAX_BYTES / sizeof(uint32_t)];

static bool publish(const ble_evt_t *event, uint16_t length)
{
    if (event == 0 || length < sizeof(ble_evt_hdr_t) ||
        length > R1_EVENT_MAX_BYTES || event->header.evt_len != length)
        return false;
    uint8_t write = __atomic_load_n(&head, __ATOMIC_RELAXED);
    uint8_t read = __atomic_load_n(&tail, __ATOMIC_ACQUIRE);
    if ((uint8_t)(write - read) >= R1_EVENT_SLOTS) {
        return false;
    }
    uint8_t *copy = pvPortMalloc(length);
    if (copy == 0) return false;
    r1_event_slot_t *slot = &slots[write % R1_EVENT_SLOTS];
    memcpy(copy, event, length);
    slot->event = copy;
    slot->length = length;
    __atomic_store_n(&head, (uint8_t)(write + 1u), __ATOMIC_RELEASE);
    NVIC_SetPendingIRQ(SD_EVT_IRQn);
    return true;
}

bool r1_cordio_ble_event_publish(const void *event, uint16_t length)
{
    return publish((const ble_evt_t *)event, length);
}

static bool valid_link(uint8_t conn_id, uint16_t hci_handle)
{
    return conn_id >= 1u && conn_id <= R1_LINKS &&
           __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) != 0u &&
           hci_handles[conn_id - 1u] == hci_handle;
}

uint8_t r1_cordio_conn_id_from_nordic(uint16_t nordic_handle)
{
    if (nordic_handle >= R1_LINKS ||
        __atomic_load_n(&active[nordic_handle], __ATOMIC_ACQUIRE) == 0u) {
        return 0u;
    }
    return (uint8_t)(nordic_handle + 1u);
}

uint16_t r1_cordio_hci_handle_from_nordic(uint16_t nordic_handle)
{
    if (nordic_handle >= R1_LINKS ||
        __atomic_load_n(&active[nordic_handle], __ATOMIC_ACQUIRE) == 0u) {
        return BLE_CONN_HANDLE_INVALID;
    }
    return hci_handles[nordic_handle];
}

uint32_t sd_ble_gattc_exchange_mtu_request(uint16_t conn_handle,
                                           uint16_t client_rx_mtu)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (client_rx_mtu < BLE_GATT_ATT_MTU_DEFAULT || client_rx_mtu > 247u)
        return NRF_ERROR_INVALID_PARAM;
    if (__atomic_exchange_n(&mtu_outbound[conn_handle], 1u,
                            __ATOMIC_ACQ_REL) != 0u)
        return NRF_ERROR_BUSY;
    r1_cordio_att_mtu_request(conn_id, client_rx_mtu);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_exchange_mtu_reply(uint16_t conn_handle,
                                         uint16_t server_rx_mtu)
{
    if (r1_cordio_conn_id_from_nordic(conn_handle) == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (server_rx_mtu < BLE_GATT_ATT_MTU_DEFAULT || server_rx_mtu > 247u)
        return NRF_ERROR_INVALID_PARAM;
    if (server_rx_mtu != 247u) return NRF_ERROR_NOT_SUPPORTED;
    if (__atomic_exchange_n(&mtu_inbound[conn_handle], 0u,
                            __ATOMIC_ACQ_REL) == 0u)
        return NRF_ERROR_INVALID_STATE;
    /* Cordio's server sent the 247-byte response before its MTU callback.
     * The Nordic observer acknowledges that completed protocol operation. */
    return NRF_SUCCESS;
}

uint32_t sd_ble_gattc_read(uint16_t conn_handle, uint16_t handle,
                           uint16_t offset)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (handle == BLE_GATT_HANDLE_INVALID) return NRF_ERROR_INVALID_PARAM;
    if (__atomic_exchange_n(&client_read_kind[conn_handle], 1u,
                            __ATOMIC_ACQ_REL) != 0u) return NRF_ERROR_BUSY;
    client_read_handle[conn_handle] = handle;
    client_read_offset[conn_handle] = offset;
    r1_cordio_att_read_request(conn_id, handle, offset);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gattc_char_value_by_uuid_read(
    uint16_t conn_handle, ble_uuid_t const *uuid,
    ble_gattc_handle_range_t const *range)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (uuid == 0 || range == 0 ||
        ((uintptr_t)uuid & 1u) != 0u || ((uintptr_t)range & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if (uuid->type != BLE_UUID_TYPE_BLE) return NRF_ERROR_NOT_SUPPORTED;
    if (range->start_handle == 0u ||
        range->start_handle > range->end_handle)
        return NRF_ERROR_INVALID_PARAM;
    if (__atomic_exchange_n(&client_read_kind[conn_handle], 2u,
                            __ATOMIC_ACQ_REL) != 0u) return NRF_ERROR_BUSY;
    client_read_handle[conn_handle] = range->start_handle;
    client_read_offset[conn_handle] = 0u;
    r1_cordio_att_read_by_type_request(conn_id, range->start_handle,
                                        range->end_handle, uuid->uuid);
    return NRF_SUCCESS;
}

bool r1_cordio_att_read_response(uint8_t conn_id, uint8_t kind,
                                 uint8_t status, uint16_t handle,
                                 const uint8_t *data, uint16_t length)
{
    if (conn_id < 1u || conn_id > R1_LINKS ||
        __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) == 0u)
        return false;
    uint8_t link = (uint8_t)(conn_id - 1u);
    if (kind == 0u || kind > 2u ||
        __atomic_load_n(&client_read_kind[link], __ATOMIC_ACQUIRE) != kind ||
        (status == 0u && length != 0u && data == 0)) return false;
    ble_evt_t *event = (ble_evt_t *)read_event_words;
    memset(event, 0, sizeof(read_event_words));
    event->evt.gattc_evt.conn_handle = link;
    event->evt.gattc_evt.gatt_status = status == 0u ?
        BLE_GATT_STATUS_SUCCESS :
        (status <= 0x13u ? (uint16_t)(0x100u + status) : BLE_GATT_STATUS_UNKNOWN);
    event->evt.gattc_evt.error_handle = status == 0u ?
        BLE_GATT_HANDLE_INVALID : handle;
    uint16_t bytes;
    if (kind == 1u) {
        event->header.evt_id = BLE_GATTC_EVT_READ_RSP;
        ble_gattc_evt_read_rsp_t *response =
            &event->evt.gattc_evt.params.read_rsp;
        response->handle = client_read_handle[link];
        response->offset = client_read_offset[link];
        response->len = status == 0u ? length : 0u;
        bytes = (uint16_t)offsetof(ble_evt_t, evt.gattc_evt.params.read_rsp.data);
        if ((uint32_t)bytes + response->len > R1_EVENT_MAX_BYTES) return false;
        if (response->len != 0u) memcpy(response->data, data, response->len);
        bytes = (uint16_t)(bytes + response->len);
    } else {
        event->header.evt_id = BLE_GATTC_EVT_CHAR_VAL_BY_UUID_READ_RSP;
        ble_gattc_evt_char_val_by_uuid_read_rsp_t *response =
            &event->evt.gattc_evt.params.char_val_by_uuid_read_rsp;
        bytes = (uint16_t)offsetof(ble_evt_t,
            evt.gattc_evt.params.char_val_by_uuid_read_rsp.handle_value);
        if (status == 0u) {
            if (length < 3u || data[0] < 3u ||
                ((length - 1u) % data[0]) != 0u ||
                (uint32_t)bytes + length - 1u > R1_EVENT_MAX_BYTES)
                return false;
            response->count = (uint16_t)((length - 1u) / data[0]);
            response->value_len = (uint16_t)(data[0] - 2u);
            memcpy(response->handle_value, data + 1u, length - 1u);
            bytes = (uint16_t)(bytes + length - 1u);
        }
    }
    event->header.evt_len = bytes;
    bool accepted = publish(event, bytes);
    if (accepted)
        __atomic_store_n(&client_read_kind[link], 0u, __ATOMIC_RELEASE);
    return accepted;
}

bool r1_cordio_gatts_ccc_changed(uint8_t conn_id, uint16_t handle,
                                 uint16_t value)
{
    if (conn_id < 1u || conn_id > R1_LINKS ||
        __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) == 0u)
        return false;
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GATTS_EVT_WRITE;
    event.header.evt_len = (uint16_t)(offsetof(ble_evt_t,
        evt.gatts_evt.params.write.data) + 2u);
    event.evt.gatts_evt.conn_handle = (uint16_t)(conn_id - 1u);
    ble_gatts_evt_write_t *write = &event.evt.gatts_evt.params.write;
    write->handle = handle;
    write->uuid.type = BLE_UUID_TYPE_BLE;
    write->uuid.uuid = BLE_UUID_DESCRIPTOR_CLIENT_CHAR_CONFIG;
    write->op = BLE_GATTS_OP_WRITE_REQ;
    write->len = 2u;
    write->data[0] = (uint8_t)value;
    write->data[1] = (uint8_t)(value >> 8);
    return publish(&event, event.header.evt_len);
}

bool r1_cordio_gatts_write_event(uint8_t conn_id, uint16_t handle,
                                 uint8_t uuid_type, uint16_t uuid,
                                 uint8_t opcode, const uint8_t *data,
                                 uint16_t length, bool authorize)
{
    if (conn_id < 1u || conn_id > R1_LINKS ||
        __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) == 0u ||
        (length != 0u && data == 0) ||
        (opcode != 0x12u && opcode != 0x52u) ||
        (authorize && opcode != 0x12u)) return false;
    ble_evt_t *event = (ble_evt_t *)read_event_words;
    memset(event, 0, sizeof(read_event_words));
    event->evt.gatts_evt.conn_handle = (uint16_t)(conn_id - 1u);
    ble_gatts_evt_write_t *write;
    uint16_t bytes;
    if (authorize) {
        event->header.evt_id = BLE_GATTS_EVT_RW_AUTHORIZE_REQUEST;
        event->evt.gatts_evt.params.authorize_request.type =
            BLE_GATTS_AUTHORIZE_TYPE_WRITE;
        write = &event->evt.gatts_evt.params.authorize_request.request.write;
        bytes = (uint16_t)offsetof(ble_evt_t,
            evt.gatts_evt.params.authorize_request.request.write.data);
        write->auth_required = 1u;
    } else {
        event->header.evt_id = BLE_GATTS_EVT_WRITE;
        write = &event->evt.gatts_evt.params.write;
        bytes = (uint16_t)offsetof(ble_evt_t, evt.gatts_evt.params.write.data);
    }
    if ((uint32_t)bytes + length > R1_EVENT_MAX_BYTES) return false;
    write->handle = handle;
    write->uuid.type = uuid_type;
    write->uuid.uuid = uuid;
    write->op = opcode == 0x12u ? BLE_GATTS_OP_WRITE_REQ :
                                  BLE_GATTS_OP_WRITE_CMD;
    write->len = length;
    if (length != 0u) memcpy(write->data, data, length);
    event->header.evt_len = (uint16_t)(bytes + length);
    return publish(event, event->header.evt_len);
}

bool r1_cordio_gatts_tx_event(uint8_t conn_id, uint16_t handle,
                              bool indication, bool service_changed)
{
    if (conn_id < 1u || conn_id > R1_LINKS ||
        __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) == 0u)
        return false;
    ble_evt_t event = {0};
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gatts_evt.conn_handle = (uint16_t)(conn_id - 1u);
    if (indication) {
        event.header.evt_id = service_changed ? BLE_GATTS_EVT_SC_CONFIRM :
                                                BLE_GATTS_EVT_HVC;
        event.evt.gatts_evt.params.hvc.handle = handle;
    } else {
        event.header.evt_id = BLE_GATTS_EVT_HVN_TX_COMPLETE;
        event.evt.gatts_evt.params.hvn_tx_complete.count = 1u;
    }
    return publish(&event, (uint16_t)sizeof(event));
}

bool r1_cordio_att_mtu_updated(uint8_t conn_id, uint16_t mtu)
{
    if (conn_id < 1u || conn_id > R1_LINKS ||
        __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) == 0u)
        return false;
    uint8_t link = (uint8_t)(conn_id - 1u);
    ble_evt_t event = {0};
    event.header.evt_len = (uint16_t)sizeof(event);
    if (__atomic_exchange_n(&mtu_outbound[link], 0u, __ATOMIC_ACQ_REL) != 0u) {
        event.header.evt_id = BLE_GATTC_EVT_EXCHANGE_MTU_RSP;
        event.evt.gattc_evt.conn_handle = link;
        event.evt.gattc_evt.gatt_status = BLE_GATT_STATUS_SUCCESS;
        event.evt.gattc_evt.error_handle = BLE_GATT_HANDLE_INVALID;
        event.evt.gattc_evt.params.exchange_mtu_rsp.server_rx_mtu = mtu;
    } else {
        __atomic_store_n(&mtu_inbound[link], 1u, __ATOMIC_RELEASE);
        event.header.evt_id = BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST;
        event.evt.gatts_evt.conn_handle = link;
        event.evt.gatts_evt.params.exchange_mtu_request.client_rx_mtu = mtu;
    }
    return publish(&event, (uint16_t)sizeof(event));
}

uint32_t sd_ble_gatts_initial_user_handle_get(uint16_t *handle)
{
    if (handle == 0 || ((uintptr_t)handle & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    *handle = R1_INITIAL_USER_HANDLE;
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_attr_get(uint16_t handle, ble_uuid_t *uuid,
                                ble_gatts_attr_md_t *metadata)
{
    static const uint16_t uuids[R1_GATT_SC_CCC] = {
        0x2800, 0x2803, 0x2a00, 0x2803, 0x2a01, 0x2803,
        0x2a04, 0x2800, 0x2803, 0x2a05, 0x2902
    };
    if ((uuid == 0 && metadata == 0) ||
        (uuid != 0 && ((uintptr_t)uuid & 1u) != 0u) ||
        (metadata != 0 && ((uintptr_t)metadata & 1u) != 0u))
        return NRF_ERROR_INVALID_ADDR;
    if (handle == 0u || handle >= R1_INITIAL_USER_HANDLE)
        return NRF_ERROR_NOT_FOUND;
    if (uuid != 0) {
        uuid->type = BLE_UUID_TYPE_BLE;
        uuid->uuid = uuids[handle - 1u];
    }
    if (metadata != 0) {
        memset(metadata, 0, sizeof(*metadata));
        BLE_GAP_CONN_SEC_MODE_SET_OPEN(&metadata->read_perm);
        if (handle == R1_GAP_NAME || handle == R1_GATT_SC_CCC)
            BLE_GAP_CONN_SEC_MODE_SET_OPEN(&metadata->write_perm);
        if (handle == R1_GATT_SC)
            BLE_GAP_CONN_SEC_MODE_SET_NO_ACCESS(&metadata->read_perm);
        metadata->vlen = handle == R1_GAP_NAME;
        metadata->vloc = BLE_GATTS_VLOC_STACK;
    }
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_value_get(uint16_t conn_handle, uint16_t handle,
                                 ble_gatts_value_t *value)
{
    if (value == 0 || ((uintptr_t)value & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    uint8_t conn_id = 0u;
    if (r1_cordio_atts_is_ccc(handle)) {
        conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
        if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    }
    uint16_t actual = 0u;
    uint8_t result = r1_cordio_atts_value_snapshot(conn_id, handle,
            value->offset, value->p_value,
            value->p_value != 0 ? value->len : 0u, &actual);
    if (result == 1u) return NRF_ERROR_NOT_FOUND;
    if (result == 2u) return NRF_ERROR_INVALID_PARAM;
    value->len = actual;
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_disconnect(uint16_t conn_handle, uint8_t hci_status_code)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (hci_status_code != BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION &&
        hci_status_code != BLE_HCI_CONN_INTERVAL_UNACCEPTABLE) {
        return NRF_ERROR_INVALID_PARAM;
    }
    r1_cordio_dm_disconnect(conn_id, hci_status_code);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_data_length_update(
    uint16_t conn_handle, ble_gap_data_length_params_t const *parameters,
    ble_gap_data_length_limitation_t *limitation)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (limitation != 0 && ((uintptr_t)limitation & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if (limitation != 0) memset(limitation, 0, sizeof(*limitation));
    uint16_t tx_octets = 251u;
    uint16_t tx_time = 2120u;
    if (parameters != 0) {
        if (((uintptr_t)parameters & 1u) != 0u) return NRF_ERROR_INVALID_ADDR;
        if (parameters->max_tx_octets != BLE_GAP_DATA_LENGTH_AUTO)
            tx_octets = parameters->max_tx_octets;
        if (parameters->max_tx_time_us != BLE_GAP_DATA_LENGTH_AUTO)
            tx_time = parameters->max_tx_time_us;
        if (tx_octets < 27u || tx_time < 328u ||
            (parameters->max_rx_octets != 0u && parameters->max_rx_octets < 27u) ||
            (parameters->max_rx_time_us != 0u && parameters->max_rx_time_us < 328u))
            return NRF_ERROR_INVALID_PARAM;
        if (tx_octets > 251u || parameters->max_rx_octets > 251u ||
            tx_time > 2120u || parameters->max_rx_time_us > 2120u) {
            if (limitation != 0) {
                if (tx_octets > 251u) limitation->tx_payload_limited_octets = tx_octets - 251u;
                if (parameters->max_rx_octets > 251u)
                    limitation->rx_payload_limited_octets = parameters->max_rx_octets - 251u;
                if (tx_time > 2120u || parameters->max_rx_time_us > 2120u)
                    limitation->tx_rx_time_limited_us =
                        (tx_time > parameters->max_rx_time_us ? tx_time : parameters->max_rx_time_us) - 2120u;
            }
            return NRF_ERROR_NOT_SUPPORTED;
        }
    }
    r1_cordio_dm_set_data_length(conn_id, tx_octets, tx_time);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_conn_param_update(uint16_t conn_handle,
                                     ble_gap_conn_params_t const *parameters)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    ble_gap_conn_params_t preferred;
    if (parameters == 0) {
        r1_cordio_gap_ppcp_get((uint8_t *)&preferred);
        parameters = &preferred;
    }
    if (((uintptr_t)parameters & 1u) != 0u) return NRF_ERROR_INVALID_ADDR;
    uint16_t min = parameters->min_conn_interval;
    uint16_t max = parameters->max_conn_interval;
    uint16_t latency = parameters->slave_latency;
    uint16_t timeout = parameters->conn_sup_timeout;
    if (min < 6u || max > 3200u || min > max || latency > 499u ||
        timeout < 10u || timeout > 3200u ||
        (uint32_t)timeout * 8u <= (uint32_t)(latency + 1u) * max * 2u) {
        return NRF_ERROR_INVALID_PARAM;
    }
    r1_cordio_dm_conn_param_update(conn_id, min, max, latency, timeout);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_phy_update(uint16_t conn_handle,
                               ble_gap_phys_t const *phys)
{
    uint8_t conn_id = r1_cordio_conn_id_from_nordic(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (phys == 0) return NRF_ERROR_INVALID_ADDR;
    uint8_t tx = phys->tx_phys;
    uint8_t rx = phys->rx_phys;
    if ((tx & (uint8_t)~BLE_GAP_PHYS_SUPPORTED) != 0u ||
        (rx & (uint8_t)~BLE_GAP_PHYS_SUPPORTED) != 0u) {
        return NRF_ERROR_INVALID_PARAM;
    }
    uint8_t all = 0u;
    if (tx == BLE_GAP_PHY_AUTO) all |= 1u;
    if (rx == BLE_GAP_PHY_AUTO) all |= 2u;
    r1_cordio_dm_set_phy(conn_id, all, tx, rx);
    return NRF_SUCCESS;
}

bool r1_cordio_gap_connected(uint8_t conn_id, uint16_t hci_handle,
                            uint8_t role, uint8_t addr_type,
                            const uint8_t peer_addr[6], uint16_t interval,
                            uint16_t latency, uint16_t timeout)
{
    if (conn_id < 1u || conn_id > R1_LINKS || peer_addr == 0 ||
        __atomic_load_n(&active[conn_id - 1u], __ATOMIC_ACQUIRE) != 0u ||
        role != 1u || addr_type > 3u) {
        return false;
    }
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_CONNECTED;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = (uint16_t)(conn_id - 1u);
    ble_gap_evt_connected_t *connected = &event.evt.gap_evt.params.connected;
    connected->role = BLE_GAP_ROLE_PERIPH;
    connected->peer_addr.addr_id_peer = (addr_type >= 2u);
    connected->peer_addr.addr_type = (addr_type == 0u || addr_type == 2u) ?
                                     BLE_GAP_ADDR_TYPE_PUBLIC :
                                     BLE_GAP_ADDR_TYPE_RANDOM_STATIC;
    if (addr_type == 1u) {
        uint8_t kind = peer_addr[5] >> 6;
        if (kind == 0u) connected->peer_addr.addr_type = BLE_GAP_ADDR_TYPE_RANDOM_PRIVATE_NON_RESOLVABLE;
        else if (kind == 1u) connected->peer_addr.addr_type = BLE_GAP_ADDR_TYPE_RANDOM_PRIVATE_RESOLVABLE;
    }
    memcpy(connected->peer_addr.addr, peer_addr, 6u);
    connected->conn_params.min_conn_interval = interval;
    connected->conn_params.max_conn_interval = interval;
    connected->conn_params.slave_latency = latency;
    connected->conn_params.conn_sup_timeout = timeout;
    /* The corresponding advertising set is always set 0 in the R1 profile.
     * Its buffer ownership is supplied by the advertising adapter later. */
    connected->adv_handle = 0u;
    r1_cordio_adv_connected(connected);
    hci_handles[conn_id - 1u] = hci_handle;
    __atomic_store_n(&active[conn_id - 1u], 1u, __ATOMIC_RELEASE);
    if (!publish(&event, (uint16_t)sizeof(event))) {
        __atomic_store_n(&active[conn_id - 1u], 0u, __ATOMIC_RELEASE);
        return false;
    }
    return true;
}

bool r1_cordio_gap_disconnected(uint8_t conn_id, uint16_t hci_handle,
                               uint8_t reason)
{
    if (!valid_link(conn_id, hci_handle)) return false;
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_DISCONNECTED;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = (uint16_t)(conn_id - 1u);
    event.evt.gap_evt.params.disconnected.reason = reason;
    __atomic_store_n(&active[conn_id - 1u], 0u, __ATOMIC_RELEASE);
    __atomic_store_n(&mtu_outbound[conn_id - 1u], 0u, __ATOMIC_RELEASE);
    __atomic_store_n(&mtu_inbound[conn_id - 1u], 0u, __ATOMIC_RELEASE);
    __atomic_store_n(&client_read_kind[conn_id - 1u], 0u, __ATOMIC_RELEASE);
    return publish(&event, (uint16_t)sizeof(event));
}

bool r1_cordio_gap_conn_updated(uint8_t conn_id, uint16_t hci_handle,
                               uint16_t interval, uint16_t latency,
                               uint16_t timeout)
{
    if (!valid_link(conn_id, hci_handle)) return false;
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_CONN_PARAM_UPDATE;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = (uint16_t)(conn_id - 1u);
    ble_gap_conn_params_t *params = &event.evt.gap_evt.params.conn_param_update.conn_params;
    params->min_conn_interval = interval;
    params->max_conn_interval = interval;
    params->slave_latency = latency;
    params->conn_sup_timeout = timeout;
    return publish(&event, (uint16_t)sizeof(event));
}

bool r1_cordio_gap_data_length_updated(uint8_t conn_id, uint16_t hci_handle,
                                      uint16_t tx_octets, uint16_t tx_time,
                                      uint16_t rx_octets, uint16_t rx_time)
{
    if (!valid_link(conn_id, hci_handle)) return false;
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_DATA_LENGTH_UPDATE;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = (uint16_t)(conn_id - 1u);
    ble_gap_data_length_params_t *params =
        &event.evt.gap_evt.params.data_length_update.effective_params;
    params->max_tx_octets = tx_octets;
    params->max_tx_time_us = tx_time;
    params->max_rx_octets = rx_octets;
    params->max_rx_time_us = rx_time;
    return publish(&event, (uint16_t)sizeof(event));
}

bool r1_cordio_gap_phy_updated(uint8_t conn_id, uint16_t hci_handle,
                              uint8_t status, uint8_t tx_phy,
                              uint8_t rx_phy)
{
    if (!valid_link(conn_id, hci_handle)) return false;
    if (tx_phy > 3u || rx_phy > 3u) return false;
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_PHY_UPDATE;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = (uint16_t)(conn_id - 1u);
    ble_gap_evt_phy_update_t *update = &event.evt.gap_evt.params.phy_update;
    update->status = status;
    update->tx_phy = tx_phy == 3u ? BLE_GAP_PHY_CODED : tx_phy;
    update->rx_phy = rx_phy == 3u ? BLE_GAP_PHY_CODED : rx_phy;
    return publish(&event, (uint16_t)sizeof(event));
}

bool r1_cordio_event_adv_terminated(uint8_t reason,
                                    const ble_gap_adv_data_t *data)
{
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_ADV_SET_TERMINATED;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = BLE_CONN_HANDLE_INVALID;
    event.evt.gap_evt.params.adv_set_terminated.reason = reason;
    event.evt.gap_evt.params.adv_set_terminated.adv_handle = 0u;
    if (data != 0) event.evt.gap_evt.params.adv_set_terminated.adv_data = *data;
    return publish(&event, (uint16_t)sizeof(event));
}

uint32_t sd_ble_evt_get(uint8_t *destination, uint16_t *length)
{
    if (length == 0 || ((uintptr_t)length & 1u) != 0u ||
        (destination != 0 && ((uintptr_t)destination & (BLE_EVT_PTR_ALIGNMENT - 1u)) != 0u)) {
        return NRF_ERROR_INVALID_ADDR;
    }
    taskENTER_CRITICAL();
    uint8_t read = __atomic_load_n(&tail, __ATOMIC_RELAXED);
    uint8_t write = __atomic_load_n(&head, __ATOMIC_ACQUIRE);
    if (read == write) {
        taskEXIT_CRITICAL();
        return NRF_ERROR_NOT_FOUND;
    }
    const r1_event_slot_t *slot = &slots[read % R1_EVENT_SLOTS];
    uint16_t needed = slot->length;
    if (destination == 0) {
        *length = needed;
        taskEXIT_CRITICAL();
        return NRF_SUCCESS;
    }
    if (*length < needed) {
        *length = needed;
        taskEXIT_CRITICAL();
        return NRF_ERROR_DATA_SIZE;
    }
    memcpy(destination, slot->event, needed);
    *length = needed;
    uint8_t *delivered = slot->event;
    __atomic_store_n(&tail, (uint8_t)(read + 1u), __ATOMIC_RELEASE);
    taskEXIT_CRITICAL();
    vPortFree(delivered);
    return NRF_SUCCESS;
}
#endif
