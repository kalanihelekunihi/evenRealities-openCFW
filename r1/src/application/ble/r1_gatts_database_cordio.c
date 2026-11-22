/* User-service ATT database for the R1 Cordio source candidate. */
#if defined(R1_CORDIO_RTC0)
#include <stddef.h>
#include <string.h>

#include "att_api.h"
#include "att_defs.h"
#include "att_uuid.h"
#include "wsf_os.h"
#include "r1_gap_service.h"
#include "r1_gatts_database_cordio.h"

enum { R1_GATTS_MAX_SERVICES = 3, R1_GATTS_MAX_ATTRS = 16,
       R1_GATTS_FIRST_USER_HANDLE = 12 };

typedef struct {
    attsGroup_t group;
    attsAttr_t attrs[R1_GATTS_MAX_ATTRS];
    uint16_t lengths[R1_GATTS_MAX_ATTRS];
    uint8_t uuid_bytes[R1_GATTS_MAX_ATTRS][16];
    uint8_t nordic_uuid_types[R1_GATTS_MAX_ATTRS];
    uint16_t nordic_uuids[R1_GATTS_MAX_ATTRS];
    uint8_t authorize_write[R1_GATTS_MAX_ATTRS];
    uint8_t properties[R1_GATTS_MAX_ATTRS];
    uint8_t count;
} r1_gatts_group_t;

typedef struct {
    uint8_t *data;
    uint16_t handle;
    uint16_t length;
    uint8_t active;
} r1_pending_write_t;

static r1_gatts_group_t *services[R1_GATTS_MAX_SERVICES];
static uint8_t service_count;
static uint16_t next_handle = R1_GATTS_FIRST_USER_HANDLE;
static r1_pending_write_t pending[3];
static void *(*allocate_bytes)(size_t);
static void (*release_bytes)(void *);
static r1_gatts_write_sink_t publish_write;

void r1_cordio_gatts_database_bind(void *(*allocate)(size_t),
                                   void (*release)(void *),
                                   r1_gatts_write_sink_t write_sink)
{
    allocate_bytes = allocate;
    release_bytes = release;
    publish_write = write_sink;
}

static uint8_t permissions(uint8_t security, uint8_t write)
{
    uint8_t value = write ? ATTS_PERMIT_WRITE : ATTS_PERMIT_READ;
    if (security >= 2u) value |= write ? ATTS_PERMIT_WRITE_ENC : ATTS_PERMIT_READ_ENC;
    if (security >= 3u) value |= write ? ATTS_PERMIT_WRITE_AUTH : ATTS_PERMIT_READ_AUTH;
    return security == 0u ? 0u : value;
}

static uint8_t write_callback(dmConnId_t conn_id, uint16_t handle,
                              uint8_t operation, uint16_t offset,
                              uint16_t length, uint8_t *data,
                              attsAttr_t *attribute)
{
    if (conn_id < 1u || conn_id > 3u || offset != 0u ||
        (operation != ATT_PDU_WRITE_REQ && operation != ATT_PDU_WRITE_CMD))
        return ATT_ERR_INVALID_PDU;
    r1_gatts_group_t *service = 0;
    uint8_t index = 0u;
    for (uint8_t i = 0u; i < service_count; ++i) {
        if (handle >= services[i]->group.startHandle &&
            handle <= services[i]->group.endHandle) {
            service = services[i];
            index = (uint8_t)(handle - service->group.startHandle);
            break;
        }
    }
    if (service == 0 || &service->attrs[index] != attribute)
        return ATT_ERR_HANDLE;
    if (service->authorize_write[index]) {
        if (operation != ATT_PDU_WRITE_REQ) return ATT_ERR_WRITE;
        r1_pending_write_t *request = &pending[conn_id - 1u];
        if (__atomic_load_n(&request->active, __ATOMIC_ACQUIRE) != 0u)
            return ATT_ERR_IN_PROGRESS;
        uint8_t *copy = allocate_bytes == 0 ? 0 :
            allocate_bytes(length != 0u ? length : 1u);
        if (copy == 0) return ATT_ERR_RESOURCES;
        if (length != 0u) memcpy(copy, data, length);
        request->data = copy;
        request->handle = handle;
        request->length = length;
        __atomic_store_n(&request->active, 1u, __ATOMIC_RELEASE);
        if (publish_write == 0 || !publish_write(conn_id, handle,
                service->nordic_uuid_types[index],
                service->nordic_uuids[index], operation, data, length, true)) {
            __atomic_store_n(&request->active, 0u, __ATOMIC_RELEASE);
            release_bytes(copy);
            return ATT_ERR_RESOURCES;
        }
        return ATT_RSP_PENDING;
    }
    if (publish_write == 0 || !publish_write(conn_id, handle,
            service->nordic_uuid_types[index],
            service->nordic_uuids[index], operation, data, length, false))
        return ATT_ERR_RESOURCES;
    if (length != 0u) memcpy(attribute->pValue, data, length);
    if ((attribute->settings & ATTS_SET_VARIABLE_LEN) != 0u)
        *attribute->pLen = length;
    return ATT_SUCCESS;
}

uint8_t r1_cordio_gatts_service_add(uint8_t type, const uint8_t *uuid,
                                     uint8_t uuid_length, uint16_t *handle)
{
    if ((type != 1u && type != 2u) || uuid == 0 || handle == 0 ||
        (uuid_length != 2u && uuid_length != 16u))
        return R1_GATTS_DB_INVALID;
    if (service_count == R1_GATTS_MAX_SERVICES || next_handle == 0xffffu)
        return R1_GATTS_DB_NO_MEM;
    if (allocate_bytes == 0 || release_bytes == 0 || publish_write == 0)
        return R1_GATTS_DB_BAD_STATE;
    r1_gatts_group_t *service = allocate_bytes(sizeof(*service));
    if (service == 0) return R1_GATTS_DB_NO_MEM;
    uint8_t *value = allocate_bytes(uuid_length);
    if (value == 0) {
        release_bytes(service);
        return R1_GATTS_DB_NO_MEM;
    }
    memset(service, 0, sizeof(*service));
    memcpy(value, uuid, uuid_length);
    service->count = 1u;
    service->lengths[0] = uuid_length;
    service->attrs[0].pUuid = type == 1u ? attPrimSvcUuid : attSecSvcUuid;
    service->attrs[0].pValue = value;
    service->attrs[0].pLen = &service->lengths[0];
    service->attrs[0].maxLen = uuid_length;
    service->attrs[0].permissions = ATTS_PERMIT_READ;
    service->group.pAttr = service->attrs;
    service->group.startHandle = next_handle;
    service->group.endHandle = next_handle;
    AttsAddGroup(&service->group);
    services[service_count++] = service;
    *handle = next_handle++;
    return R1_GATTS_DB_OK;
}

uint8_t r1_cordio_gatts_characteristic_add(
    const r1_gatts_characteristic_spec_t *spec, uint16_t *value_handle,
    uint16_t *ccc_handle)
{
    if (spec == 0 || value_handle == 0 || ccc_handle == 0 ||
        spec->uuid == 0 || (spec->uuid_length != 2u && spec->uuid_length != 16u) ||
        spec->max_length == 0u || spec->max_length > 244u ||
        spec->initial_length > spec->max_length ||
        (spec->initial_length != 0u && spec->initial_value == 0) ||
        spec->read_security > 3u || spec->write_security > 3u ||
        spec->ccc_security > 3u ||
        (spec->write_authorize &&
         (spec->write_security == 0u ||
          (spec->properties & ATT_PROP_WRITE) == 0u)))
        return R1_GATTS_DB_INVALID;
    if (service_count == 0u ||
        services[service_count - 1u]->group.startHandle != spec->service_handle)
        return R1_GATTS_DB_BAD_STATE;
    r1_gatts_group_t *service = services[service_count - 1u];
    uint8_t has_ccc = (spec->properties & (ATT_PROP_NOTIFY | ATT_PROP_INDICATE)) != 0u;
    uint8_t required = has_ccc ? 3u : 2u;
    if (service->count + required > R1_GATTS_MAX_ATTRS ||
        (uint32_t)next_handle + required >= 0xffffu)
        return R1_GATTS_DB_NO_MEM;
    uint8_t *declaration = allocate_bytes((size_t)(3u + spec->uuid_length));
    if (declaration == 0) return R1_GATTS_DB_NO_MEM;
    uint8_t *value = allocate_bytes(spec->max_length);
    if (value == 0) {
        release_bytes(declaration);
        return R1_GATTS_DB_NO_MEM;
    }
    uint8_t *ccc = 0;
    if (has_ccc) {
        ccc = allocate_bytes(2u);
        if (ccc == 0) {
            release_bytes(value);
            release_bytes(declaration);
            return R1_GATTS_DB_NO_MEM;
        }
    }
    uint16_t value_id = (uint16_t)(next_handle + 1u);
    uint16_t ccc_id = has_ccc ? (uint16_t)(next_handle + 2u) : 0u;
    if (has_ccc && !r1_cordio_ccc_register(ccc_id,
            (uint16_t)(((spec->properties & ATT_PROP_NOTIFY) ? ATT_CLIENT_CFG_NOTIFY : 0u) |
                       ((spec->properties & ATT_PROP_INDICATE) ? ATT_CLIENT_CFG_INDICATE : 0u)),
            spec->ccc_security != 0u ? (uint8_t)(spec->ccc_security - 1u) : 0u)) {
        release_bytes(ccc);
        release_bytes(value);
        release_bytes(declaration);
        return R1_GATTS_DB_BAD_STATE;
    }
    declaration[0] = spec->properties;
    declaration[1] = (uint8_t)value_id;
    declaration[2] = (uint8_t)(value_id >> 8);
    memcpy(declaration + 3u, spec->uuid, spec->uuid_length);
    memset(value, 0, spec->max_length);
    if (spec->initial_length != 0u)
        memcpy(value, spec->initial_value, spec->initial_length);
    uint8_t declaration_index = service->count;
    uint8_t value_index = (uint8_t)(declaration_index + 1u);
    attsAttr_t *decl = &service->attrs[declaration_index];
    service->lengths[declaration_index] = (uint16_t)(3u + spec->uuid_length);
    *decl = (attsAttr_t){attChUuid, declaration,
                         &service->lengths[declaration_index],
                         service->lengths[declaration_index], 0u,
                         ATTS_PERMIT_READ};
    attsAttr_t *attr = &service->attrs[value_index];
    memcpy(service->uuid_bytes[value_index], spec->uuid, spec->uuid_length);
    service->lengths[value_index] = spec->initial_length;
    *attr = (attsAttr_t){service->uuid_bytes[value_index], value,
                         &service->lengths[value_index], spec->max_length,
                         (uint8_t)((spec->uuid_length == 16u ? ATTS_SET_UUID_128 : 0u) |
                                   (spec->variable_length ? ATTS_SET_VARIABLE_LEN : 0u) |
                                   (spec->write_security ? ATTS_SET_WRITE_CBACK : 0u)),
                         (uint8_t)(permissions(spec->read_security, 0u) |
                                   permissions(spec->write_security, 1u))};
    service->nordic_uuid_types[value_index] = spec->nordic_uuid_type;
    service->nordic_uuids[value_index] = spec->nordic_uuid;
    service->authorize_write[value_index] = spec->write_authorize;
    service->properties[value_index] = spec->properties;
    service->group.writeCback = write_callback;
    if (has_ccc) {
        uint8_t ccc_index = (uint8_t)(value_index + 1u);
        memset(ccc, 0, 2u);
        service->lengths[ccc_index] = 2u;
        service->attrs[ccc_index] = (attsAttr_t){attCliChCfgUuid, ccc,
            &service->lengths[ccc_index], 2u, ATTS_SET_CCC,
            (uint8_t)(ATTS_PERMIT_READ | permissions(spec->ccc_security, 1u))};
    }
    WsfTaskLock();
    service->count = (uint8_t)(service->count + required);
    service->group.endHandle = (uint16_t)(next_handle + required - 1u);
    next_handle = (uint16_t)(next_handle + required);
    WsfTaskUnlock();
    *value_handle = value_id;
    *ccc_handle = ccc_id;
    return R1_GATTS_DB_OK;
}

uint8_t r1_cordio_gatts_authorize_reply(uint8_t conn_id,
                                        uint8_t att_status, uint8_t update,
                                        uint16_t offset, const uint8_t *data,
                                        uint16_t length)
{
    if (conn_id < 1u || conn_id > 3u || offset != 0u)
        return R1_GATTS_DB_INVALID;
    r1_pending_write_t *request = &pending[conn_id - 1u];
    if (__atomic_load_n(&request->active, __ATOMIC_ACQUIRE) == 0u)
        return R1_GATTS_DB_BAD_STATE;
    if (att_status == ATT_SUCCESS && update == 0u)
        return R1_GATTS_DB_INVALID;
    uint16_t handle = request->handle;
    uint8_t *original = request->data;
    uint8_t status = att_status;
    WsfTaskLock();
    if (status == ATT_SUCCESS) {
        const uint8_t *source = data != 0 ? data : original;
        uint16_t size = data != 0 ? length : request->length;
        status = AttsSetAttr(handle, size, (uint8_t *)source);
    }
    __atomic_store_n(&request->active, 0u, __ATOMIC_RELEASE);
    AttsContinueWriteReq(conn_id, handle, status);
    WsfTaskUnlock();
    release_bytes(original);
    return R1_GATTS_DB_OK;
}

void r1_cordio_gatts_clear_pending(uint8_t conn_id)
{
    if (conn_id < 1u || conn_id > 3u) return;
    r1_pending_write_t *request = &pending[conn_id - 1u];
    if (__atomic_exchange_n(&request->active, 0u, __ATOMIC_ACQ_REL) != 0u)
        release_bytes(request->data);
}

bool r1_cordio_gatts_hvx_details(uint16_t value_handle, uint16_t *ccc_handle,
                                uint8_t *properties, uint16_t *max_length)
{
    if (ccc_handle == 0 || properties == 0 || max_length == 0) return false;
    bool found = false;
    WsfTaskLock();
    for (uint8_t i = 0u; i < service_count && !found; ++i) {
        r1_gatts_group_t *service = services[i];
        if (value_handle < service->group.startHandle ||
            value_handle > service->group.endHandle) continue;
        uint8_t index = (uint8_t)(value_handle - service->group.startHandle);
        if (index >= service->count || service->properties[index] == 0u) break;
        *properties = service->properties[index];
        *max_length = service->attrs[index].maxLen;
        *ccc_handle = (uint16_t)(value_handle + 1u);
        found = index + 1u < service->count &&
                service->attrs[index + 1u].pUuid == attCliChCfgUuid;
    }
    WsfTaskUnlock();
    return found;
}
#endif
