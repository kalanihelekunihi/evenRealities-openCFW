/* R1 Generic Access service exposed through Cordio ATT. */
#if defined(R1_CORDIO_RTC0)
#include <string.h>

#include "att_api.h"
#include "att_defs.h"
#include "att_uuid.h"
#include "wsf_assert.h"
#include "wsf_os.h"
#include "r1_gap_service.h"

enum { R1_GAP_SVC = 1, R1_GAP_NAME_CH = 2, R1_GAP_NAME = 3,
       R1_GAP_APPEARANCE_CH = 4, R1_GAP_APPEARANCE = 5,
       R1_GAP_PPCP_CH = 6, R1_GAP_PPCP = 7,
       R1_GATT_SVC = 8, R1_GATT_SC_CH = 9, R1_GATT_SC = 10,
       R1_GATT_SC_CCC = 11,
       R1_GAP_NAME_MAX = 32, R1_CCC_MAX = 8 };

static const uint8_t service_value[] = {0x00, 0x18};
static const uint16_t service_length = sizeof(service_value);
static const uint8_t name_decl[] = {ATT_PROP_READ | ATT_PROP_WRITE,
                                    R1_GAP_NAME, 0, 0x00, 0x2a};
static const uint16_t name_decl_length = sizeof(name_decl);
static const uint8_t appearance_decl[] = {ATT_PROP_READ,
                                          R1_GAP_APPEARANCE, 0, 0x01, 0x2a};
static const uint16_t appearance_decl_length = sizeof(appearance_decl);
static const uint8_t ppcp_decl[] = {ATT_PROP_READ,
                                    R1_GAP_PPCP, 0, 0x04, 0x2a};
static const uint16_t ppcp_decl_length = sizeof(ppcp_decl);

static uint8_t name_value[R1_GAP_NAME_MAX];
static uint16_t name_length;
static uint8_t appearance_value[2];
static const uint16_t appearance_length = sizeof(appearance_value);
static uint8_t ppcp_value[8];
static const uint16_t ppcp_length = sizeof(ppcp_value);
static uint8_t initialized;

static attsAttr_t attributes[] = {
    {attPrimSvcUuid, (uint8_t *)service_value, (uint16_t *)&service_length,
     sizeof(service_value), 0, ATTS_PERMIT_READ},
    {attChUuid, (uint8_t *)name_decl, (uint16_t *)&name_decl_length,
     sizeof(name_decl), 0, ATTS_PERMIT_READ},
    {attDnChUuid, name_value, &name_length, sizeof(name_value),
     ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
    {attChUuid, (uint8_t *)appearance_decl, (uint16_t *)&appearance_decl_length,
     sizeof(appearance_decl), 0, ATTS_PERMIT_READ},
    {attApChUuid, appearance_value, (uint16_t *)&appearance_length,
     sizeof(appearance_value), 0, ATTS_PERMIT_READ},
    {attChUuid, (uint8_t *)ppcp_decl, (uint16_t *)&ppcp_decl_length,
     sizeof(ppcp_decl), 0, ATTS_PERMIT_READ},
    {attPpcpChUuid, ppcp_value, (uint16_t *)&ppcp_length,
     sizeof(ppcp_value), 0, ATTS_PERMIT_READ},
};
static attsGroup_t group = {0, attributes, 0, 0, R1_GAP_SVC, R1_GAP_PPCP};

static const uint8_t gatt_service_value[] = {0x01, 0x18};
static const uint16_t gatt_service_length = sizeof(gatt_service_value);
static const uint8_t sc_declaration[] = {ATT_PROP_INDICATE,
                                         R1_GATT_SC, 0, 0x05, 0x2a};
static const uint16_t sc_declaration_length = sizeof(sc_declaration);
static const uint8_t sc_value[] = {0x01, 0x00, 0xff, 0xff};
static const uint16_t sc_length = sizeof(sc_value);
static uint8_t sc_ccc_value[2];
static const uint16_t sc_ccc_length = sizeof(sc_ccc_value);
static attsAttr_t gatt_attributes[] = {
    {attPrimSvcUuid, (uint8_t *)gatt_service_value,
     (uint16_t *)&gatt_service_length, sizeof(gatt_service_value),
     0, ATTS_PERMIT_READ},
    {attChUuid, (uint8_t *)sc_declaration,
     (uint16_t *)&sc_declaration_length, sizeof(sc_declaration),
     0, ATTS_PERMIT_READ},
    {attScChUuid, (uint8_t *)sc_value,
     (uint16_t *)&sc_length, sizeof(sc_value), 0, 0},
    {attCliChCfgUuid, sc_ccc_value, (uint16_t *)&sc_ccc_length,
     sizeof(sc_ccc_value), ATTS_SET_CCC,
     ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
};
static attsGroup_t gatt_group = {0, gatt_attributes, 0, 0,
                                 R1_GATT_SVC, R1_GATT_SC_CCC};
static attsCccSet_t ccc_set[R1_CCC_MAX] = {{R1_GATT_SC_CCC,
                                           ATT_CLIENT_CFG_INDICATE,
                                           DM_SEC_LEVEL_NONE}};
static uint8_t ccc_count = 1u;
static uint8_t ccc_frozen;
static uint16_t recent_ccc[3][R1_CCC_MAX];
static uint8_t recent_ccc_valid[3];
static bool (*ccc_sink)(uint8_t conn_id, uint16_t handle, uint16_t value);

void r1_cordio_gap_service_set_ccc_sink(
    bool (*sink)(uint8_t conn_id, uint16_t handle, uint16_t value))
{
    ccc_sink = sink;
}

static void ccc_changed(attsCccEvt_t *event)
{
    if (event->handle != ATT_HANDLE_NONE &&
        (ccc_sink == 0 ||
         !ccc_sink(event->hdr.param, event->handle, event->value))) {
        WsfAssert(__FILE__, (uint16_t)__LINE__);
    }
}

void r1_cordio_gap_service_init(void)
{
    if (initialized != 0u) return;
    AttsAddGroup(&group);
    AttsAddGroup(&gatt_group);
    AttsCccRegister(ccc_count, ccc_set, ccc_changed);
    initialized = 1u;
}

bool r1_cordio_ccc_register(uint16_t handle, uint16_t range,
                            uint8_t security_level)
{
    if (initialized == 0u || ccc_frozen != 0u ||
        ccc_count >= R1_CCC_MAX || handle <= R1_GATT_SC_CCC ||
        range == 0u || range >
        (ATT_CLIENT_CFG_NOTIFY | ATT_CLIENT_CFG_INDICATE) ||
        security_level > DM_SEC_LEVEL_ENC_LESC)
        return false;
    WsfTaskLock();
    ccc_set[ccc_count].handle = handle;
    ccc_set[ccc_count].valueRange = range;
    ccc_set[ccc_count].secLevel = security_level;
    ++ccc_count;
    AttsCccRegister(ccc_count, ccc_set, ccc_changed);
    WsfTaskUnlock();
    return true;
}

void r1_cordio_ccc_freeze(void)
{
    ccc_frozen = 1u;
}

bool r1_cordio_atts_is_ccc(uint16_t handle)
{
    WsfTaskLock();
    bool found = false;
    for (uint8_t i = 0; i < ccc_count; ++i)
        if (ccc_set[i].handle == handle) found = true;
    WsfTaskUnlock();
    return found;
}

uint16_t r1_cordio_ccc_enabled(uint8_t conn_id, uint16_t handle)
{
    WsfTaskLock();
    uint16_t enabled = 0u;
    for (uint8_t i = 0; i < ccc_count; ++i)
        if (ccc_set[i].handle == handle) {
            enabled = AttsCccEnabled(conn_id, i);
            break;
        }
    WsfTaskUnlock();
    return enabled;
}

void r1_cordio_ccc_new_connection(uint8_t conn_id)
{
    if (conn_id < 1u || conn_id > 3u) return;
    recent_ccc_valid[conn_id - 1u] = 0u;
}

void r1_cordio_ccc_retain(uint8_t conn_id)
{
    if (conn_id < 1u || conn_id > 3u) return;
    WsfTaskLock();
    for (uint8_t i = 0u; i < ccc_count; ++i)
        recent_ccc[conn_id - 1u][i] = AttsCccGet(conn_id, i);
    recent_ccc_valid[conn_id - 1u] = 1u;
    WsfTaskUnlock();
}

static bool ccc_selected(uint8_t flags, uint16_t handle)
{
    return handle <= R1_GATT_SC_CCC ? (flags & 1u) != 0u :
                                       (flags & 2u) != 0u;
}

bool r1_cordio_ccc_export(uint8_t conn_id, bool recent, uint8_t flags,
                          uint8_t *data, uint16_t capacity,
                          uint16_t *actual)
{
    if (conn_id < 1u || conn_id > 3u || actual == 0 ||
        (flags & ~3u) != 0u) return false;
    if (flags == 0u) flags = 3u;
    WsfTaskLock();
    if (recent && recent_ccc_valid[conn_id - 1u] == 0u) {
        WsfTaskUnlock();
        return false;
    }
    uint16_t bytes = 0u;
    for (uint8_t i = 0u; i < ccc_count; ++i) {
        uint16_t handle = ccc_set[i].handle;
        if (!ccc_selected(flags, handle)) continue;
        uint16_t value = recent ? recent_ccc[conn_id - 1u][i] :
                                  AttsCccGet(conn_id, i);
        if (data != 0 && bytes + 4u <= capacity) {
            data[bytes] = (uint8_t)handle;
            data[bytes + 1u] = (uint8_t)(handle >> 8);
            data[bytes + 2u] = (uint8_t)value;
            data[bytes + 3u] = (uint8_t)(value >> 8);
        }
        bytes = (uint16_t)(bytes + 4u);
    }
    *actual = bytes;
    WsfTaskUnlock();
    return true;
}

bool r1_cordio_ccc_restore(uint8_t conn_id, uint8_t flags,
                           const uint8_t *data, uint16_t length)
{
    if (conn_id < 1u || conn_id > 3u || (flags & ~3u) != 0u)
        return false;
    if (flags == 0u) flags = 3u;
    uint16_t expected = 0u;
    for (uint8_t i = 0u; i < ccc_count; ++i)
        if (ccc_selected(flags, ccc_set[i].handle)) expected += 4u;
    if (data != 0 && length != expected) return false;
    if (data == 0 && length != 0u) return false;
    WsfTaskLock();
    uint16_t offset = 0u;
    for (uint8_t i = 0u; i < ccc_count; ++i) {
        uint16_t handle = ccc_set[i].handle;
        if (!ccc_selected(flags, handle)) continue;
        if (data != 0 && ((uint16_t)data[offset] |
            ((uint16_t)data[offset + 1u] << 8)) != handle) {
            WsfTaskUnlock();
            return false;
        }
        offset = (uint16_t)(offset + 4u);
    }
    offset = 0u;
    for (uint8_t i = 0u; i < ccc_count; ++i) {
        if (!ccc_selected(flags, ccc_set[i].handle)) continue;
        uint16_t value = data == 0 ? 0u :
            (uint16_t)data[offset + 2u] |
            ((uint16_t)data[offset + 3u] << 8);
        if ((value & ~ccc_set[i].valueRange) != 0u) {
            WsfTaskUnlock();
            return false;
        }
        offset = (uint16_t)(offset + 4u);
    }
    offset = 0u;
    for (uint8_t i = 0u; i < ccc_count; ++i) {
        if (!ccc_selected(flags, ccc_set[i].handle)) continue;
        uint16_t value = data == 0 ? 0u :
            (uint16_t)data[offset + 2u] |
            ((uint16_t)data[offset + 3u] << 8);
        AttsCccSet(conn_id, i, value);
        offset = (uint16_t)(offset + 4u);
    }
    WsfTaskUnlock();
    return true;
}

bool r1_cordio_gap_name_set(const uint8_t *name, uint16_t length)
{
    return length <= R1_GAP_NAME_MAX &&
           AttsSetAttr(R1_GAP_NAME, length, (uint8_t *)name) == ATT_SUCCESS;
}

bool r1_cordio_gap_name_read(uint8_t *destination, uint16_t capacity,
                             uint16_t *actual)
{
    WsfTaskLock();
    *actual = name_length;
    bool fits = destination == 0 || capacity >= name_length;
    if (fits && destination != 0) memcpy(destination, name_value, name_length);
    WsfTaskUnlock();
    return fits;
}

void r1_cordio_gap_appearance_set(uint16_t appearance)
{
    uint8_t value[2] = {(uint8_t)appearance, (uint8_t)(appearance >> 8)};
    (void)AttsSetAttr(R1_GAP_APPEARANCE, sizeof(value), value);
}

uint16_t r1_cordio_gap_appearance_get(void)
{
    uint16_t value;
    WsfTaskLock();
    value = (uint16_t)appearance_value[0] | ((uint16_t)appearance_value[1] << 8);
    WsfTaskUnlock();
    return value;
}

void r1_cordio_gap_ppcp_set(const uint8_t params[8])
{
    (void)AttsSetAttr(R1_GAP_PPCP, sizeof(ppcp_value), (uint8_t *)params);
}

void r1_cordio_gap_ppcp_get(uint8_t params[8])
{
    WsfTaskLock();
    memcpy(params, ppcp_value, sizeof(ppcp_value));
    WsfTaskUnlock();
}

uint8_t r1_cordio_atts_value_snapshot(uint8_t conn_id, uint16_t handle,
                                      uint16_t offset, uint8_t *destination,
                                      uint16_t capacity, uint16_t *actual)
{
    if (actual == 0) return 1u;
    WsfTaskLock();
    uint16_t length;
    uint8_t *value;
    uint8_t ccc_value[2];
    uint8_t ccc_index = ccc_count;
    for (uint8_t i = 0; i < ccc_count; ++i)
        if (ccc_set[i].handle == handle) ccc_index = i;
    if (ccc_index != ccc_count) {
        if (conn_id == 0u) {
            WsfTaskUnlock();
            return 1u;
        }
        uint16_t ccc = AttsCccGet(conn_id, ccc_index);
        ccc_value[0] = (uint8_t)ccc;
        ccc_value[1] = (uint8_t)(ccc >> 8);
        value = ccc_value;
        length = sizeof(ccc_value);
    } else if (AttsGetAttr(handle, &length, &value) != ATT_SUCCESS) {
        WsfTaskUnlock();
        return 1u;
    }
    if (offset > length) {
        WsfTaskUnlock();
        return 2u;
    }
    uint16_t available = (uint16_t)(length - offset);
    uint16_t copy = available < capacity ? available : capacity;
    if (destination != 0 && copy != 0u)
        memcpy(destination, value + offset, copy);
    *actual = length;
    WsfTaskUnlock();
    return 0u;
}
#endif
