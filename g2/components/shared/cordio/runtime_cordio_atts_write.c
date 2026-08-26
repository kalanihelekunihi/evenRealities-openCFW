/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 Cordio ATT server write processors.  Business
 * behavior follows Packetcraft r20.05--r20.05c and preserves the recovered
 * G2 fixed-SRAM ABI and per-bearer pending-response semantics.
 */

#include "runtime_cordio_atts_write.h"

#if !defined(OPEN_CFW_ATTS_WRITE_EXECUTE_ONLY) && \
    !defined(OPEN_CFW_ATTS_WRITE_PROCESS_ONLY) && \
    !defined(OPEN_CFW_ATTS_WRITE_PREPARE_ONLY) && \
    !defined(OPEN_CFW_ATTS_WRITE_EXECUTE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTS_WRITE_CONTINUE_ONLY)
#define OPEN_CFW_ATTS_WRITE_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_WRITE_PRODUCTION
#define OPEN_CFW_ATTS_WRITE_QUEUE_BASE \
    ((struct open_cfw_cordio_wsf_queue_candidate *)0x2006E828U)
#define OPEN_CFW_ATTS_WRITE_CONFIGURATION \
    (*(struct open_cfw_cordio_att_configuration **)0x200004B4U)
#define OPEN_CFW_ATTS_WRITE_CCC_CALLBACK \
    (*(open_cfw_cordio_atts_ccc_write_callback_t *)0x2006E85CU)
#else
#define OPEN_CFW_ATTS_WRITE_QUEUE_BASE \
    open_cfw_cordio_atts_prepared_write_queues
#define OPEN_CFW_ATTS_WRITE_CONFIGURATION \
    open_cfw_cordio_att_configuration
#define OPEN_CFW_ATTS_WRITE_CCC_CALLBACK \
    open_cfw_cordio_atts_write_ccc_callback
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_atts_read_u16(
    const uint8_t *value
)
{
    return (uint16_t)value[0] | ((uint16_t)value[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_atts_copy(
    uint8_t *destination,
    const uint8_t *source,
    uint16_t length
)
{
    while (length != 0U) {
        *destination++ = *source++;
        length--;
    }
}

#if defined(OPEN_CFW_ATTS_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_WRITE_EXECUTE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_execute_prepared_write(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    struct open_cfw_cordio_atts_prepared_write *prepared
)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute =
        open_cfw_cordio_atts_find_by_handle(prepared->handle, &group);

    if (attribute == NULL) {
        return OPEN_CFW_ATTS_WRITE_ERR_UNLIKELY;
    }
    if ((attribute->permissions & OPEN_CFW_ATTS_WRITE_PERMIT_WRITE) == 0U) {
        return OPEN_CFW_ATTS_WRITE_ERR_WRITE;
    }
    if (((attribute->settings & OPEN_CFW_ATTS_WRITE_SET_WRITE_CALLBACK) != 0U)
        && (group->write_callback != NULL)) {
        return group->write_callback(
            connection->connection_id,
            prepared->handle,
            OPEN_CFW_ATTS_EXECUTE_WRITE_REQUEST,
            prepared->offset,
            prepared->write_length,
            prepared->packet,
            attribute
        );
    }
    if (((attribute->settings & OPEN_CFW_ATTS_WRITE_SET_CCC) != 0U)
        && (OPEN_CFW_ATTS_WRITE_CCC_CALLBACK != NULL)) {
        return OPEN_CFW_ATTS_WRITE_CCC_CALLBACK(
            connection->connection_id,
            OPEN_CFW_ATTS_WRITE_METHOD_WRITE,
            prepared->handle,
            prepared->packet
        );
    }
    open_cfw_cordio_atts_copy(
        attribute->value + prepared->offset,
        prepared->packet,
        prepared->write_length
    );
    if ((attribute->settings & OPEN_CFW_ATTS_WRITE_SET_VARIABLE_LENGTH) != 0U) {
        *attribute->length = prepared->write_length + prepared->offset;
    }
    return OPEN_CFW_ATTS_WRITE_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTS_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_WRITE_PROCESS_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_write(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    uint8_t *response;
    uint8_t opcode;
    uint8_t error = OPEN_CFW_ATTS_WRITE_SUCCESS;
    uint16_t handle;
    uint16_t write_length;

    packet += OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START;
    opcode = *packet++;
    handle = open_cfw_cordio_atts_read_u16(packet);
    packet += 2;
    write_length = length - 3U;
    attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
    if (attribute == NULL) {
        error = OPEN_CFW_ATTS_WRITE_ERR_HANDLE;
    } else if ((error = open_cfw_cordio_atts_permissions(
            connection->main->connection_id,
            OPEN_CFW_ATTS_WRITE_PERMIT_WRITE,
            handle,
            attribute->permissions
        )) != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        /* Permission provider selected the ATT error. */
    } else if (((attribute->settings
                & OPEN_CFW_ATTS_WRITE_SET_VARIABLE_LENGTH) == 0U)
            && (write_length != attribute->maximum_length)) {
        error = OPEN_CFW_ATTS_WRITE_ERR_LENGTH;
    } else if (((attribute->settings
                & OPEN_CFW_ATTS_WRITE_SET_VARIABLE_LENGTH) != 0U)
            && (write_length > attribute->maximum_length)) {
        error = OPEN_CFW_ATTS_WRITE_ERR_LENGTH;
    } else {
        if (((attribute->settings
                & OPEN_CFW_ATTS_WRITE_SET_WRITE_CALLBACK) != 0U)
            && (group->write_callback != NULL)) {
            error = group->write_callback(
                connection->main->connection_id,
                handle,
                opcode,
                0U,
                write_length,
                packet,
                attribute
            );
        } else if (((attribute->settings & OPEN_CFW_ATTS_WRITE_SET_CCC) != 0U)
            && (OPEN_CFW_ATTS_WRITE_CCC_CALLBACK != NULL)) {
            error = OPEN_CFW_ATTS_WRITE_CCC_CALLBACK(
                connection->main->connection_id,
                OPEN_CFW_ATTS_WRITE_METHOD_WRITE,
                handle,
                packet
            );
        } else {
            open_cfw_cordio_atts_copy(
                attribute->value, packet, write_length
            );
            if ((attribute->settings
                    & OPEN_CFW_ATTS_WRITE_SET_VARIABLE_LENGTH) != 0U) {
                *attribute->length = write_length;
            }
        }
        if ((error == OPEN_CFW_ATTS_WRITE_SUCCESS)
            && (opcode == OPEN_CFW_ATTS_WRITE_REQUEST)) {
            response = open_cfw_cordio_att_message_allocate(9U);
            if (response != NULL) {
                response[OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START] =
                    OPEN_CFW_ATTS_WRITE_RESPONSE;
                open_cfw_cordio_att_l2c_data_request(
                    connection->main, connection->slot, 1U, response
                );
            }
        }
    }
    if ((error != OPEN_CFW_ATTS_WRITE_SUCCESS)
        && (opcode == OPEN_CFW_ATTS_WRITE_REQUEST)) {
        if (error == OPEN_CFW_ATTS_WRITE_RESPONSE_PENDING) {
            connection->main->bearer[connection->slot].control |=
                OPEN_CFW_ATTS_WRITE_CCB_RESPONSE_PENDING;
        } else {
            open_cfw_cordio_atts_error_response(
                connection->main,
                connection->slot,
                OPEN_CFW_ATTS_WRITE_REQUEST,
                handle,
                error
            );
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_WRITE_PREPARE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_prepare_write_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    struct open_cfw_cordio_atts_prepared_write *prepared = NULL;
    struct open_cfw_cordio_wsf_queue_candidate *queue =
        &OPEN_CFW_ATTS_WRITE_QUEUE_BASE[connection->connection_id];
    uint8_t *response;
    uint8_t error = OPEN_CFW_ATTS_WRITE_SUCCESS;
    uint16_t handle;
    uint16_t offset;
    uint16_t write_length;

    packet += OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START + 1U;
    handle = open_cfw_cordio_atts_read_u16(packet);
    packet += 2;
    offset = open_cfw_cordio_atts_read_u16(packet);
    packet += 2;
    write_length = length - 5U;
    attribute = open_cfw_cordio_atts_find_by_handle(handle, &group);
    if (attribute == NULL) {
        error = OPEN_CFW_ATTS_WRITE_ERR_HANDLE;
    } else if ((error = open_cfw_cordio_atts_permissions(
            connection->connection_id,
            OPEN_CFW_ATTS_WRITE_PERMIT_WRITE,
            handle,
            attribute->permissions
        )) != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        /* Permission provider selected the ATT error. */
    } else if ((offset != 0U)
        && ((attribute->settings
            & OPEN_CFW_ATTS_WRITE_SET_ALLOW_OFFSET) == 0U)) {
        error = OPEN_CFW_ATTS_WRITE_ERR_NOT_LONG;
    } else if (((attribute->settings
                & OPEN_CFW_ATTS_WRITE_SET_VARIABLE_LENGTH) == 0U)
            && (write_length != attribute->maximum_length)) {
        error = OPEN_CFW_ATTS_WRITE_ERR_LENGTH;
    } else if (open_cfw_cordio_wsf_queue_count_candidate(queue)
        >= OPEN_CFW_ATTS_WRITE_CONFIGURATION->prepared_write_limit) {
        error = OPEN_CFW_ATTS_WRITE_ERR_QUEUE_FULL;
    } else if ((prepared = open_cfw_cordio_wsf_buffer_allocate_candidate(
            (uint16_t)(sizeof(*prepared) - 1U + write_length)
        )) == NULL) {
        error = OPEN_CFW_ATTS_WRITE_ERR_RESOURCES;
    } else if (((attribute->settings
            & OPEN_CFW_ATTS_WRITE_SET_WRITE_CALLBACK) != 0U)
        && (group->write_callback != NULL)) {
        error = group->write_callback(
            connection->connection_id,
            handle,
            OPEN_CFW_ATTS_PREPARE_WRITE_REQUEST,
            0U,
            write_length,
            packet,
            attribute
        );
    }

    if (error == OPEN_CFW_ATTS_WRITE_SUCCESS) {
        prepared->write_length = write_length;
        prepared->handle = handle;
        prepared->offset = offset;
        open_cfw_cordio_atts_copy(prepared->packet, packet, write_length);
        open_cfw_cordio_wsf_queue_enqueue_candidate(queue, prepared);
        response = open_cfw_cordio_att_message_allocate(
            (uint16_t)(13U + write_length)
        );
        if (response != NULL) {
            uint8_t *cursor = response + OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START;
            *cursor++ = OPEN_CFW_ATTS_PREPARE_WRITE_RESPONSE;
            *cursor++ = (uint8_t)handle;
            *cursor++ = (uint8_t)(handle >> 8);
            *cursor++ = (uint8_t)offset;
            *cursor++ = (uint8_t)(offset >> 8);
            open_cfw_cordio_atts_copy(cursor, packet, write_length);
            open_cfw_cordio_att_l2c_data_request(
                connection->main,
                connection->slot,
                (uint16_t)(5U + write_length),
                response
            );
        }
    }
    if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        open_cfw_cordio_atts_error_response(
            connection->main,
            connection->slot,
            OPEN_CFW_ATTS_PREPARE_WRITE_REQUEST,
            handle,
            error
        );
    }
}
#endif

#if defined(OPEN_CFW_ATTS_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_WRITE_EXECUTE_REQUEST_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_process_execute_write_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
)
{
    struct open_cfw_cordio_wsf_queue_candidate *queue =
        &OPEN_CFW_ATTS_WRITE_QUEUE_BASE[connection->connection_id];
    struct open_cfw_cordio_atts_prepared_write *prepared;
    struct open_cfw_cordio_atts_group *group;
    struct open_cfw_cordio_atts_attribute *attribute;
    uint8_t *response;
    uint8_t error = OPEN_CFW_ATTS_WRITE_SUCCESS;

    (void)length;
    packet += OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START + 1U;
    if (*packet == OPEN_CFW_ATTS_EXECUTE_WRITE_CANCEL) {
        open_cfw_cordio_atts_clear_prepared_writes(connection);
    } else if (*packet == OPEN_CFW_ATTS_EXECUTE_WRITE_ALL) {
        for (prepared = queue->head; prepared != NULL;
            prepared = prepared->next) {
            attribute = open_cfw_cordio_atts_find_by_handle(
                prepared->handle, &group
            );
            if (attribute != NULL) {
                if (prepared->offset > attribute->maximum_length) {
                    error = OPEN_CFW_ATTS_WRITE_ERR_OFFSET;
                } else if ((uint32_t)prepared->write_length
                    + prepared->offset > attribute->maximum_length) {
                    error = OPEN_CFW_ATTS_WRITE_ERR_LENGTH;
                }
                if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
                    open_cfw_cordio_atts_clear_prepared_writes(connection);
                    break;
                }
            }
        }
        if (error == OPEN_CFW_ATTS_WRITE_SUCCESS) {
            while ((prepared = open_cfw_cordio_wsf_queue_dequeue_candidate(
                    queue)) != NULL) {
                error = open_cfw_cordio_atts_execute_prepared_write(
                    connection, prepared
                );
                if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
                    open_cfw_cordio_atts_clear_prepared_writes(connection);
                }
                open_cfw_cordio_wsf_buffer_free_candidate(prepared);
            }
        }
    } else {
        error = OPEN_CFW_ATTS_WRITE_ERR_INVALID_PDU;
    }

    if (error != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        open_cfw_cordio_atts_error_response(
            connection->main,
            connection->slot,
            OPEN_CFW_ATTS_EXECUTE_WRITE_REQUEST,
            0U,
            error
        );
    } else {
        response = open_cfw_cordio_att_message_allocate(9U);
        if (response != NULL) {
            response[OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START] =
                OPEN_CFW_ATTS_EXECUTE_WRITE_RESPONSE;
            open_cfw_cordio_att_l2c_data_request(
                connection->main, connection->slot, 1U, response
            );
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_WRITE_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_WRITE_CONTINUE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_continue_write_request(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t status
)
{
    struct open_cfw_cordio_att_main_control_block *main =
        open_cfw_cordio_att_control_block_by_connection_id(connection_id);
    uint8_t *response;

    if (main == NULL) {
        return;
    }
    main->bearer[0].control &=
        (uint8_t)~OPEN_CFW_ATTS_WRITE_CCB_RESPONSE_PENDING;
    if (status != OPEN_CFW_ATTS_WRITE_SUCCESS) {
        open_cfw_cordio_atts_error_response(
            main, 0U, OPEN_CFW_ATTS_WRITE_REQUEST, handle, status
        );
    } else {
        response = open_cfw_cordio_att_message_allocate(9U);
        if (response != NULL) {
            response[OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START] =
                OPEN_CFW_ATTS_WRITE_RESPONSE;
            open_cfw_cordio_att_l2c_data_request(main, 0U, 1U, response);
        }
    }
}
#endif
