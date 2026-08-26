/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_atts_read.h"

#if !defined(OPEN_CFW_ATTS_READ_FIND_UUID_ONLY) && \
    !defined(OPEN_CFW_ATTS_READ_FIND_SERVICE_END_ONLY) && \
    !defined(OPEN_CFW_ATTS_READ_BLOB_ONLY) && \
    !defined(OPEN_CFW_ATTS_READ_FIND_TYPE_ONLY) && \
    !defined(OPEN_CFW_ATTS_READ_TYPE_ONLY) && \
    !defined(OPEN_CFW_ATTS_READ_MULTIPLE_ONLY) && \
    !defined(OPEN_CFW_ATTS_READ_GROUP_TYPE_ONLY)
#define OPEN_CFW_ATTS_READ_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_READ_PRODUCTION
#define OPEN_CFW_ATTS_READ_GROUP_QUEUE \
    (*(struct open_cfw_cordio_wsf_queue_candidate *)0x2006E848U)
#define OPEN_CFW_ATTS_READ_CCC_CALLBACK \
    (*(open_cfw_cordio_atts_ccc_write_callback_t *)0x2006E85CU)
#define OPEN_CFW_ATTS_READ_PRIMARY_UUID ((uint8_t *)0x0078F550U)
#define OPEN_CFW_ATTS_READ_SECONDARY_UUID ((uint8_t *)0x0078F552U)
#define OPEN_CFW_ATTS_READ_DATABASE_HASH_UUID ((uint8_t *)0x0078F54EU)
#else
#define OPEN_CFW_ATTS_READ_GROUP_QUEUE open_cfw_cordio_atts_group_queue
#define OPEN_CFW_ATTS_READ_CCC_CALLBACK open_cfw_cordio_atts_proc_ccc_callback
#define OPEN_CFW_ATTS_READ_PRIMARY_UUID open_cfw_cordio_atts_primary_service_uuid
#define OPEN_CFW_ATTS_READ_SECONDARY_UUID open_cfw_cordio_atts_secondary_service_uuid
#define OPEN_CFW_ATTS_READ_DATABASE_HASH_UUID open_cfw_cordio_atts_database_hash_uuid
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_atts_read_u16(
    const uint8_t *value
)
{
    return (uint16_t)value[0] | ((uint16_t)value[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_atts_read_put_u16(
    uint8_t **destination, uint16_t value
)
{
    *(*destination)++ = (uint8_t)value;
    *(*destination)++ = (uint8_t)(value >> 8);
}

static __attribute__((unused)) void open_cfw_cordio_atts_read_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length--;
    }
}

static __attribute__((unused)) uint8_t open_cfw_cordio_atts_read_equal(
    const uint8_t *left, const uint8_t *right, uint16_t length
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

static __attribute__((unused)) uint8_t open_cfw_cordio_atts_read_invoke_callback(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    struct open_cfw_cordio_atts_group *group,
    struct open_cfw_cordio_atts_attribute *attribute,
    uint16_t handle, uint8_t opcode, uint16_t offset
)
{
    open_cfw_cordio_atts_read_callback_t callback;
    if (((attribute->settings & OPEN_CFW_ATTS_READ_SET_CALLBACK) != 0U)
        && (group->read_callback != NULL)) {
        callback = (open_cfw_cordio_atts_read_callback_t)group->read_callback;
        return callback(
            connection->main->connection_id, handle, opcode, offset, attribute
        );
    }
    if (((attribute->settings & OPEN_CFW_ATTS_READ_SET_CCC) != 0U)
        && (OPEN_CFW_ATTS_READ_CCC_CALLBACK != NULL)) {
        return OPEN_CFW_ATTS_READ_CCC_CALLBACK(
            connection->main->connection_id, OPEN_CFW_ATTS_READ_METHOD,
            handle, attribute->value
        );
    }
    return 0U;
}

static __attribute__((unused)) uint8_t open_cfw_cordio_atts_read_attribute(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    struct open_cfw_cordio_atts_group *group,
    struct open_cfw_cordio_atts_attribute *attribute,
    uint16_t handle, uint8_t opcode, uint16_t offset
)
{
    uint8_t error = open_cfw_cordio_atts_permissions(
        connection->main->connection_id, OPEN_CFW_ATTS_READ_PERMIT,
        handle, attribute->permissions
    );
    return (error != 0U) ? error : open_cfw_cordio_atts_read_invoke_callback(
        connection, group, attribute, handle, opcode, offset
    );
}

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_FIND_UUID_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_atts_find_uuid_in_range(
    uint16_t start_handle, uint16_t end_handle, uint8_t uuid_length,
    uint8_t *uuid, struct open_cfw_cordio_atts_attribute **attribute,
    struct open_cfw_cordio_atts_group **group
)
{
    struct open_cfw_cordio_atts_group *current;
    for (current = OPEN_CFW_ATTS_READ_GROUP_QUEUE.head;
         current != NULL; current = current->next) {
        if ((start_handle < current->start_handle)
            && (end_handle >= current->start_handle)) {
            start_handle = current->start_handle;
        }
        if ((start_handle >= current->start_handle)
            && (start_handle <= current->end_handle)) {
            *attribute = &current->attributes[start_handle-current->start_handle];
            while ((start_handle <= current->end_handle)
                && (start_handle <= end_handle)) {
                if (open_cfw_cordio_atts_uuid_compare(
                        *attribute, uuid_length, uuid)) {
                    *group = current;
                    return start_handle;
                }
                if (start_handle == OPEN_CFW_ATTS_READ_HANDLE_MAX) {
                    break;
                }
                start_handle++;
                (*attribute)++;
            }
        }
    }
    return OPEN_CFW_ATTS_READ_HANDLE_NONE;
}
#endif

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_FIND_SERVICE_END_ONLY)
__attribute__((used, noinline))
uint16_t open_cfw_cordio_atts_find_service_group_end(uint16_t start_handle)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    uint16_t previous;
    if (start_handle == OPEN_CFW_ATTS_READ_HANDLE_MAX) {
        return OPEN_CFW_ATTS_READ_HANDLE_MAX;
    }
    previous = start_handle++;
    for (group = OPEN_CFW_ATTS_READ_GROUP_QUEUE.head;
         group != NULL; group = group->next) {
        if (start_handle < group->start_handle) {
            start_handle = group->start_handle;
        }
        if (start_handle <= group->end_handle) {
            attribute = &group->attributes[start_handle-group->start_handle];
            while (start_handle <= group->end_handle) {
                if (open_cfw_cordio_atts_uuid_compare(
                        attribute, 2U, OPEN_CFW_ATTS_READ_PRIMARY_UUID)
                    || open_cfw_cordio_atts_uuid_compare(
                        attribute, 2U, OPEN_CFW_ATTS_READ_SECONDARY_UUID)) {
                    return previous;
                }
                if (start_handle == OPEN_CFW_ATTS_READ_HANDLE_MAX) {
                    return OPEN_CFW_ATTS_READ_HANDLE_MAX;
                }
                previous = start_handle++;
                attribute++;
            }
        }
    }
    return OPEN_CFW_ATTS_READ_HANDLE_MAX;
}
#endif

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_BLOB_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_read_blob_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    uint8_t *buffer;
    uint8_t *output;
    uint16_t handle = open_cfw_cordio_atts_read_u16(packet + 9U);
    uint16_t offset = open_cfw_cordio_atts_read_u16(packet + 11U);
    uint16_t read_length;
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    uint8_t error = 0U;
    (void)length;
    attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
    if (attribute == NULL) {
        error = OPEN_CFW_ATTS_READ_ERR_HANDLE;
    } else if ((error = open_cfw_cordio_atts_permissions(
            connection->main->connection_id, OPEN_CFW_ATTS_READ_PERMIT,
            handle, attribute->permissions)) != 0U) {
    } else if (offset > *attribute->length) {
        error = OPEN_CFW_ATTS_READ_ERR_OFFSET;
    } else {
        error = open_cfw_cordio_atts_read_invoke_callback(
            connection, group, attribute, handle,
            OPEN_CFW_ATTS_READ_BLOB_REQUEST, offset
        );
        if (error == 0U) {
            read_length = (uint16_t)(*attribute->length - offset);
            if (read_length > (uint16_t)(mtu - 1U)) {
                read_length = (uint16_t)(mtu - 1U);
            }
            buffer = open_cfw_cordio_att_message_allocate(
                (uint16_t)(9U + read_length)
            );
            if (buffer != NULL) {
                output = buffer + 8U;
                *output++ = OPEN_CFW_ATTS_READ_BLOB_RESPONSE;
                open_cfw_cordio_atts_read_copy(
                    output, attribute->value + offset, read_length
                );
                open_cfw_cordio_att_l2c_data_request(
                    connection->main, connection->slot,
                    (uint16_t)(1U + read_length), buffer
                );
            }
        }
    }
    if (error != 0U) {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_READ_BLOB_REQUEST, handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_FIND_TYPE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_find_type_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    uint8_t *buffer = NULL;
    uint8_t *output = NULL;
    uint8_t *uuid = packet + 13U;
    uint8_t *value = packet + 15U;
    uint16_t start_handle = open_cfw_cordio_atts_read_u16(packet + 9U);
    uint16_t end_handle = open_cfw_cordio_atts_read_u16(packet + 11U);
    uint16_t handle, next_handle;
    uint16_t value_length = (uint16_t)(length-OPEN_CFW_ATTS_FIND_TYPE_FIXED_LENGTH);
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    uint8_t error = 0U;
    if ((start_handle == 0U) || (start_handle > end_handle)) {
        error = OPEN_CFW_ATTS_READ_ERR_HANDLE;
    } else if ((buffer = open_cfw_cordio_att_message_allocate(
            (uint16_t)(mtu + 8U))) != NULL) {
        output = buffer + 8U;
        *output++ = OPEN_CFW_ATTS_FIND_TYPE_RESPONSE;
        handle = start_handle;
        while ((handle = open_cfw_cordio_atts_find_uuid_in_range(
                handle, end_handle, 2U, uuid, &attribute, &group)) != 0U) {
            if (((attribute->permissions & OPEN_CFW_ATTS_READ_PERMIT) != 0U)
                && ((value_length == 0U)
                    || ((value_length == *attribute->length)
                        && open_cfw_cordio_atts_read_equal(
                            value, attribute->value, value_length)))) {
                next_handle = ((uuid[0] == (uint8_t)OPEN_CFW_ATTS_READ_PRIMARY_SERVICE_UUID)
                    && (uuid[1] == (uint8_t)(OPEN_CFW_ATTS_READ_PRIMARY_SERVICE_UUID >> 8)))
                    ? open_cfw_cordio_atts_find_service_group_end(handle)
                    : handle;
                if (output <= buffer + 8U + mtu - 4U) {
                    open_cfw_cordio_atts_read_put_u16(&output, handle);
                    open_cfw_cordio_atts_read_put_u16(&output, next_handle);
                } else {
                    break;
                }
            } else {
                next_handle = handle;
            }
            if ((next_handle >= end_handle)
                || (next_handle == OPEN_CFW_ATTS_READ_HANDLE_MAX)) {
                break;
            }
            handle = (uint16_t)(next_handle + 1U);
        }
        if (output == buffer + 9U) {
            open_cfw_cordio_wsf_message_free(buffer);
            error = OPEN_CFW_ATTS_READ_ERR_NOT_FOUND;
        }
    } else {
        error = OPEN_CFW_ATTS_READ_ERR_RESOURCES;
    }
    open_cfw_cordio_atts_discovery_busy(connection);
    if (error == 0U) {
        open_cfw_cordio_att_l2c_data_request(
            connection->main, connection->slot,
            (uint16_t)(output-(buffer+8U)), buffer
        );
    } else {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_FIND_TYPE_REQUEST, start_handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_TYPE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_read_type_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_pending_database_hash_response *pending;
    uint8_t *buffer = NULL, *output = NULL, *uuid = packet + 13U;
    uint16_t start_handle = open_cfw_cordio_atts_read_u16(packet + 9U);
    uint16_t end_handle = open_cfw_cordio_atts_read_u16(packet + 11U);
    uint16_t handle;
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    uint8_t uuid_length = (uint8_t)(length-OPEN_CFW_ATTS_READ_TYPE_FIXED_LENGTH);
    uint8_t attribute_length, callback_error = 0U, error = 0U;
    if ((uuid_length != 2U) && (uuid_length != 16U)) {
        error = OPEN_CFW_ATTS_READ_ERR_INVALID_PDU;
    } else if ((start_handle == 0U) || (start_handle > end_handle)) {
        error = OPEN_CFW_ATTS_READ_ERR_HANDLE;
    } else {
        handle = open_cfw_cordio_atts_find_uuid_in_range(
            start_handle, end_handle, uuid_length, uuid, &attribute, &group
        );
        start_handle = handle;
        if (handle == 0U) {
            error = OPEN_CFW_ATTS_READ_ERR_NOT_FOUND;
        } else {
            error = open_cfw_cordio_atts_read_attribute(
                connection, group, attribute, handle,
                OPEN_CFW_ATTS_READ_TYPE_REQUEST, 0U
            );
        }
        if (error == 0U) {
            if (open_cfw_cordio_atts_read_equal(
                    uuid, OPEN_CFW_ATTS_READ_DATABASE_HASH_UUID, 2U)
                && open_cfw_cordio_atts_csf_get_hash_update_status()) {
                pending = open_cfw_cordio_wsf_buffer_allocate_candidate(
                    (uint16_t)sizeof(*pending)
                );
                connection->main->pending_database_hash_response = pending;
                if (pending != NULL) {
                    pending->start_handle = start_handle;
                    pending->handle = handle;
                } else {
                    open_cfw_cordio_atts_error_response(
                        connection->main, connection->slot,
                        OPEN_CFW_ATTS_READ_TYPE_REQUEST, start_handle,
                        OPEN_CFW_ATTS_READ_ERR_RESOURCES
                    );
                }
                return;
            }
            buffer = open_cfw_cordio_att_message_allocate((uint16_t)(mtu+8U));
            if (buffer == NULL) {
                error = OPEN_CFW_ATTS_READ_ERR_RESOURCES;
            } else {
                output = buffer + 8U;
                *output++ = OPEN_CFW_ATTS_READ_TYPE_RESPONSE;
                attribute_length = (uint8_t)*attribute->length;
                if (attribute_length > (uint8_t)(mtu-4U)) {
                    attribute_length = (uint8_t)(mtu-4U);
                }
                *output++ = (uint8_t)(attribute_length+2U);
                open_cfw_cordio_atts_read_put_u16(&output, handle);
                open_cfw_cordio_atts_read_copy(output, attribute->value, attribute_length);
                output += attribute_length;
                handle++;
                while ((handle = open_cfw_cordio_atts_find_uuid_in_range(
                        handle, end_handle, uuid_length, uuid,
                        &attribute, &group)) != 0U) {
                    callback_error = 0U;
                    if (((attribute->settings & OPEN_CFW_ATTS_READ_SET_CALLBACK) != 0U)
                        && (group->read_callback != NULL)) {
                        callback_error = ((open_cfw_cordio_atts_read_callback_t)
                            group->read_callback)(connection->main->connection_id,
                            handle, OPEN_CFW_ATTS_READ_TYPE_REQUEST, 0U, attribute);
                    } else if (((attribute->settings & OPEN_CFW_ATTS_READ_SET_CCC) != 0U)
                        && (OPEN_CFW_ATTS_READ_CCC_CALLBACK != NULL)) {
                        callback_error = OPEN_CFW_ATTS_READ_CCC_CALLBACK(
                            connection->main->connection_id,
                            OPEN_CFW_ATTS_READ_METHOD, handle, attribute->value
                        );
                    }
                    if ((callback_error == 0U)
                        && (*attribute->length == attribute_length)
                        && (open_cfw_cordio_atts_permissions(
                            connection->main->connection_id,
                            OPEN_CFW_ATTS_READ_PERMIT, handle,
                            attribute->permissions) == 0U)) {
                        if (output <= buffer + 8U + mtu
                                - attribute_length - 2U) {
                            open_cfw_cordio_atts_read_put_u16(&output, handle);
                            open_cfw_cordio_atts_read_copy(
                                output, attribute->value, attribute_length
                            );
                            output += attribute_length;
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                    if ((handle == OPEN_CFW_ATTS_READ_HANDLE_MAX)
                        || (++handle > end_handle)) {
                        break;
                    }
                }
            }
        }
    }
    if (error == 0U) {
        open_cfw_cordio_att_l2c_data_request(
            connection->main, connection->slot,
            (uint16_t)(output-(buffer+8U)), buffer
        );
    } else {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_READ_TYPE_REQUEST, start_handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_MULTIPLE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_read_multiple_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    uint8_t *buffer = NULL, *output, *end = packet + 8U + length;
    uint16_t handle = 0U, read_length;
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    uint8_t error = 0U;
    packet += 9U;
    buffer = open_cfw_cordio_att_message_allocate((uint16_t)(mtu+8U));
    if (buffer == NULL) {
        error = OPEN_CFW_ATTS_READ_ERR_RESOURCES;
        output = NULL;
    } else {
        output = buffer + 8U;
        *output++ = OPEN_CFW_ATTS_READ_MULTIPLE_RESPONSE;
        while (packet < end) {
            handle = open_cfw_cordio_atts_read_u16(packet);
            packet += 2U;
            attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
            if (attribute == NULL) {
                error = OPEN_CFW_ATTS_READ_ERR_HANDLE;
                break;
            }
            error = open_cfw_cordio_atts_read_attribute(
                connection, group, attribute, handle,
                OPEN_CFW_ATTS_READ_MULTIPLE_REQUEST, 0U
            );
            if (error != 0U) {
                break;
            }
            if (output < buffer + 8U + mtu) {
                read_length = (uint16_t)((buffer+8U+mtu)-output);
                if (read_length > *attribute->length) {
                    read_length = *attribute->length;
                }
                open_cfw_cordio_atts_read_copy(
                    output, attribute->value, read_length
                );
                output += read_length;
            }
        }
    }
    if (error == 0U) {
        open_cfw_cordio_att_l2c_data_request(
            connection->main, connection->slot,
            (uint16_t)(output-(buffer+8U)), buffer
        );
    } else {
        if (buffer != NULL) {
            open_cfw_cordio_wsf_message_free(buffer);
        }
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_READ_MULTIPLE_REQUEST, handle, error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_READ_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_READ_GROUP_TYPE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_read_group_type_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
)
{
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_group *group;
    uint8_t primary[2] = {
        (uint8_t)OPEN_CFW_ATTS_READ_PRIMARY_SERVICE_UUID,
        (uint8_t)(OPEN_CFW_ATTS_READ_PRIMARY_SERVICE_UUID >> 8)
    };
    uint8_t *buffer = NULL, *output = NULL, *uuid = packet + 13U;
    uint16_t start_handle = open_cfw_cordio_atts_read_u16(packet + 9U);
    uint16_t end_handle = open_cfw_cordio_atts_read_u16(packet + 11U);
    uint16_t handle;
    uint16_t mtu = connection->main->bearer[connection->slot].mtu;
    uint8_t uuid_length = (uint8_t)(length-OPEN_CFW_ATTS_READ_GROUP_TYPE_FIXED_LENGTH);
    uint8_t attribute_length, error = 0U;
    if ((uuid_length != 2U) && (uuid_length != 16U)) {
        error = OPEN_CFW_ATTS_READ_ERR_INVALID_PDU;
    } else if ((start_handle == 0U) || (start_handle > end_handle)) {
        error = OPEN_CFW_ATTS_READ_ERR_HANDLE;
    } else if (!open_cfw_cordio_atts_uuid16_compare(
            primary, uuid_length, uuid)) {
        error = OPEN_CFW_ATTS_READ_ERR_GROUP_TYPE;
    } else {
        handle = open_cfw_cordio_atts_find_uuid_in_range(
            start_handle, end_handle, uuid_length, uuid, &attribute, &group
        );
        if (handle == 0U) {
            error = OPEN_CFW_ATTS_READ_ERR_NOT_FOUND;
        } else if ((error = open_cfw_cordio_atts_permissions(
                connection->main->connection_id, OPEN_CFW_ATTS_READ_PERMIT,
                handle, attribute->permissions)) != 0U) {
            start_handle = handle;
        } else {
            buffer = open_cfw_cordio_att_message_allocate((uint16_t)(mtu+8U));
            if (buffer == NULL) {
                error = OPEN_CFW_ATTS_READ_ERR_RESOURCES;
            } else {
                output = buffer + 8U;
                *output++ = OPEN_CFW_ATTS_READ_GROUP_TYPE_RESPONSE;
                attribute_length = (uint8_t)*attribute->length;
                if (attribute_length > (uint8_t)(mtu-6U)) {
                    attribute_length = (uint8_t)(mtu-6U);
                }
                *output++ = (uint8_t)(attribute_length+4U);
                open_cfw_cordio_atts_read_put_u16(&output, handle);
                handle = open_cfw_cordio_atts_find_service_group_end(handle);
                open_cfw_cordio_atts_read_put_u16(&output, handle);
                open_cfw_cordio_atts_read_copy(output, attribute->value, attribute_length);
                output += attribute_length;
                for (;;) {
                    if ((handle == OPEN_CFW_ATTS_READ_HANDLE_MAX)
                        || (++handle > end_handle)) {
                        break;
                    }
                    handle = open_cfw_cordio_atts_find_uuid_in_range(
                        handle, end_handle, uuid_length, uuid,
                        &attribute, &group
                    );
                    if (handle == 0U) {
                        break;
                    }
                    if ((*attribute->length == attribute_length)
                        && (open_cfw_cordio_atts_permissions(
                            connection->main->connection_id,
                            OPEN_CFW_ATTS_READ_PERMIT, handle,
                            attribute->permissions) == 0U)) {
                        if (output <= buffer + 8U + mtu
                                - attribute_length - 4U) {
                            open_cfw_cordio_atts_read_put_u16(&output, handle);
                            handle = open_cfw_cordio_atts_find_service_group_end(handle);
                            open_cfw_cordio_atts_read_put_u16(&output, handle);
                            open_cfw_cordio_atts_read_copy(
                                output, attribute->value, attribute_length
                            );
                            output += attribute_length;
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                }
            }
        }
    }
    open_cfw_cordio_atts_discovery_busy(connection);
    if (error == 0U) {
        open_cfw_cordio_att_l2c_data_request(
            connection->main, connection->slot,
            (uint16_t)(output-(buffer+8U)), buffer
        );
    } else {
        open_cfw_cordio_atts_error_response(
            connection->main, connection->slot,
            OPEN_CFW_ATTS_READ_GROUP_TYPE_REQUEST, start_handle, error
        );
    }
}
#endif
