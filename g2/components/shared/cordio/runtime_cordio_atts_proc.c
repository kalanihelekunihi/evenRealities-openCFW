/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 Cordio common ATT server processors.  Packetcraft
 * r20.05c supplies the public business oracle; the authenticated G2 MTU floor
 * of 247 and fixed-SRAM callback ABI are preserved explicitly.
 */

#include "runtime_cordio_atts_proc.h"

#if !defined(OPEN_CFW_ATTS_PROC_UUID_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_UUID16_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_FIND_HANDLE_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_FIND_RANGE_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_PERMISSIONS_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_MTU_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_FIND_INFO_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_READ_ONLY) && \
    !defined(OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_ONLY)
#define OPEN_CFW_ATTS_PROC_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_PROC_PRODUCTION
#define OPEN_CFW_ATTS_PROC_GROUP_QUEUE \
    (*(struct open_cfw_cordio_wsf_queue_candidate *)0x2006E848U)
#define OPEN_CFW_ATTS_PROC_AUTHORIZATION_CALLBACK \
    (*(open_cfw_cordio_atts_authorization_callback_t *)0x2006E858U)
#define OPEN_CFW_ATTS_PROC_CCC_CALLBACK \
    (*(open_cfw_cordio_atts_ccc_write_callback_t *)0x2006E85CU)
#define OPEN_CFW_ATTS_PROC_CONFIGURATION \
    (*(struct open_cfw_cordio_att_configuration **)0x200004B4U)
#else
#define OPEN_CFW_ATTS_PROC_GROUP_QUEUE open_cfw_cordio_atts_group_queue
#define OPEN_CFW_ATTS_PROC_AUTHORIZATION_CALLBACK \
    open_cfw_cordio_atts_authorization_callback
#define OPEN_CFW_ATTS_PROC_CCC_CALLBACK open_cfw_cordio_atts_proc_ccc_callback
#define OPEN_CFW_ATTS_PROC_CONFIGURATION open_cfw_cordio_att_configuration
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_atts_proc_read_u16(
    const uint8_t *value
)
{
    return (uint16_t)value[0] | ((uint16_t)value[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_atts_proc_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length--;
    }
}

static __attribute__((unused)) uint8_t open_cfw_cordio_atts_proc_equal(
    const uint8_t *left, const uint8_t *right, uint8_t length
)
{
    while (length != 0U) {
        if (*left++ != *right++) {
            return 0U;
        }
        length--;
    }
    return 1U;
}

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_UUID_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_uuid_compare(
    struct open_cfw_cordio_atts_attribute *attribute,
    uint8_t uuid_length,
    uint8_t *uuid
)
{
    if ((((attribute->settings & OPEN_CFW_ATTS_PROC_SET_UUID_128) == 0U)
            && (uuid_length == OPEN_CFW_ATTS_PROC_UUID_16_LENGTH))
        || (((attribute->settings & OPEN_CFW_ATTS_PROC_SET_UUID_128) != 0U)
            && (uuid_length == OPEN_CFW_ATTS_PROC_UUID_128_LENGTH))) {
        return open_cfw_cordio_atts_proc_equal(
            attribute->uuid, uuid, uuid_length
        );
    }
    if (((attribute->settings & OPEN_CFW_ATTS_PROC_SET_UUID_128) == 0U)
        && (uuid_length == OPEN_CFW_ATTS_PROC_UUID_128_LENGTH)) {
        return open_cfw_cordio_att_uuid_compare_16_to_128(
            attribute->uuid, uuid
        );
    }
    return open_cfw_cordio_att_uuid_compare_16_to_128(
        uuid, attribute->uuid
    );
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_UUID16_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_uuid16_compare(
    uint8_t *uuid16, uint8_t uuid_length, uint8_t *uuid
)
{
    if (uuid_length == OPEN_CFW_ATTS_PROC_UUID_16_LENGTH) {
        return (uint8_t)((uuid16[0] == uuid[0]) && (uuid16[1] == uuid[1]));
    }
    return open_cfw_cordio_att_uuid_compare_16_to_128(uuid16, uuid);
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_FIND_HANDLE_ONLY)
__attribute__((used, noinline))
struct open_cfw_cordio_atts_attribute *open_cfw_cordio_atts_find_by_handle(
    uint16_t handle, struct open_cfw_cordio_atts_group **group
)
{
    struct open_cfw_cordio_atts_group *current =
        OPEN_CFW_ATTS_PROC_GROUP_QUEUE.head;
    while (current != NULL) {
        if ((handle >= current->start_handle)
            && (handle <= current->end_handle)) {
            *group = current;
            return &current->attributes[handle - current->start_handle];
        }
        current = current->next;
    }
    return NULL;
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_FIND_RANGE_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_atts_find_in_range(
    uint16_t start_handle,
    uint16_t end_handle,
    struct open_cfw_cordio_atts_attribute **attribute
)
{
    struct open_cfw_cordio_atts_group *group =
        OPEN_CFW_ATTS_PROC_GROUP_QUEUE.head;
    while (group != NULL) {
        if ((start_handle < group->start_handle)
            && (end_handle >= group->start_handle)) {
            start_handle = group->start_handle;
        }
        if ((start_handle >= group->start_handle)
            && (start_handle <= group->end_handle)) {
            *attribute = &group->attributes[start_handle - group->start_handle];
            return start_handle;
        }
        group = group->next;
    }
    return OPEN_CFW_ATTS_PROC_HANDLE_NONE;
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_PERMISSIONS_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_permissions(
    uint8_t connection_id,
    uint8_t permit,
    uint16_t handle,
    uint8_t permissions
)
{
    uint8_t security_level;
    if ((permissions & permit) == 0U) {
        return permit == OPEN_CFW_ATTS_PROC_PERMIT_READ
            ? OPEN_CFW_ATTS_PROC_ERR_READ : OPEN_CFW_ATTS_WRITE_ERR_WRITE;
    }
    if (permit == OPEN_CFW_ATTS_WRITE_PERMIT_WRITE) {
        permissions >>= 4;
    }
    if ((permissions & 0x0EU) == 0U) {
        return OPEN_CFW_ATTS_WRITE_SUCCESS;
    }
    security_level = open_cfw_cordio_dm_connection_security_level(
        connection_id
    );
    if (((permissions & OPEN_CFW_ATTS_PROC_PERMIT_READ_ENCRYPTED) != 0U)
        && (security_level == OPEN_CFW_ATTS_PROC_SECURITY_NONE)) {
        return 0x05U;
    }
    if ((permissions & (OPEN_CFW_ATTS_PROC_PERMIT_READ_AUTHENTICATED
            | OPEN_CFW_ATTS_PROC_PERMIT_READ_ENCRYPTED)) ==
            (OPEN_CFW_ATTS_PROC_PERMIT_READ_AUTHENTICATED
            | OPEN_CFW_ATTS_PROC_PERMIT_READ_ENCRYPTED)
        && (security_level
            < OPEN_CFW_ATTS_PROC_SECURITY_ENCRYPTED_AUTHENTICATED)) {
        return 0x05U;
    }
    if ((permissions & OPEN_CFW_ATTS_PROC_PERMIT_READ_AUTHORIZED) != 0U) {
        if (OPEN_CFW_ATTS_PROC_AUTHORIZATION_CALLBACK == NULL) {
            return OPEN_CFW_ATTS_PROC_ERR_AUTHORIZATION;
        }
        return OPEN_CFW_ATTS_PROC_AUTHORIZATION_CALLBACK(
            connection_id, permit, handle
        );
    }
    return OPEN_CFW_ATTS_WRITE_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_MTU_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_mtu_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    uint8_t features = 0U;
    uint8_t *response;
    uint16_t peer_mtu;
    uint16_t local_mtu;
    uint16_t controller_mtu;
    (void)length;

    open_cfw_cordio_atts_csf_get_features(
        connection->connection_id, &features, 1U
    );
    if ((features & OPEN_CFW_ATTS_PROC_CSF_EATT_BEARER) != 0U) {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_PROC_MTU_REQUEST, 0U,
            OPEN_CFW_ATTS_PROC_ERR_NOT_SUPPORTED
        );
        return;
    }
    peer_mtu = open_cfw_cordio_atts_proc_read_u16(
        packet + OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START + 1U
    );
    if (peer_mtu < OPEN_CFW_ATTS_PROC_G2_MINIMUM_MTU) {
        peer_mtu = OPEN_CFW_ATTS_PROC_G2_MINIMUM_MTU;
    }
    controller_mtu = open_cfw_cordio_hci_get_maximum_receive_acl_length() - 4U;
    local_mtu = OPEN_CFW_ATTS_PROC_CONFIGURATION->mtu < controller_mtu
        ? OPEN_CFW_ATTS_PROC_CONFIGURATION->mtu : controller_mtu;
    response = open_cfw_cordio_att_message_allocate(11U);
    if (response != NULL) {
        response[8] = OPEN_CFW_ATTS_PROC_MTU_RESPONSE;
        response[9] = (uint8_t)local_mtu;
        response[10] = (uint8_t)(local_mtu >> 8);
        open_cfw_cordio_att_l2c_data_request(
            connection->main, connection->slot, 3U, response
        );
    }
    open_cfw_cordio_att_set_mtu(
        connection->main, connection->slot, peer_mtu, local_mtu
    );
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_FIND_INFO_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_find_information_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    uint8_t *buffer = NULL;
    uint8_t *cursor = NULL;
    uint8_t error = OPEN_CFW_ATTS_WRITE_SUCCESS;
    uint16_t start_handle;
    uint16_t end_handle;
    uint16_t handle;
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    (void)length;

    packet += 9U;
    start_handle = open_cfw_cordio_atts_proc_read_u16(packet);
    end_handle = open_cfw_cordio_atts_proc_read_u16(packet + 2U);
    if ((start_handle == 0U) || (start_handle > end_handle)) {
        error = OPEN_CFW_ATTS_WRITE_ERR_HANDLE;
    }
    if (error == OPEN_CFW_ATTS_WRITE_SUCCESS) {
        buffer = open_cfw_cordio_att_message_allocate((uint16_t)(mtu + 8U));
        if (buffer == NULL) {
            error = OPEN_CFW_ATTS_PROC_ERR_RESOURCES;
        } else {
            cursor = buffer + 8U;
            *cursor++ = OPEN_CFW_ATTS_PROC_FIND_INFO_RESPONSE;
            *cursor++ = OPEN_CFW_ATTS_PROC_FIND_HANDLE_16_UUID;
            handle = start_handle;
            while ((handle = open_cfw_cordio_atts_find_in_range(
                    handle, end_handle, &attribute)) != 0U) {
                if ((attribute->settings & OPEN_CFW_ATTS_PROC_SET_UUID_128)
                    != 0U) {
                    if (cursor == buffer + 10U) {
                        cursor--;
                        *cursor++ = OPEN_CFW_ATTS_PROC_FIND_HANDLE_128_UUID;
                        *cursor++ = (uint8_t)handle;
                        *cursor++ = (uint8_t)(handle >> 8);
                        open_cfw_cordio_atts_proc_copy(
                            cursor, attribute->uuid, 16U
                        );
                        cursor += 16U;
                    }
                    break;
                }
                if (cursor + 4U <= buffer + 8U + mtu) {
                    *cursor++ = (uint8_t)handle;
                    *cursor++ = (uint8_t)(handle >> 8);
                    *cursor++ = attribute->uuid[0];
                    *cursor++ = attribute->uuid[1];
                } else {
                    break;
                }
                if ((handle == OPEN_CFW_ATTS_PROC_HANDLE_MAX)
                    || (++handle > end_handle)) {
                    break;
                }
            }
            if (cursor == buffer + 10U) {
                open_cfw_cordio_wsf_message_free(buffer);
                error = OPEN_CFW_ATTS_PROC_ERR_NOT_FOUND;
            }
        }
    }
    open_cfw_cordio_atts_discovery_busy(connection);
    if (error == OPEN_CFW_ATTS_WRITE_SUCCESS) {
        open_cfw_cordio_att_l2c_data_request(
            connection->main, connection->slot,
            (uint16_t)(cursor - (buffer + 8U)), buffer
        );
    } else {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_PROC_FIND_INFO_REQUEST, start_handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_READ_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_read_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    open_cfw_cordio_atts_read_callback_t read_callback;
    uint8_t *response;
    uint8_t error = OPEN_CFW_ATTS_WRITE_SUCCESS;
    uint16_t handle = open_cfw_cordio_atts_proc_read_u16(packet + 9U);
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    uint16_t read_length;
    (void)length;

    attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
    if (attribute == NULL) {
        error = OPEN_CFW_ATTS_WRITE_ERR_HANDLE;
    } else if ((error = open_cfw_cordio_atts_permissions(
            connection->main->connection_id,
            OPEN_CFW_ATTS_PROC_PERMIT_READ,
            handle, attribute->permissions
        )) == OPEN_CFW_ATTS_WRITE_SUCCESS) {
        read_callback = (open_cfw_cordio_atts_read_callback_t)
            group->read_callback;
        if (((attribute->settings
                & OPEN_CFW_ATTS_PROC_SET_READ_CALLBACK) != 0U)
            && (read_callback != NULL)) {
            error = read_callback(
                connection->main->connection_id, handle,
                OPEN_CFW_ATTS_PROC_READ_REQUEST, 0U, attribute
            );
        } else if (((attribute->settings & OPEN_CFW_ATTS_PROC_SET_CCC) != 0U)
            && (OPEN_CFW_ATTS_PROC_CCC_CALLBACK != NULL)) {
            error = OPEN_CFW_ATTS_PROC_CCC_CALLBACK(
                connection->main->connection_id,
                OPEN_CFW_ATTS_PROC_METHOD_READ, handle, attribute->value
            );
        }
        if (error == OPEN_CFW_ATTS_WRITE_SUCCESS) {
            read_length = *attribute->length < (uint16_t)(mtu - 1U)
                ? *attribute->length : (uint16_t)(mtu - 1U);
            response = open_cfw_cordio_att_message_allocate(
                (uint16_t)(9U + read_length)
            );
            if (response != NULL) {
                response[8] = OPEN_CFW_ATTS_PROC_READ_RESPONSE;
                open_cfw_cordio_atts_proc_copy(
                    response + 9U, attribute->value, read_length
                );
                open_cfw_cordio_att_l2c_data_request(
                    connection->main, connection->slot,
                    (uint16_t)(1U + read_length), response
                );
            }
        }
    }
    if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_PROC_READ_REQUEST, handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_read_multiple_variable_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    open_cfw_cordio_atts_read_callback_t read_callback;
    uint8_t *buffer;
    uint8_t *cursor;
    uint8_t error = OPEN_CFW_ATTS_WRITE_SUCCESS;
    uint16_t handle = 0U;
    uint16_t response_length = 0U;
    uint16_t read_length;
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;

    packet += 9U;
    length -= 1U;
    buffer = open_cfw_cordio_att_message_allocate((uint16_t)(8U + mtu));
    if (buffer != NULL) {
        cursor = buffer + 9U;
        while (length > 0U) {
            handle = open_cfw_cordio_atts_proc_read_u16(packet);
            packet += 2U;
            length -= 2U;
            attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
            if (attribute == NULL) {
                error = OPEN_CFW_ATTS_WRITE_ERR_HANDLE;
                break;
            }
            error = open_cfw_cordio_atts_permissions(
                connection->main->connection_id,
                OPEN_CFW_ATTS_PROC_PERMIT_READ,
                handle, attribute->permissions
            );
            if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
                break;
            }
            read_callback = (open_cfw_cordio_atts_read_callback_t)
                group->read_callback;
            if (((attribute->settings
                    & OPEN_CFW_ATTS_PROC_SET_READ_CALLBACK) != 0U)
                && (read_callback != NULL)) {
                error = read_callback(
                    connection->main->connection_id, handle,
                    OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_REQUEST, 0U, attribute
                );
            } else if (((attribute->settings
                    & OPEN_CFW_ATTS_PROC_SET_CCC) != 0U)
                && (OPEN_CFW_ATTS_PROC_CCC_CALLBACK != NULL)) {
                error = OPEN_CFW_ATTS_PROC_CCC_CALLBACK(
                    connection->main->connection_id,
                    OPEN_CFW_ATTS_PROC_METHOD_READ, handle, attribute->value
                );
            }
            if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
                break;
            }
            read_length = *attribute->length <
                    (uint16_t)(mtu - response_length - 9U)
                ? *attribute->length
                : (uint16_t)(mtu - response_length - 9U);
            *cursor++ = (uint8_t)read_length;
            *cursor++ = (uint8_t)(read_length >> 8);
            open_cfw_cordio_atts_proc_copy(
                cursor, attribute->value, read_length
            );
            cursor += read_length;
            response_length += read_length + 2U;
            if (read_length < *attribute->length) {
                break;
            }
        }
        if (error == OPEN_CFW_ATTS_WRITE_SUCCESS) {
            buffer[8] = OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_RESPONSE;
            open_cfw_cordio_att_l2c_data_request(
                connection->main, connection->slot,
                (uint16_t)(1U + response_length), buffer
            );
        } else {
            open_cfw_cordio_att_message_free(
                buffer, OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_RESPONSE
            );
        }
    }
    if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_REQUEST, handle, error
        );
    }
}
#endif
