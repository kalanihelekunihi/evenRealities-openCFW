/* One legacy advertising set for the R1 source-built Cordio candidate. */
#if defined(R1_CORDIO_RTC0)
#include <string.h>

#include "ble.h"
#include "nrf_error.h"
#include "dm_api.h"
#include "hci_defs.h"
#include "ll_api.h"
#include "wsf_os.h"
#include "wsf_assert.h"
#include "cordio_ble_event_bridge.h"
#include "r1_factory_ble_address.h"
#include "r1_adv_bridge.h"

enum { R1_ADV_HANDLE = 0, R1_ADV_UNCONFIGURED = 0,
       R1_ADV_IDLE = 1, R1_ADV_RUNNING = 2, R1_ADV_STOPPING = 3 };

static ble_gap_adv_data_t adv_buffers;
static ble_gap_adv_params_t adv_params;
static uint8_t adv_state;
static uint8_t empty_data;
static bool (*terminated_sink)(uint8_t, const ble_gap_adv_data_t *);
static uint16_t (*hci_handle_lookup)(uint16_t);
static bool (*stop_wait)(void);

void r1_cordio_adv_set_stop_wait(bool (*wait_for_stop)(void))
{
    stop_wait = wait_for_stop;
}

bool r1_cordio_adv_is_idle(void)
{
    uint8_t state = __atomic_load_n(&adv_state, __ATOMIC_ACQUIRE);
    return state == R1_ADV_IDLE || state == R1_ADV_UNCONFIGURED;
}

void r1_cordio_adv_set_hooks(
    bool (*terminated)(uint8_t reason, const ble_gap_adv_data_t *data),
    uint16_t (*hci_handle)(uint16_t nordic_handle))
{
    terminated_sink = terminated;
    hci_handle_lookup = hci_handle;
}

void r1_cordio_dm_adv_config(uint8_t type, uint8_t peer_type,
                             const uint8_t peer_addr[6], uint16_t interval,
                             uint8_t channels, const uint8_t *adv_data,
                             uint8_t adv_length, const uint8_t *scan_data,
                             uint8_t scan_length)
{
    uint8_t own_addr[6];
    r1_factory_ble_address_load(own_addr);
    DmAdvSetAddrType(DM_ADDR_RANDOM);
    DmAdvSetRandAddr(0u, own_addr);
    DmAdvSetInterval(0u, interval, interval);
    DmAdvSetChannelMap(0u, channels);
    DmAdvConfig(0u, type, peer_type, (uint8_t *)peer_addr);
    DmAdvSetData(0u, HCI_ADV_DATA_OP_COMP_FRAG, DM_DATA_LOC_ADV,
                 adv_length, adv_length != 0u ? (uint8_t *)adv_data : &empty_data);
    DmAdvSetData(0u, HCI_ADV_DATA_OP_COMP_FRAG, DM_DATA_LOC_SCAN,
                 scan_length, scan_length != 0u ? (uint8_t *)scan_data : &empty_data);
}

void r1_cordio_dm_adv_start(uint16_t duration_ms)
{
    uint8_t handle = 0u;
    uint8_t max_events = 0u;
    DmAdvStart(1u, &handle, &duration_ms, &max_events);
}

void r1_cordio_dm_adv_stop(void)
{
    uint8_t handle = 0u;
    DmAdvStop(1u, &handle);
}

void r1_cordio_ll_set_adv_tx_power(int8_t power)
{
    WsfTaskLock();
    LlSetAdvTxPower(power);
    WsfTaskUnlock();
}

uint8_t r1_cordio_ll_set_conn_tx_power(uint16_t hci_handle, int8_t power)
{
    return LlSetAllPhyTxPowerLevel(hci_handle, power);
}

static bool data_valid(const ble_data_t *data)
{
    return data->len <= BLE_GAP_ADV_SET_DATA_SIZE_MAX &&
           (data->len == 0u || data->p_data != 0);
}

static uint8_t cordio_type(uint8_t nordic_type)
{
    switch (nordic_type) {
    case BLE_GAP_ADV_TYPE_CONNECTABLE_SCANNABLE_UNDIRECTED: return 0u;
    case BLE_GAP_ADV_TYPE_CONNECTABLE_NONSCANNABLE_DIRECTED_HIGH_DUTY_CYCLE: return 1u;
    case BLE_GAP_ADV_TYPE_CONNECTABLE_NONSCANNABLE_DIRECTED: return 4u;
    case BLE_GAP_ADV_TYPE_NONCONNECTABLE_SCANNABLE_UNDIRECTED: return 2u;
    case BLE_GAP_ADV_TYPE_NONCONNECTABLE_NONSCANNABLE_UNDIRECTED: return 3u;
    default: return UINT8_MAX;
    }
}

uint32_t sd_ble_gap_adv_set_configure(uint8_t *handle,
                                      ble_gap_adv_data_t const *data,
                                      ble_gap_adv_params_t const *params)
{
    if (handle == 0) return NRF_ERROR_INVALID_ADDR;
    if (*handle != BLE_GAP_ADV_SET_HANDLE_NOT_SET && *handle != R1_ADV_HANDLE)
        return BLE_ERROR_INVALID_ADV_HANDLE;
    uint8_t state = __atomic_load_n(&adv_state, __ATOMIC_ACQUIRE);
    if (*handle == BLE_GAP_ADV_SET_HANDLE_NOT_SET &&
        state != R1_ADV_UNCONFIGURED) return NRF_ERROR_NO_MEM;
    if (*handle == R1_ADV_HANDLE && state == R1_ADV_UNCONFIGURED)
        return BLE_ERROR_INVALID_ADV_HANDLE;
    if (state == R1_ADV_RUNNING || state == R1_ADV_STOPPING)
        return NRF_ERROR_INVALID_STATE;
    if (params == 0 && state == R1_ADV_UNCONFIGURED)
        return NRF_ERROR_INVALID_PARAM;
    if (params != 0 && ((uintptr_t)params & 3u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if (data != 0 && ((uintptr_t)data & 3u) != 0u)
        return NRF_ERROR_INVALID_ADDR;

    ble_gap_adv_params_t next = params != 0 ? *params : adv_params;
    uint8_t type = cordio_type(next.properties.type);
    if (type == UINT8_MAX) return NRF_ERROR_NOT_SUPPORTED;
    if (next.filter_policy != BLE_GAP_ADV_FP_ANY || next.max_adv_evts != 0u ||
        (next.primary_phy != BLE_GAP_PHY_AUTO &&
         next.primary_phy != BLE_GAP_PHY_1MBPS) ||
        next.scan_req_notification != 0u || next.duration > 6553u ||
        next.interval > UINT16_MAX) return NRF_ERROR_NOT_SUPPORTED;
    if (next.properties.type != BLE_GAP_ADV_TYPE_CONNECTABLE_NONSCANNABLE_DIRECTED_HIGH_DUTY_CYCLE &&
        (next.interval < 32u || next.interval > 16384u))
        return NRF_ERROR_INVALID_PARAM;
    if (type == 1u || type == 4u) {
        if (next.p_peer_addr == 0) return NRF_ERROR_INVALID_ADDR;
        if (next.p_peer_addr->addr_type != BLE_GAP_ADDR_TYPE_PUBLIC &&
            next.p_peer_addr->addr_type != BLE_GAP_ADDR_TYPE_RANDOM_STATIC)
            return BLE_ERROR_GAP_INVALID_BLE_ADDR;
    } else if (next.p_peer_addr != 0) {
        return NRF_ERROR_INVALID_PARAM;
    }
    /* Only the three primary advertising channels can be masked here. */
    if (next.channel_mask[0] != 0u || next.channel_mask[1] != 0u ||
        next.channel_mask[2] != 0u || next.channel_mask[3] != 0u ||
        (next.channel_mask[4] & 0x1fu) != 0u)
        return NRF_ERROR_NOT_SUPPORTED;
    uint8_t channels = (uint8_t)((~next.channel_mask[4] >> 5) & 7u);
    if (channels == 0u) return NRF_ERROR_INVALID_PARAM;

    ble_gap_adv_data_t next_data = {0};
    if (data != 0) next_data = *data;
    if (!data_valid(&next_data.adv_data) || !data_valid(&next_data.scan_rsp_data))
        return NRF_ERROR_INVALID_LENGTH;
    if ((type == 1u || type == 4u) &&
        (next_data.adv_data.len != 0u || next_data.scan_rsp_data.len != 0u))
        return NRF_ERROR_INVALID_PARAM;
    if (type == 3u && next_data.scan_rsp_data.len != 0u)
        return NRF_ERROR_INVALID_PARAM;

    uint8_t peer[6] = {0};
    uint8_t peer_type = 0u;
    if (next.p_peer_addr != 0) {
        memcpy(peer, next.p_peer_addr->addr, sizeof(peer));
        peer_type = next.p_peer_addr->addr_type == BLE_GAP_ADDR_TYPE_PUBLIC ? 0u : 1u;
    }
    r1_cordio_dm_adv_config(type, peer_type, peer, (uint16_t)next.interval,
                            channels, next_data.adv_data.p_data,
                            (uint8_t)next_data.adv_data.len,
                            next_data.scan_rsp_data.p_data,
                            (uint8_t)next_data.scan_rsp_data.len);
    adv_params = next;
    adv_buffers = next_data;
    *handle = R1_ADV_HANDLE;
    __atomic_store_n(&adv_state, R1_ADV_IDLE, __ATOMIC_RELEASE);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_adv_start(uint8_t handle, uint8_t conn_tag)
{
    if (handle != R1_ADV_HANDLE ||
        __atomic_load_n(&adv_state, __ATOMIC_ACQUIRE) == R1_ADV_UNCONFIGURED)
        return BLE_ERROR_INVALID_ADV_HANDLE;
    if (conn_tag != 1u && conn_tag != BLE_CONN_CFG_TAG_DEFAULT)
        return NRF_ERROR_NOT_FOUND;
    if (__atomic_load_n(&adv_state, __ATOMIC_ACQUIRE) != R1_ADV_IDLE)
        return NRF_ERROR_INVALID_STATE;
    __atomic_store_n(&adv_state, R1_ADV_RUNNING, __ATOMIC_RELEASE);
    r1_cordio_dm_adv_start((uint16_t)(adv_params.duration * 10u));
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_adv_stop(uint8_t handle)
{
    if (handle != R1_ADV_HANDLE ||
        __atomic_load_n(&adv_state, __ATOMIC_ACQUIRE) == R1_ADV_UNCONFIGURED)
        return BLE_ERROR_INVALID_ADV_HANDLE;
    if (__atomic_load_n(&adv_state, __ATOMIC_ACQUIRE) != R1_ADV_RUNNING)
        return NRF_ERROR_INVALID_STATE;
    __atomic_store_n(&adv_state, R1_ADV_STOPPING, __ATOMIC_RELEASE);
    r1_cordio_dm_adv_stop();
    if (stop_wait != 0 && !stop_wait()) return NRF_ERROR_TIMEOUT;
    return NRF_SUCCESS;
}

uint32_t sd_ble_gap_adv_addr_get(uint8_t handle, ble_gap_addr_t *address)
{
    if (handle != R1_ADV_HANDLE ||
        __atomic_load_n(&adv_state, __ATOMIC_ACQUIRE) == R1_ADV_UNCONFIGURED)
        return BLE_ERROR_INVALID_ADV_HANDLE;
    if (address == 0) return NRF_ERROR_INVALID_ADDR;
    return sd_ble_gap_addr_get(address);
}

static bool tx_power_supported(int8_t power)
{
    switch (power) {
    case -40: case -20: case -16: case -12: case -8: case -4:
    case 0: case 2: case 3: case 4: case 5: case 6: case 7: case 8:
        return true;
    default: return false;
    }
}

uint32_t sd_ble_gap_tx_power_set(uint8_t role, uint16_t handle, int8_t power)
{
    if (!tx_power_supported(power)) return NRF_ERROR_INVALID_PARAM;
    if (role == BLE_GAP_TX_POWER_ROLE_ADV) {
        if (handle != R1_ADV_HANDLE ||
            __atomic_load_n(&adv_state, __ATOMIC_ACQUIRE) == R1_ADV_UNCONFIGURED)
            return BLE_ERROR_INVALID_ADV_HANDLE;
        r1_cordio_ll_set_adv_tx_power(power);
        return NRF_SUCCESS;
    }
    if (role == BLE_GAP_TX_POWER_ROLE_CONN) {
        uint16_t hci_handle = hci_handle_lookup == 0 ?
            BLE_CONN_HANDLE_INVALID : hci_handle_lookup(handle);
        if (hci_handle == BLE_CONN_HANDLE_INVALID)
            return BLE_ERROR_INVALID_CONN_HANDLE;
        return r1_cordio_ll_set_conn_tx_power(hci_handle, power) == 0u ?
               NRF_SUCCESS : BLE_ERROR_INVALID_CONN_HANDLE;
    }
    return NRF_ERROR_INVALID_PARAM;
}

void r1_cordio_adv_started(uint8_t status)
{
    if (status != 0u) {
        __atomic_store_n(&adv_state, R1_ADV_IDLE, __ATOMIC_RELEASE);
    }
}

void r1_cordio_adv_stopped(uint8_t status)
{
    if (status != 0u) return;
    uint8_t previous = __atomic_exchange_n(&adv_state, R1_ADV_IDLE, __ATOMIC_ACQ_REL);
    if (previous == R1_ADV_RUNNING &&
        (terminated_sink == 0 || !terminated_sink(
            BLE_GAP_EVT_ADV_SET_TERMINATED_REASON_TIMEOUT, &adv_buffers))) {
        WsfAssert(__FILE__, (uint16_t)__LINE__);
    }
}

void r1_cordio_adv_connected(ble_gap_evt_connected_t *event)
{
    (void)__atomic_exchange_n(&adv_state, R1_ADV_IDLE, __ATOMIC_ACQ_REL);
    event->adv_handle = R1_ADV_HANDLE;
    event->adv_data = adv_buffers;
}
#endif
