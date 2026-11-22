/* Nordic GATTS registration calls backed by the R1 Cordio ATT database. */
#if defined(R1_CORDIO_RTC0)
#include <string.h>
#include "ble.h"
#include "nrf_error.h"
#include "att_api.h"
#include "att_defs.h"
#include "wsf_os.h"
#include "r1_gatts_api_bridge.h"
#include "r1_gap_service.h"
#include "r1_gatts_database_cordio.h"

/* One queued notification and one outstanding indication per link. Cordio's
 * callback reports the attribute handle, but carries no per-PDU token. The
 * one-notification limit keeps completion attribution unambiguous. */
static uint16_t pending_notification[3];
static uint16_t pending_indication[3];
static uint8_t pending_service_changed[3];
static uint8_t (*connection_id)(uint16_t);
static uint32_t (*encode_uuid)(const ble_uuid_t *, uint8_t *, uint8_t *);
static bool (*publish_tx)(uint8_t, uint16_t, bool, bool);

void r1_cordio_gatts_api_bind(
    uint8_t (*conn_id)(uint16_t),
    uint32_t (*uuid_encode)(const ble_uuid_t *, uint8_t *, uint8_t *),
    bool (*tx_event)(uint8_t, uint16_t, bool, bool))
{
    connection_id = conn_id;
    encode_uuid = uuid_encode;
    publish_tx = tx_event;
}

static uint8_t active_connection(uint16_t handle)
{
    return connection_id == 0 ? 0u : connection_id(handle);
}

static uint32_t encode(const ble_uuid_t *uuid, uint8_t *length,
                       uint8_t *bytes)
{
    return encode_uuid == 0 ? NRF_ERROR_INVALID_STATE :
                              encode_uuid(uuid, length, bytes);
}

void r1_cordio_gatts_tx_clear(uint8_t conn_id)
{
    if (conn_id < 1u || conn_id > 3u) return;
    WsfTaskLock();
    pending_notification[conn_id - 1u] = 0u;
    pending_indication[conn_id - 1u] = 0u;
    pending_service_changed[conn_id - 1u] = 0u;
    WsfTaskUnlock();
}

bool r1_cordio_gatts_tx_complete(uint8_t conn_id, uint16_t handle,
                                  uint8_t status)
{
    if (conn_id < 1u || conn_id > 3u) return false;
    uint8_t link = (uint8_t)(conn_id - 1u);
    bool indication = false;
    bool service_changed = false;
    bool found = false;
    WsfTaskLock();
    if (pending_indication[link] == handle) {
        indication = true;
        service_changed = pending_service_changed[link] != 0u;
        pending_indication[link] = 0u;
        pending_service_changed[link] = 0u;
        found = true;
    } else if (pending_notification[link] == handle) {
        pending_notification[link] = 0u;
        found = true;
    }
    WsfTaskUnlock();
    if (!found || status != ATT_SUCCESS) return true;
    return publish_tx != 0 && publish_tx(conn_id, handle, indication,
                                         service_changed);
}

static uint32_t queue_hvx(uint8_t conn_id, uint16_t handle,
                          uint8_t type, const uint8_t *data,
                          uint16_t length, bool service_changed)
{
    uint8_t link = (uint8_t)(conn_id - 1u);
    WsfTaskLock();
    uint16_t *slot = type == BLE_GATT_HVX_INDICATION ?
                     &pending_indication[link] : &pending_notification[link];
    if (*slot != 0u) {
        WsfTaskUnlock();
        return type == BLE_GATT_HVX_INDICATION ? NRF_ERROR_BUSY :
                                                 NRF_ERROR_RESOURCES;
    }
    *slot = handle;
    if (type == BLE_GATT_HVX_INDICATION)
        pending_service_changed[link] = service_changed;
    WsfTaskUnlock();
    if (type == BLE_GATT_HVX_INDICATION)
        AttsHandleValueInd(conn_id, handle, length, (uint8_t *)data);
    else
        AttsHandleValueNtf(conn_id, handle, length, (uint8_t *)data);
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_hvx(uint16_t conn_handle,
                           ble_gatts_hvx_params_t const *params)
{
    uint8_t conn_id = active_connection(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (params == 0 || params->p_len == 0) return NRF_ERROR_INVALID_ADDR;
    if (params->offset != 0u ||
        (params->type != BLE_GATT_HVX_NOTIFICATION &&
         params->type != BLE_GATT_HVX_INDICATION))
        return NRF_ERROR_INVALID_PARAM;
    uint16_t ccc_handle, max_length;
    uint8_t properties;
    if (!r1_cordio_gatts_hvx_details(params->handle, &ccc_handle,
                                      &properties, &max_length))
        return BLE_ERROR_INVALID_ATTR_HANDLE;
    uint8_t needed = params->type == BLE_GATT_HVX_INDICATION ?
                     ATT_PROP_INDICATE : ATT_PROP_NOTIFY;
    if ((properties & needed) == 0u) return BLE_ERROR_GATTS_INVALID_ATTR_TYPE;
    if ((r1_cordio_ccc_enabled(conn_id, ccc_handle) &
         (params->type == BLE_GATT_HVX_INDICATION ?
          ATT_CLIENT_CFG_INDICATE : ATT_CLIENT_CFG_NOTIFY)) == 0u)
        return NRF_ERROR_INVALID_STATE;
    uint16_t requested = *params->p_len;
    if (requested > max_length || requested > 244u ||
        (uint32_t)requested + 3u > AttGetMtu(conn_id))
        return NRF_ERROR_DATA_SIZE;
    uint8_t current[244];
    const uint8_t *send = params->p_data;
    uint16_t length = requested;
    if (send != 0) {
        if (AttsSetAttr(params->handle, requested, (uint8_t *)send) != ATT_SUCCESS)
            return NRF_ERROR_DATA_SIZE;
    } else {
        if (r1_cordio_atts_value_snapshot(conn_id, params->handle, 0u,
                                            current, sizeof(current),
                                            &length) != 0u)
            return NRF_ERROR_INVALID_STATE;
        if (length > requested) length = requested;
        send = current;
    }
    uint32_t result = queue_hvx(conn_id, params->handle, params->type,
                                 send, length, false);
    if (params->p_data != 0) *params->p_len = requested;
    else *params->p_len = 0u;
    return result;
}

uint32_t sd_ble_gatts_service_changed(uint16_t conn_handle,
                                       uint16_t start_handle,
                                       uint16_t end_handle)
{
    uint8_t conn_id = active_connection(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (start_handle == 0u || start_handle > end_handle)
        return NRF_ERROR_INVALID_PARAM;
    if ((r1_cordio_ccc_enabled(conn_id, 11u) &
         ATT_CLIENT_CFG_INDICATE) == 0u) return NRF_ERROR_INVALID_STATE;
    uint8_t value[4] = {(uint8_t)start_handle,
                        (uint8_t)(start_handle >> 8),
                        (uint8_t)end_handle,
                        (uint8_t)(end_handle >> 8)};
    return queue_hvx(conn_id, 10u, BLE_GATT_HVX_INDICATION,
                     value, sizeof(value), true);
}

uint32_t sd_ble_gatts_sys_attr_set(uint16_t conn_handle,
                                   uint8_t const *data, uint16_t length,
                                   uint32_t flags)
{
    uint8_t conn_id = active_connection(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if ((flags & ~3u) != 0u) return NRF_ERROR_INVALID_PARAM;
    if (data == 0 && length != 0u) return NRF_ERROR_INVALID_ADDR;
    if (!r1_cordio_ccc_restore(conn_id, (uint8_t)flags, data, length))
        return NRF_ERROR_INVALID_DATA;
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_sys_attr_get(uint16_t conn_handle,
                                   uint8_t *data, uint16_t *length,
                                   uint32_t flags)
{
    if (conn_handle >= 3u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (length == 0 || ((uintptr_t)length & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if ((flags & ~3u) != 0u) return NRF_ERROR_INVALID_PARAM;
    uint8_t conn_id = active_connection(conn_handle);
    bool recent = conn_id == 0u;
    if (recent) conn_id = (uint8_t)(conn_handle + 1u);
    uint16_t required;
    if (!r1_cordio_ccc_export(conn_id, recent, (uint8_t)flags,
                               0, 0u, &required))
        return recent ? BLE_ERROR_INVALID_CONN_HANDLE : NRF_ERROR_NOT_FOUND;
    uint16_t capacity = *length;
    *length = required;
    if (data == 0) return NRF_SUCCESS;
    if (capacity < required) return NRF_ERROR_DATA_SIZE;
    if (!r1_cordio_ccc_export(conn_id, recent, (uint8_t)flags,
                               data, capacity, &required))
        return NRF_ERROR_INVALID_STATE;
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_service_add(uint8_t type, ble_uuid_t const *uuid,
                                   uint16_t *handle)
{
    if (uuid == 0 || handle == 0 ||
        ((uintptr_t)uuid & 1u) != 0u || ((uintptr_t)handle & 1u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    if (type != BLE_GATTS_SRVC_TYPE_PRIMARY &&
        type != BLE_GATTS_SRVC_TYPE_SECONDARY)
        return NRF_ERROR_INVALID_PARAM;
    if (uuid->type == BLE_UUID_TYPE_BLE &&
        (uuid->uuid == 0x1800u || uuid->uuid == 0x1801u))
        return NRF_ERROR_FORBIDDEN;
    uint8_t encoded[16];
    uint8_t length = sizeof(encoded);
    uint32_t status = encode(uuid, &length, encoded);
    if (status != NRF_SUCCESS) return status;
    uint8_t result = r1_cordio_gatts_service_add(type, encoded, length,
                                                  handle);
    if (result == R1_GATTS_DB_INVALID) return NRF_ERROR_INVALID_PARAM;
    if (result == R1_GATTS_DB_NO_MEM) return NRF_ERROR_NO_MEM;
    if (result == R1_GATTS_DB_BAD_STATE) return NRF_ERROR_INVALID_STATE;
    return NRF_SUCCESS;
}

static uint8_t security_level(ble_gap_conn_sec_mode_t mode)
{
    if (mode.sm == 0u && mode.lv == 0u) return 0u;
    if (mode.sm != 1u) return 0xffu;
    if (mode.lv == 1u) return 1u;
    if (mode.lv == 2u) return 2u;
    if (mode.lv == 3u || mode.lv == 4u) return 3u;
    return 0xffu;
}

uint32_t sd_ble_gatts_characteristic_add(
    uint16_t service_handle, ble_gatts_char_md_t const *char_md,
    ble_gatts_attr_t const *value, ble_gatts_char_handles_t *handles)
{
    if (char_md == 0 || value == 0 || handles == 0 ||
        value->p_uuid == 0 || value->p_attr_md == 0)
        return NRF_ERROR_INVALID_ADDR;
    if (char_md->p_char_user_desc != 0 || char_md->p_char_pf != 0 ||
        char_md->p_user_desc_md != 0 || char_md->p_sccd_md != 0 ||
        value->init_offs != 0u ||
        value->p_attr_md->vloc != BLE_GATTS_VLOC_STACK ||
        value->p_attr_md->rd_auth != 0u)
        return NRF_ERROR_NOT_SUPPORTED;
    uint8_t read_security = security_level(value->p_attr_md->read_perm);
    uint8_t write_security = security_level(value->p_attr_md->write_perm);
    uint8_t ccc_security = 0u;
    if (char_md->p_cccd_md != 0)
        ccc_security = security_level(char_md->p_cccd_md->write_perm);
    if (read_security == 0xffu || write_security == 0xffu ||
        ccc_security == 0xffu) return NRF_ERROR_NOT_SUPPORTED;
    uint8_t uuid_bytes[16];
    uint8_t uuid_length = sizeof(uuid_bytes);
    uint32_t status = encode(value->p_uuid, &uuid_length,
                             uuid_bytes);
    if (status != NRF_SUCCESS) return status;
    uint8_t properties = 0u;
    if (char_md->char_props.broadcast) properties |= 0x01u;
    if (char_md->char_props.read) properties |= 0x02u;
    if (char_md->char_props.write_wo_resp) properties |= 0x04u;
    if (char_md->char_props.write) properties |= 0x08u;
    if (char_md->char_props.notify) properties |= 0x10u;
    if (char_md->char_props.indicate) properties |= 0x20u;
    if (char_md->char_props.auth_signed_wr) properties |= 0x40u;
    if (char_md->char_ext_props.reliable_wr ||
        char_md->char_ext_props.wr_aux ||
        char_md->p_cccd_md == 0 &&
        (char_md->char_props.notify || char_md->char_props.indicate))
        return NRF_ERROR_NOT_SUPPORTED;
    r1_gatts_characteristic_spec_t spec = {
        .service_handle = service_handle,
        .nordic_uuid = value->p_uuid->uuid,
        .nordic_uuid_type = value->p_uuid->type,
        .uuid = uuid_bytes,
        .uuid_length = uuid_length,
        .properties = properties,
        .read_security = read_security,
        .write_security = write_security,
        .ccc_security = ccc_security,
        .variable_length = value->p_attr_md->vlen,
        .write_authorize = value->p_attr_md->wr_auth,
        .max_length = value->max_len,
        .initial_length = value->init_len,
        .initial_value = value->p_value,
    };
    uint16_t value_handle = 0u;
    uint16_t ccc_handle = 0u;
    uint8_t result = r1_cordio_gatts_characteristic_add(&spec,
                               &value_handle, &ccc_handle);
    if (result == R1_GATTS_DB_INVALID) return NRF_ERROR_INVALID_PARAM;
    if (result == R1_GATTS_DB_NO_MEM) return NRF_ERROR_NO_MEM;
    if (result == R1_GATTS_DB_BAD_STATE) return NRF_ERROR_INVALID_STATE;
    memset(handles, 0, sizeof(*handles));
    handles->value_handle = value_handle;
    handles->cccd_handle = ccc_handle;
    return NRF_SUCCESS;
}

uint32_t sd_ble_gatts_rw_authorize_reply(
    uint16_t conn_handle,
    ble_gatts_rw_authorize_reply_params_t const *reply)
{
    uint8_t conn_id = active_connection(conn_handle);
    if (conn_id == 0u) return BLE_ERROR_INVALID_CONN_HANDLE;
    if (reply == 0) return NRF_ERROR_INVALID_ADDR;
    if (reply->type != BLE_GATTS_AUTHORIZE_TYPE_WRITE)
        return NRF_ERROR_NOT_SUPPORTED;
    const ble_gatts_authorize_params_t *write = &reply->params.write;
    uint8_t att_status;
    if (write->gatt_status == BLE_GATT_STATUS_SUCCESS)
        att_status = 0u;
    else if ((write->gatt_status & 0xff00u) == 0x0100u)
        att_status = (uint8_t)write->gatt_status;
    else return NRF_ERROR_INVALID_PARAM;
    uint8_t result = r1_cordio_gatts_authorize_reply(conn_id, att_status,
                        write->update, write->offset, write->p_data,
                        write->len);
    if (result == R1_GATTS_DB_INVALID) return NRF_ERROR_INVALID_PARAM;
    if (result == R1_GATTS_DB_BAD_STATE) return NRF_ERROR_INVALID_STATE;
    return NRF_SUCCESS;
}
#endif
