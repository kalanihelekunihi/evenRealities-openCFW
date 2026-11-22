/* Standalone peripheral host for the source DFU bootloader. All persistent
 * state is lower RAM; the only upper-image call is the supplied BLE event
 * publisher, which the bootloader owns while its application is absent. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "ble.h"
#include "ble_hci.h"
#include "nrf.h"
#include "nrf_error.h"
#include "att_api.h"
#include "att_handler.h"
#include "dm_api.h"
#include "dm_handler.h"
#include "hci_api.h"
#include "hci_defs.h"
#include "l2c_api.h"
#include "l2c_handler.h"
#include "sec_api.h"
#include "smp_defs.h"
#include "smp_api.h"
#include "smp_handler.h"
#include "wsf_assert.h"
#include "wsf_os.h"
#include "wsf_timer.h"
#include "cordio_controller_bootstrap.h"
#include "cordio_dfu_flash.h"
#include "cordio_dfu_arena.h"
#include "cordio_dfu_host.h"
#include "r1_adv_bridge.h"
#include "r1_gap_service.h"
#include "r1_gatts_api_bridge.h"
#include "r1_gatts_database_cordio.h"

enum { R1_DFU_ATT_MTU = 247, R1_DFU_RX_ACL_LEN = 251,
       R1_DFU_STOP_TICKS = 16384 };
extern bool r1_cordio_dfu_cfg_ready(void);
_Static_assert(sizeof(ble_evt_t) <= BLE_EVT_LEN_MAX(R1_DFU_ATT_MTU),
               "DFU events must fit the bootloader's BLE event queue");
_Static_assert(offsetof(ble_evt_t, evt.gatts_evt.params.write.data) + 2u <=
               sizeof(ble_evt_t), "CCC write event must fit its stack record");
static attCfg_t dfu_att_cfg;
static r1_cordio_dfu_publish_t event_publish;
static uint16_t hci_connection;
static uint8_t connection_active;
static uint8_t mtu_reply_pending;
static uint8_t initialized;
static uint8_t reset_ready;
static uint8_t pair_pending;
static uint8_t ltk_pending;
/* Authorized writes may carry the full ATT payload. Keep their Nordic
 * event record off the callback stack; the boot queue copies before return. */
static uint32_t write_event_words[(BLE_EVT_LEN_MAX(R1_DFU_ATT_MTU) + 3u) / 4u];

static void publish_or_assert(const ble_evt_t *event)
{
    if (event_publish == 0 ||
        !event_publish(event, event->header.evt_len))
        WsfAssert(__FILE__, (uint16_t)__LINE__);
}

static uint16_t hci_handle_from_nordic(uint16_t nordic_handle)
{
    return nordic_handle == 0u && connection_active != 0u ?
        hci_connection : BLE_CONN_HANDLE_INVALID;
}

static uint8_t dfu_conn_id(uint16_t nordic_handle)
{
    return nordic_handle == 0u && connection_active != 0u ? 1u : 0u;
}

static bool dfu_tx_event(uint8_t conn_id, uint16_t handle,
                         bool indication, bool service_changed)
{
    if (conn_id != 1u || connection_active == 0u || event_publish == 0)
        return false;
    ble_evt_t event = {0};
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gatts_evt.conn_handle = 0u;
    if (indication) {
        event.header.evt_id = service_changed ? BLE_GATTS_EVT_SC_CONFIRM :
                                                BLE_GATTS_EVT_HVC;
        event.evt.gatts_evt.params.hvc.handle = handle;
    } else {
        event.header.evt_id = BLE_GATTS_EVT_HVN_TX_COMPLETE;
        event.evt.gatts_evt.params.hvn_tx_complete.count = 1u;
    }
    return event_publish(&event, sizeof(event));
}

static bool advertising_terminated(uint8_t reason,
                                    const ble_gap_adv_data_t *data)
{
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GAP_EVT_ADV_SET_TERMINATED;
    event.header.evt_len = (uint16_t)sizeof(event);
    event.evt.gap_evt.conn_handle = BLE_CONN_HANDLE_INVALID;
    event.evt.gap_evt.params.adv_set_terminated.reason = reason;
    event.evt.gap_evt.params.adv_set_terminated.adv_handle = 0u;
    if (data != 0)
        event.evt.gap_evt.params.adv_set_terminated.adv_data = *data;
    return event_publish != 0 && event_publish(&event, sizeof(event));
}

static bool ccc_changed(uint8_t conn_id, uint16_t handle, uint16_t value)
{
    if (conn_id != 1u || connection_active == 0u) return false;
    ble_evt_t event = {0};
    event.header.evt_id = BLE_GATTS_EVT_WRITE;
    event.header.evt_len = (uint16_t)(offsetof(ble_evt_t,
        evt.gatts_evt.params.write.data) + 2u);
    event.evt.gatts_evt.conn_handle = 0u;
    ble_gatts_evt_write_t *write = &event.evt.gatts_evt.params.write;
    write->handle = handle;
    write->uuid.type = BLE_UUID_TYPE_BLE;
    write->uuid.uuid = BLE_UUID_DESCRIPTOR_CLIENT_CHAR_CONFIG;
    write->op = BLE_GATTS_OP_WRITE_REQ;
    write->len = 2u;
    write->data[0] = (uint8_t)value;
    write->data[1] = (uint8_t)(value >> 8);
    return event_publish != 0 && event_publish(&event, event.header.evt_len);
}

static bool dfu_write_event(uint8_t conn_id, uint16_t handle,
                            uint8_t uuid_type, uint16_t uuid,
                            uint8_t opcode, const uint8_t *data,
                            uint16_t length, bool authorize)
{
    if (conn_id != 1u || connection_active == 0u ||
        (length != 0u && data == 0) ||
        (opcode != 0x12u && opcode != 0x52u) ||
        (authorize && opcode != 0x12u)) return false;
    ble_evt_t *event = (ble_evt_t *)write_event_words;
    memset(event, 0, sizeof(write_event_words));
    event->evt.gatts_evt.conn_handle = 0u;
    ble_gatts_evt_write_t *write;
    uint16_t header_bytes;
    if (authorize) {
        event->header.evt_id = BLE_GATTS_EVT_RW_AUTHORIZE_REQUEST;
        event->evt.gatts_evt.params.authorize_request.type =
            BLE_GATTS_AUTHORIZE_TYPE_WRITE;
        write = &event->evt.gatts_evt.params.authorize_request.request.write;
        header_bytes = (uint16_t)offsetof(ble_evt_t,
            evt.gatts_evt.params.authorize_request.request.write.data);
        write->auth_required = 1u;
    } else {
        event->header.evt_id = BLE_GATTS_EVT_WRITE;
        write = &event->evt.gatts_evt.params.write;
        header_bytes = (uint16_t)offsetof(ble_evt_t,
            evt.gatts_evt.params.write.data);
    }
    if ((uint32_t)header_bytes + length > BLE_EVT_LEN_MAX(R1_DFU_ATT_MTU))
        return false;
    write->handle = handle;
    write->uuid.type = uuid_type;
    write->uuid.uuid = uuid;
    write->op = opcode == 0x12u ? BLE_GATTS_OP_WRITE_REQ :
                                  BLE_GATTS_OP_WRITE_CMD;
    write->len = length;
    if (length != 0u) memcpy(write->data, data, length);
    event->header.evt_len = (uint16_t)(header_bytes + length);
    return event_publish != 0 && event_publish(event, event->header.evt_len);
}

static void reset_callback(dmEvt_t *event)
{
    if (event->hdr.event == DM_RESET_CMPL_IND && event->hdr.status == 0u)
        reset_ready = 1u;
    else if (event->hdr.event == DM_ADV_START_IND) {
        r1_cordio_adv_started(event->hdr.status);
        if (event->hdr.status != 0u)
            WsfAssert(__FILE__, (uint16_t)__LINE__);
    } else if (event->hdr.event == DM_ADV_STOP_IND) {
        r1_cordio_adv_stopped(event->hdr.status);
        if (event->hdr.status != 0u)
            WsfAssert(__FILE__, (uint16_t)__LINE__);
    } else if (event->hdr.event == DM_SEC_PAIR_IND &&
               event->hdr.param == 1u && connection_active != 0u) {
        pair_pending = 1u;
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_SEC_PARAMS_REQUEST;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        ble_gap_sec_params_t *params =
            &out.evt.gap_evt.params.sec_params_request.peer_params;
        params->bond = (event->pairInd.auth & DM_AUTH_BOND_FLAG) != 0u;
        params->mitm = (event->pairInd.auth & DM_AUTH_MITM_FLAG) != 0u;
        params->lesc = (event->pairInd.auth & DM_AUTH_SC_FLAG) != 0u;
        params->keypress = (event->pairInd.auth & DM_AUTH_KP_FLAG) != 0u;
        params->oob = event->pairInd.oob != 0u;
        params->io_caps = BLE_GAP_IO_CAPS_NONE;
        params->min_key_size = 7u;
        params->max_key_size = 16u;
        publish_or_assert(&out);
    } else if (event->hdr.event == DM_SEC_LTK_REQ_IND &&
               event->hdr.param == 1u && connection_active != 0u) {
        ltk_pending = 1u;
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_SEC_INFO_REQUEST;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        ble_gap_evt_sec_info_request_t *request =
            &out.evt.gap_evt.params.sec_info_request;
        request->master_id.ediv = event->ltkReqInd.encDiversifier;
        memcpy(request->master_id.rand, event->ltkReqInd.randNum,
               sizeof(request->master_id.rand));
        request->enc_info = 1u;
        publish_or_assert(&out);
    }
}

static void connection_callback(dmEvt_t *event)
{
    if (event->hdr.event == DM_CONN_OPEN_IND &&
        event->connOpen.status == 0u) {
        if (event->hdr.param != 1u || connection_active != 0u)
        {
            WsfAssert(__FILE__, (uint16_t)__LINE__);
            return;
        }
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_CONNECTED;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        ble_gap_evt_connected_t *connected = &out.evt.gap_evt.params.connected;
        connected->role = BLE_GAP_ROLE_PERIPH;
        connected->peer_addr.addr_type = event->connOpen.addrType == 0u ?
            BLE_GAP_ADDR_TYPE_PUBLIC : BLE_GAP_ADDR_TYPE_RANDOM_STATIC;
        memcpy(connected->peer_addr.addr, event->connOpen.peerAddr, 6u);
        connected->conn_params.min_conn_interval = event->connOpen.connInterval;
        connected->conn_params.max_conn_interval = event->connOpen.connInterval;
        connected->conn_params.slave_latency = event->connOpen.connLatency;
        connected->conn_params.conn_sup_timeout = event->connOpen.supTimeout;
        r1_cordio_adv_connected(connected);
        r1_cordio_ccc_freeze();
        r1_cordio_ccc_new_connection(1u);
        AttsCccInitTable(1u, 0);
        hci_connection = event->connOpen.handle;
        connection_active = 1u;
        mtu_reply_pending = 0u;
        pair_pending = 0u;
        ltk_pending = 0u;
        publish_or_assert(&out);
    } else if (event->hdr.event == DM_CONN_CLOSE_IND &&
               event->connClose.status == 0u) {
        if (event->hdr.param != 1u || connection_active == 0u ||
            event->connClose.handle != hci_connection)
        {
            WsfAssert(__FILE__, (uint16_t)__LINE__);
            return;
        }
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_DISCONNECTED;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        out.evt.gap_evt.params.disconnected.reason = event->connClose.reason;
        connection_active = 0u;
        mtu_reply_pending = 0u;
        pair_pending = 0u;
        ltk_pending = 0u;
        AttsCccClearTable(1u);
        r1_cordio_gatts_clear_pending(1u);
        r1_cordio_gatts_tx_clear(1u);
        publish_or_assert(&out);
    } else if (event->hdr.event == DM_CONN_CLOSE_IND &&
               event->connClose.status == HCI_ERR_ADV_TIMEOUT) {
        r1_cordio_adv_stopped(0u);
    } else if (event->hdr.event == DM_CONN_UPDATE_IND &&
               event->connUpdate.status == 0u && connection_active != 0u) {
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_CONN_PARAM_UPDATE;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        ble_gap_conn_params_t *params =
            &out.evt.gap_evt.params.conn_param_update.conn_params;
        params->min_conn_interval = event->connUpdate.connInterval;
        params->max_conn_interval = event->connUpdate.connInterval;
        params->slave_latency = event->connUpdate.connLatency;
        params->conn_sup_timeout = event->connUpdate.supTimeout;
        publish_or_assert(&out);
    } else if (event->hdr.event == DM_CONN_DATA_LEN_CHANGE_IND &&
               connection_active != 0u) {
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_DATA_LENGTH_UPDATE;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        ble_gap_data_length_params_t *params =
            &out.evt.gap_evt.params.data_length_update.effective_params;
        params->max_tx_octets = event->dataLenChange.maxTxOctets;
        params->max_tx_time_us = event->dataLenChange.maxTxTime;
        params->max_rx_octets = event->dataLenChange.maxRxOctets;
        params->max_rx_time_us = event->dataLenChange.maxRxTime;
        publish_or_assert(&out);
    } else if (event->hdr.event == DM_PHY_UPDATE_IND &&
               connection_active != 0u) {
        ble_evt_t out = {0};
        out.header.evt_id = BLE_GAP_EVT_PHY_UPDATE;
        out.header.evt_len = (uint16_t)sizeof(out);
        out.evt.gap_evt.conn_handle = 0u;
        out.evt.gap_evt.params.phy_update.status = event->phyUpdate.status;
        out.evt.gap_evt.params.phy_update.tx_phy = event->phyUpdate.txPhy;
        out.evt.gap_evt.params.phy_update.rx_phy = event->phyUpdate.rxPhy;
        publish_or_assert(&out);
    }
}

static void att_callback(attEvt_t *event)
{
    if (event->hdr.event == ATTS_HANDLE_VALUE_CNF) {
        if (!r1_cordio_gatts_tx_complete(event->hdr.param,
                                         event->handle, event->hdr.status))
            WsfAssert(__FILE__, (uint16_t)__LINE__);
        return;
    }
    if (event->hdr.event != ATT_MTU_UPDATE_IND ||
        event->hdr.param != 1u || connection_active == 0u) return;
    ble_evt_t out = {0};
    out.header.evt_id = BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST;
    out.header.evt_len = (uint16_t)sizeof(out);
    out.evt.gatts_evt.conn_handle = 0u;
    out.evt.gatts_evt.params.exchange_mtu_request.client_rx_mtu = event->mtu;
    mtu_reply_pending = 1u;
    publish_or_assert(&out);
}

static bool wait_for_adv_stop(void)
{
    uint32_t start = NRF_RTC1->COUNTER;
    for (uint32_t remaining = 1000000u; remaining != 0u; --remaining) {
        WsfTimerSleepUpdate();
        wsfOsDispatcher();
        r1_cordio_dfu_flash_service();
        if (r1_cordio_adv_is_idle()) return true;
        if (((NRF_RTC1->COUNTER - start) & 0x00ffffffu) >=
            R1_DFU_STOP_TICKS) break;
    }
    return false;
}

bool r1_cordio_dfu_host_idle(void)
{
    return connection_active == 0u && r1_cordio_adv_is_idle();
}

bool r1_cordio_dfu_host_start(r1_cordio_dfu_publish_t publish)
{
    if (publish == 0 || initialized != 0u) return false;
    event_publish = publish;
    SecInit();
    SecAesInit();
    SecCmacInit();
    SecEccInit();
    HciSetMaxRxAclLen(R1_DFU_RX_ACL_LEN);
    dfu_att_cfg = *pAttCfg;
    dfu_att_cfg.mtu = R1_DFU_ATT_MTU;
    pAttCfg = &dfu_att_cfg;
    DmDevVsInit(0);
    DmAdvInit();
    DmConnInit();
    DmConnSlaveInit();
    DmPhyInit();
    DmSecInit();
    DmHandlerInit(WsfOsSetNextHandler(DmHandler));
    L2cSlaveHandlerInit(WsfOsSetNextHandler(L2cSlaveHandler));
    L2cInit();
    L2cSlaveInit();
    AttHandlerInit(WsfOsSetNextHandler(AttHandler));
    AttsInit();
    r1_cordio_gatts_database_bind(r1_cordio_dfu_arena_alloc,
                                   r1_cordio_dfu_arena_free,
                                   dfu_write_event);
    r1_cordio_adv_set_hooks(advertising_terminated, hci_handle_from_nordic);
    r1_cordio_adv_set_stop_wait(wait_for_adv_stop);
    r1_cordio_gap_service_set_ccc_sink(ccc_changed);
    r1_cordio_gap_service_init();
    AttsIndInit();
    AttcInit();
    AttRegister(att_callback);
    SmpHandlerInit(WsfOsSetNextHandler(SmpHandler));
    SmprInit();
    SmprScInit();
    DmRegister(reset_callback);
    DmConnRegister(DM_CLIENT_ID_APP, connection_callback);
    initialized = 1u;
    DmDevReset();
    return true;
}

bool r1_cordio_dfu_host_ready(void)
{
    return initialized != 0u && reset_ready != 0u;
}

uint32_t r1_cordio_dfu_ble_enable(r1_cordio_dfu_publish_t publish,
                                  void *arena, uint32_t arena_bytes,
                                  uint32_t (*uuid_encode)(const ble_uuid_t *,
                                                           uint8_t *, uint8_t *))
{
    if (!r1_cordio_dfu_cfg_ready()) return NRF_ERROR_INVALID_STATE;
    if (uuid_encode == 0) return NRF_ERROR_INVALID_ADDR;
    if (!r1_cordio_dfu_arena_init(arena, arena_bytes))
        return NRF_ERROR_NO_MEM;
    r1_cordio_gatts_api_bind(dfu_conn_id, uuid_encode, dfu_tx_event);
    if (!r1_cordio_controller_bootstrap()) return NRF_ERROR_NO_MEM;
    r1_cordio_dfu_flash_register();
    if (!r1_cordio_dfu_host_start(publish)) return NRF_ERROR_INVALID_STATE;
    for (uint32_t remaining = 10000u; remaining != 0u; --remaining) {
        WsfTimerSleepUpdate();
        wsfOsDispatcher();
        r1_cordio_dfu_flash_service();
        if (r1_cordio_dfu_host_ready()) return NRF_SUCCESS;
    }
    return NRF_ERROR_TIMEOUT;
}

void r1_cordio_dfu_host_request_shutdown(void)
{
    if (initialized == 0u) return;
    reset_ready = 0u;
    DmDevReset();
}

uint32_t r1_cordio_dfu_gatts_value_get(uint16_t conn_handle,
                                       uint16_t handle, ble_gatts_value_t *value)
{
    if (value == 0 || ((uintptr_t)value & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    /* Nordic's unbonded DFU handler passes the Service Changed UUID while
     * requesting its CCC value. The source database assigns that CCC handle
     * 11; translate this one SDK call before doing a handle-based lookup. */
    if (handle == BLE_UUID_GATT_CHARACTERISTIC_SERVICE_CHANGED)
        handle = 11u;
    uint8_t conn_id = 0u;
    if (r1_cordio_atts_is_ccc(handle)) {
        conn_id = dfu_conn_id(conn_handle);
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

uint32_t r1_cordio_dfu_sec_params_reply(
    uint16_t conn_handle, uint8_t status,
    const ble_gap_sec_params_t *parameters,
    const ble_gap_sec_keyset_t *keys)
{
    if (dfu_conn_id(conn_handle) == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (pair_pending == 0u) return NRF_ERROR_INVALID_STATE;
    if (status != BLE_GAP_SEC_STATUS_PAIRING_NOT_SUPP ||
        parameters != 0 || keys != 0)
        return NRF_ERROR_NOT_SUPPORTED;
    pair_pending = 0u;
    DmSecCancelReq(1u, (uint8_t)(status - 0x80u));
    return NRF_SUCCESS;
}

uint32_t r1_cordio_dfu_sec_info_reply(
    uint16_t conn_handle, const ble_gap_enc_info_t *enc_info,
    const ble_gap_irk_t *id_info, const ble_gap_sign_info_t *sign_info)
{
    if (dfu_conn_id(conn_handle) == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (ltk_pending == 0u) return NRF_ERROR_INVALID_STATE;
    if (enc_info != 0 || id_info != 0 || sign_info != 0)
        return NRF_ERROR_NOT_SUPPORTED;
    ltk_pending = 0u;
    DmSecLtkRsp(1u, false, DM_SEC_LEVEL_NONE, 0);
    return NRF_SUCCESS;
}

uint32_t r1_cordio_dfu_gap_disconnect(uint16_t conn_handle, uint8_t reason)
{
    if (conn_handle != 0u || connection_active == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (reason != BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION &&
        reason != BLE_HCI_CONN_INTERVAL_UNACCEPTABLE)
        return NRF_ERROR_INVALID_PARAM;
    DmConnClose(DM_CLIENT_ID_APP, 1u, reason);
    uint32_t start = NRF_RTC1->COUNTER;
    for (uint32_t remaining = 1000000u; remaining != 0u; --remaining) {
        WsfTimerSleepUpdate();
        wsfOsDispatcher();
        r1_cordio_dfu_flash_service();
        if (connection_active == 0u) return NRF_SUCCESS;
        if (((NRF_RTC1->COUNTER - start) & 0x00ffffffu) >=
            R1_DFU_STOP_TICKS) break;
    }
    return NRF_ERROR_TIMEOUT;
}

uint32_t r1_cordio_dfu_gap_conn_param_update(
    uint16_t conn_handle, const ble_gap_conn_params_t *parameters)
{
    if (conn_handle != 0u || connection_active == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    ble_gap_conn_params_t preferred;
    if (parameters == 0) {
        r1_cordio_gap_ppcp_get((uint8_t *)&preferred);
        parameters = &preferred;
    }
    if (((uintptr_t)parameters & 1u) != 0u) return NRF_ERROR_INVALID_ADDR;
    const ble_gap_conn_params_t *p = parameters;
    if (p->min_conn_interval < 6u || p->max_conn_interval > 3200u ||
        p->min_conn_interval > p->max_conn_interval ||
        p->slave_latency > 499u || p->conn_sup_timeout < 10u ||
        p->conn_sup_timeout > 3200u ||
        (uint32_t)p->conn_sup_timeout * 8u <=
        (uint32_t)(p->slave_latency + 1u) * p->max_conn_interval * 2u)
        return NRF_ERROR_INVALID_PARAM;
    hciConnSpec_t spec = {0};
    spec.connIntervalMin = p->min_conn_interval;
    spec.connIntervalMax = p->max_conn_interval;
    spec.connLatency = p->slave_latency;
    spec.supTimeout = p->conn_sup_timeout;
    DmConnUpdate(1u, &spec);
    return NRF_SUCCESS;
}

uint32_t r1_cordio_dfu_gap_data_length_update(
    uint16_t conn_handle, const ble_gap_data_length_params_t *parameters,
    ble_gap_data_length_limitation_t *limitation)
{
    if (conn_handle != 0u || connection_active == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (limitation != 0 && ((uintptr_t)limitation & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if (limitation != 0)
        memset(limitation, 0, sizeof(ble_gap_data_length_limitation_t));
    uint16_t tx_octets = 251u;
    uint16_t tx_time = 2120u;
    if (parameters != 0) {
        if (((uintptr_t)parameters & 1u) != 0u)
            return NRF_ERROR_INVALID_ADDR;
        const ble_gap_data_length_params_t *p = parameters;
        if (p->max_tx_octets != BLE_GAP_DATA_LENGTH_AUTO)
            tx_octets = p->max_tx_octets;
        if (p->max_tx_time_us != BLE_GAP_DATA_LENGTH_AUTO)
            tx_time = p->max_tx_time_us;
        if (tx_octets < 27u || tx_time < 328u ||
            (p->max_rx_octets != 0u && p->max_rx_octets < 27u) ||
            (p->max_rx_time_us != 0u && p->max_rx_time_us < 328u))
            return NRF_ERROR_INVALID_PARAM;
        if (tx_octets > 251u || p->max_rx_octets > 251u ||
            tx_time > 2120u || p->max_rx_time_us > 2120u) {
            if (limitation != 0) {
                if (tx_octets > 251u)
                    limitation->tx_payload_limited_octets = tx_octets - 251u;
                if (p->max_rx_octets > 251u)
                    limitation->rx_payload_limited_octets =
                        p->max_rx_octets - 251u;
                if (tx_time > 2120u || p->max_rx_time_us > 2120u)
                    limitation->tx_rx_time_limited_us =
                        (tx_time > p->max_rx_time_us ?
                         tx_time : p->max_rx_time_us) - 2120u;
            }
            return NRF_ERROR_NOT_SUPPORTED;
        }
    }
    DmConnSetDataLen(1u, tx_octets, tx_time);
    return NRF_SUCCESS;
}

uint32_t r1_cordio_dfu_gap_phy_update(uint16_t conn_handle,
                                      const ble_gap_phys_t *phys)
{
    if (conn_handle != 0u || connection_active == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (phys == 0) return NRF_ERROR_INVALID_ADDR;
    if (((uintptr_t)phys & 1u) != 0u) return NRF_ERROR_INVALID_ADDR;
    const ble_gap_phys_t *p = phys;
    if ((p->tx_phys & (uint8_t)~BLE_GAP_PHYS_SUPPORTED) != 0u ||
        (p->rx_phys & (uint8_t)~BLE_GAP_PHYS_SUPPORTED) != 0u)
        return NRF_ERROR_INVALID_PARAM;
    uint8_t all = 0u;
    if (p->tx_phys == BLE_GAP_PHY_AUTO) all |= 1u;
    if (p->rx_phys == BLE_GAP_PHY_AUTO) all |= 2u;
    DmSetPhy(1u, all, p->tx_phys, p->rx_phys, 0u);
    return NRF_SUCCESS;
}

uint32_t r1_cordio_dfu_gatts_exchange_mtu_reply(uint16_t conn_handle,
                                                 uint16_t server_rx_mtu)
{
    if (conn_handle != 0u || connection_active == 0u)
        return BLE_ERROR_INVALID_CONN_HANDLE;
    if (server_rx_mtu < BLE_GATT_ATT_MTU_DEFAULT || server_rx_mtu > 247u)
        return NRF_ERROR_INVALID_PARAM;
    if (server_rx_mtu != 247u) return NRF_ERROR_NOT_SUPPORTED;
    if (mtu_reply_pending == 0u) return NRF_ERROR_INVALID_STATE;
    /* Cordio already transmitted its ATT MTU response before the callback. */
    mtu_reply_pending = 0u;
    return NRF_SUCCESS;
}
#endif
