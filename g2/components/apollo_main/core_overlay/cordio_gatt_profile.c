/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the six Packetcraft Cordio r20.05c gatt_main.c
 * functions linked by G2 2.2.6.10.  The G2-specific EasyLogger expansion in
 * GattDiscover is diagnostic-only and intentionally omitted.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_GATT_CONNECTION_NONE 0u
#define OPEN_CFW_GATT_CONNECTION_MAX 3u
#define OPEN_CFW_GATT_SERVICE_UUID_LENGTH 2u
#define OPEN_CFW_GATT_DISCOVERY_HANDLE_COUNT 3u
#define OPEN_CFW_GATT_SERVICE_CHANGED_INDEX 0u
#define OPEN_CFW_GATT_SERVICE_CHANGED_HANDLE 0x12u
#define OPEN_CFW_GATT_CLIENT_FEATURES_HANDLE 0x15u
#define OPEN_CFW_GATT_CLIENT_FEATURES_LENGTH 1u
#define OPEN_CFW_GATT_SUCCESS 0u
#define OPEN_CFW_GATT_NOT_FOUND 0x0au

struct open_cfw_gatt_event {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
    uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
    uint8_t reserved;
    uint16_t mtu;
};

struct open_cfw_gatt_attribute {
    const uint8_t *uuid;
    uint8_t *value;
    uint16_t *length;
    uint16_t maximum_length;
    uint8_t settings;
    uint8_t permissions;
};

struct open_cfw_gatt_control {
    uint8_t service_changed_index_set;
    uint8_t service_changed_index;
};

#if UINTPTR_MAX == 0xffffffffu
_Static_assert(offsetof(struct open_cfw_gatt_event, handle) == 0x0au,
    "G2 ATT event handle ABI changed");
_Static_assert(offsetof(struct open_cfw_gatt_attribute, value) == 0x04u,
    "G2 ATT attribute value ABI changed");
#endif

#ifndef OPEN_CFW_GATT_CONTROL
#define OPEN_CFW_GATT_CONTROL \
    ((volatile struct open_cfw_gatt_control *)(uintptr_t)0x20074f38u)
#endif
#ifndef OPEN_CFW_GATT_SERVICE_UUID
#define OPEN_CFW_GATT_SERVICE_UUID ((const uint8_t *)(uintptr_t)0x0078f53au)
#endif
#ifndef OPEN_CFW_GATT_DISCOVERY_LIST
#define OPEN_CFW_GATT_DISCOVERY_LIST ((const void *)(uintptr_t)0x200030d0u)
#endif

#ifndef OPEN_CFW_GATT_DISCOVER_SERVICE
void open_cfw_retained_gatt_discover_service(
    uint8_t connection_id, uint8_t uuid_length, const uint8_t *uuid,
    uint8_t handle_count, const void *characteristics, uint16_t *handles
);
#define OPEN_CFW_GATT_DISCOVER_SERVICE(...) \
    open_cfw_retained_gatt_discover_service(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_GATT_SERVICE_CHANGED
void open_cfw_retained_gatt_service_changed(struct open_cfw_gatt_event *event);
#define OPEN_CFW_GATT_SERVICE_CHANGED(event) \
    open_cfw_retained_gatt_service_changed(event)
#endif
#ifndef OPEN_CFW_GATT_CCC_ENABLED
uint8_t open_cfw_retained_gatt_ccc_enabled(
    uint8_t connection_id, uint8_t index
);
#define OPEN_CFW_GATT_CCC_ENABLED(connection_id, index) \
    open_cfw_retained_gatt_ccc_enabled((connection_id), (index))
#endif
#ifndef OPEN_CFW_GATT_HANDLE_VALUE_INDICATION
void open_cfw_retained_gatt_handle_value_indication(
    uint8_t connection_id, uint16_t handle, uint16_t length,
    const uint8_t *value
);
#define OPEN_CFW_GATT_HANDLE_VALUE_INDICATION(...) \
    open_cfw_retained_gatt_handle_value_indication(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_GATT_GET_CLIENT_FEATURES
void open_cfw_retained_gatt_get_client_features(
    uint8_t connection_id, uint8_t *features, uint8_t length
);
#define OPEN_CFW_GATT_GET_CLIENT_FEATURES(...) \
    open_cfw_retained_gatt_get_client_features(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_GATT_WRITE_CLIENT_FEATURES
uint8_t open_cfw_retained_gatt_write_client_features(
    uint8_t connection_id, uint16_t offset, uint16_t length,
    const uint8_t *value
);
#define OPEN_CFW_GATT_WRITE_CLIENT_FEATURES(...) \
    open_cfw_retained_gatt_write_client_features(__VA_ARGS__)
#endif

void open_cfw_gatt_discover(uint8_t connection_id, uint16_t *handles);
uint8_t open_cfw_gatt_value_update(
    uint16_t *handles, struct open_cfw_gatt_event *event
);
void open_cfw_gatt_set_service_changed_index(uint8_t index);
void open_cfw_gatt_send_service_changed_indication(
    uint8_t connection_id, uint16_t start, uint16_t end
);
uint8_t open_cfw_gatt_read_callback(
    uint8_t connection_id, uint16_t handle, uint8_t operation,
    uint16_t offset, struct open_cfw_gatt_attribute *attribute
);
uint8_t open_cfw_gatt_write_callback(
    uint8_t connection_id, uint16_t handle, uint8_t operation,
    uint16_t offset, uint16_t length, uint8_t *value,
    struct open_cfw_gatt_attribute *attribute
);

#if !defined(OPEN_CFW_GATT_DISCOVER_ONLY) && \
    !defined(OPEN_CFW_GATT_VALUE_UPDATE_ONLY) && \
    !defined(OPEN_CFW_GATT_SET_INDEX_ONLY) && \
    !defined(OPEN_CFW_GATT_SEND_CHANGED_ONLY) && \
    !defined(OPEN_CFW_GATT_READ_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_GATT_WRITE_CALLBACK_ONLY)
#define OPEN_CFW_GATT_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_GATT_BUILD_ALL) || defined(OPEN_CFW_GATT_DISCOVER_ONLY)
void open_cfw_gatt_discover(uint8_t connection_id, uint16_t *handles)
{
    OPEN_CFW_GATT_DISCOVER_SERVICE(
        connection_id, OPEN_CFW_GATT_SERVICE_UUID_LENGTH,
        OPEN_CFW_GATT_SERVICE_UUID, OPEN_CFW_GATT_DISCOVERY_HANDLE_COUNT,
        OPEN_CFW_GATT_DISCOVERY_LIST, handles
    );
}
#endif

#if defined(OPEN_CFW_GATT_BUILD_ALL) || defined(OPEN_CFW_GATT_VALUE_UPDATE_ONLY)
uint8_t open_cfw_gatt_value_update(
    uint16_t *handles, struct open_cfw_gatt_event *event
)
{
    if (event->handle == handles[OPEN_CFW_GATT_SERVICE_CHANGED_INDEX]) {
        OPEN_CFW_GATT_SERVICE_CHANGED(event);
        return OPEN_CFW_GATT_SUCCESS;
    }
    return OPEN_CFW_GATT_NOT_FOUND;
}
#endif

#if defined(OPEN_CFW_GATT_BUILD_ALL) || defined(OPEN_CFW_GATT_SET_INDEX_ONLY)
void open_cfw_gatt_set_service_changed_index(uint8_t index)
{
    OPEN_CFW_GATT_CONTROL->service_changed_index_set = 1u;
    OPEN_CFW_GATT_CONTROL->service_changed_index = index;
}
#endif

#if defined(OPEN_CFW_GATT_BUILD_ALL) || defined(OPEN_CFW_GATT_SEND_CHANGED_ONLY)
void open_cfw_gatt_send_service_changed_indication(
    uint8_t connection_id, uint16_t start, uint16_t end
)
{
    uint8_t value[4];
    uint8_t candidate;

    if (OPEN_CFW_GATT_CONTROL->service_changed_index_set == 0u) {
        return;
    }
    value[0] = (uint8_t)start;
    value[1] = (uint8_t)(start >> 8);
    value[2] = (uint8_t)end;
    value[3] = (uint8_t)(end >> 8);
    if (connection_id == OPEN_CFW_GATT_CONNECTION_NONE) {
        for (candidate = 1u; candidate <= OPEN_CFW_GATT_CONNECTION_MAX;
             ++candidate) {
            if (OPEN_CFW_GATT_CCC_ENABLED(
                    candidate, OPEN_CFW_GATT_CONTROL->service_changed_index)) {
                OPEN_CFW_GATT_HANDLE_VALUE_INDICATION(
                    candidate, OPEN_CFW_GATT_SERVICE_CHANGED_HANDLE,
                    sizeof(value), value
                );
            }
        }
    } else if (OPEN_CFW_GATT_CCC_ENABLED(
                   connection_id,
                   OPEN_CFW_GATT_CONTROL->service_changed_index)) {
        OPEN_CFW_GATT_HANDLE_VALUE_INDICATION(
            connection_id, OPEN_CFW_GATT_SERVICE_CHANGED_HANDLE,
            sizeof(value), value
        );
    }
}
#endif

#if defined(OPEN_CFW_GATT_BUILD_ALL) || defined(OPEN_CFW_GATT_READ_CALLBACK_ONLY)
uint8_t open_cfw_gatt_read_callback(
    uint8_t connection_id, uint16_t handle, uint8_t operation,
    uint16_t offset, struct open_cfw_gatt_attribute *attribute
)
{
    uint8_t features[OPEN_CFW_GATT_CLIENT_FEATURES_LENGTH];
    (void)operation;
    (void)offset;
    if (handle == OPEN_CFW_GATT_CLIENT_FEATURES_HANDLE) {
        OPEN_CFW_GATT_GET_CLIENT_FEATURES(
            connection_id, features, sizeof(features)
        );
        attribute->value[0] = features[0];
    }
    return OPEN_CFW_GATT_SUCCESS;
}
#endif

#if defined(OPEN_CFW_GATT_BUILD_ALL) || defined(OPEN_CFW_GATT_WRITE_CALLBACK_ONLY)
uint8_t open_cfw_gatt_write_callback(
    uint8_t connection_id, uint16_t handle, uint8_t operation,
    uint16_t offset, uint16_t length, uint8_t *value,
    struct open_cfw_gatt_attribute *attribute
)
{
    (void)operation;
    (void)attribute;
    if (handle == OPEN_CFW_GATT_CLIENT_FEATURES_HANDLE) {
        return OPEN_CFW_GATT_WRITE_CLIENT_FEATURES(
            connection_id, offset, length, value
        );
    }
    return OPEN_CFW_GATT_SUCCESS;
}
#endif
