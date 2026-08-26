/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_l2c.h"

#if !defined(OPEN_CFW_L2C_SLAVE_TIMEOUT_ONLY) && \
    !defined(OPEN_CFW_L2C_SLAVE_RECEIVE_ONLY) && \
    !defined(OPEN_CFW_L2C_SLAVE_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_L2C_SLAVE_SIGNAL_REQUEST_ONLY) && \
    !defined(OPEN_CFW_L2C_SLAVE_UPDATE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_L2C_SLAVE_HANDLER_INIT_ONLY) && \
    !defined(OPEN_CFW_L2C_SLAVE_HANDLER_ONLY)
#define OPEN_CFW_L2C_SLAVE_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_L2C_PRODUCTION
#define OPEN_CFW_L2C_SLAVE_CONTROL \
    (*(struct open_cfw_cordio_l2c_control_block *)0x200737D8U)
#define OPEN_CFW_L2C_SLAVE_STATE \
    (*(struct open_cfw_cordio_l2c_slave_control_block *)0x20073BD8U)
#define OPEN_CFW_L2C_SLAVE_RECEIVE_CALLBACK \
    ((open_cfw_cordio_l2c_data_callback_t)(uintptr_t)0x00536C5DU)
#else
#define OPEN_CFW_L2C_SLAVE_CONTROL open_cfw_cordio_l2c_control_block
#define OPEN_CFW_L2C_SLAVE_STATE open_cfw_cordio_l2c_slave_control_block
#define OPEN_CFW_L2C_SLAVE_RECEIVE_CALLBACK \
    open_cfw_cordio_l2c_slave_receive_signaling_packet
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_l2c_slave_get_u16(
    const uint8_t *input
)
{
    return (uint16_t)input[0] | ((uint16_t)input[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_l2c_slave_put_u16(
    uint8_t *output, uint16_t value
)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8);
}

static __attribute__((unused)) void open_cfw_cordio_l2c_slave_copy(
    uint8_t *output, const uint8_t *input, uint16_t length
)
{
    while (length != 0U) {
        *output++ = *input++;
        length--;
    }
}

static __attribute__((unused)) uint8_t open_cfw_cordio_l2c_slave_next_id(
    uint8_t identifier
)
{
    return identifier == 0xFFU ? 1U : (uint8_t)(identifier + 1U);
}

static __attribute__((unused)) void open_cfw_cordio_l2c_slave_set_timer_param(
    uint16_t parameter
)
{
    OPEN_CFW_L2C_SLAVE_STATE.request_timer[8] = (uint8_t)parameter;
    OPEN_CFW_L2C_SLAVE_STATE.request_timer[9] = (uint8_t)(parameter >> 8);
}

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_TIMEOUT_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_slave_request_timeout(
    struct open_cfw_cordio_l2c_message_header *message
)
{
    uint8_t connection_id;
    if (message == NULL) {
        return;
    }
    connection_id = open_cfw_cordio_dm_connection_id_by_handle(
        message->parameter
    );
    if (connection_id != 0U && connection_id <= OPEN_CFW_L2C_CONNECTIONS) {
        OPEN_CFW_L2C_SLAVE_STATE.signaling_id[connection_id - 1U] =
            OPEN_CFW_L2C_SIGNAL_ID_INVALID;
    }
    open_cfw_cordio_dm_l2c_connection_update_confirmation(
        message->parameter, OPEN_CFW_L2C_CONNECTION_PARAMETERS_REJECTED
    );
}
#endif

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_RECEIVE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_slave_receive_signaling_packet(
    uint16_t handle, uint16_t l2c_length, uint8_t *packet
)
{
    uint8_t connection_id;
    uint8_t slot;
    uint8_t code;
    uint8_t identifier;
    uint8_t last_code;
    uint16_t parameter_length;
    uint16_t result;
    uint8_t *input;
    connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    if (connection_id == 0U || connection_id > OPEN_CFW_L2C_CONNECTIONS
            || packet == NULL
            || l2c_length < OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH) {
        return;
    }
    slot = (uint8_t)(connection_id - 1U);
    input = packet + OPEN_CFW_L2C_PAYLOAD_START;
    code = input[0];
    identifier = input[1];
    parameter_length = open_cfw_cordio_l2c_slave_get_u16(input + 2U);
    input += OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH;
    if (identifier == OPEN_CFW_L2C_SIGNAL_ID_INVALID) {
        return;
    }
    if (identifier == OPEN_CFW_L2C_SLAVE_STATE.signaling_id[slot]
            && l2c_length == (uint16_t)(parameter_length
                + OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH)
            && ((code == OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_RESPONSE
                    && parameter_length ==
                        OPEN_CFW_L2C_CONNECTION_UPDATE_RESPONSE_LENGTH)
                || (code == OPEN_CFW_L2C_SIGNAL_COMMAND_REJECT
                    && parameter_length >= OPEN_CFW_L2C_COMMAND_REJECT_LENGTH))) {
        last_code = OPEN_CFW_L2C_SLAVE_STATE.last_code[slot];
        OPEN_CFW_L2C_SLAVE_STATE.signaling_id[slot] =
            OPEN_CFW_L2C_SIGNAL_ID_INVALID;
        result = open_cfw_cordio_l2c_slave_get_u16(input);
        open_cfw_cordio_wsf_timer_stop_candidate(
            OPEN_CFW_L2C_SLAVE_STATE.request_timer
        );
        if (last_code == OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_REQUEST) {
            if (code == OPEN_CFW_L2C_SIGNAL_COMMAND_REJECT) {
                result = OPEN_CFW_L2C_CONNECTION_PARAMETERS_REJECTED;
            }
            open_cfw_cordio_dm_l2c_connection_update_confirmation(
                handle, result
            );
        } else {
            open_cfw_cordio_dm_l2c_command_reject_indication(handle, result);
        }
        return;
    }
    if (code != OPEN_CFW_L2C_SIGNAL_COMMAND_REJECT) {
        open_cfw_cordio_l2c_send_command_reject(
            handle, identifier, OPEN_CFW_L2C_REJECT_NOT_UNDERSTOOD
        );
    }
}
#endif

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_INITIALIZE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_slave_initialize(void)
{
    uint8_t index;
    OPEN_CFW_L2C_SLAVE_CONTROL.slave_signaling_callback =
        OPEN_CFW_L2C_SLAVE_RECEIVE_CALLBACK;
    for (index = 0U; index < OPEN_CFW_L2C_CONNECTIONS; index++) {
        OPEN_CFW_L2C_SLAVE_STATE.last_code[index] = 0U;
        OPEN_CFW_L2C_SLAVE_STATE.signaling_id[index] =
            OPEN_CFW_L2C_SIGNAL_ID_INVALID;
    }
}
#endif

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_SIGNAL_REQUEST_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_signaling_request(
    uint16_t handle, uint8_t code, uint16_t length, const uint8_t *parameters
)
{
    uint8_t connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    uint8_t slot;
    uint8_t identifier;
    uint8_t *packet;
    uint8_t *output;
    if (connection_id == 0U || connection_id > OPEN_CFW_L2C_CONNECTIONS
            || (length != 0U && parameters == NULL)
            || length > (uint16_t)(0xFFFFU - 12U)) {
        return;
    }
    packet = open_cfw_cordio_l2c_message_allocate((uint16_t)(12U + length));
    if (packet == NULL) {
        return;
    }
    slot = (uint8_t)(connection_id - 1U);
    identifier = OPEN_CFW_L2C_SLAVE_CONTROL.identifier;
    if (identifier == OPEN_CFW_L2C_SIGNAL_ID_INVALID) {
        identifier = 1U;
    }
    output = packet + OPEN_CFW_L2C_PAYLOAD_START;
    output[0] = code;
    output[1] = identifier;
    open_cfw_cordio_l2c_slave_put_u16(output + 2U, length);
    if (length != 0U) {
        open_cfw_cordio_l2c_slave_copy(output + 4U, parameters, length);
    }
    OPEN_CFW_L2C_SLAVE_STATE.last_code[slot] = code;
    OPEN_CFW_L2C_SLAVE_STATE.signaling_id[slot] = identifier;
    OPEN_CFW_L2C_SLAVE_CONTROL.identifier =
        open_cfw_cordio_l2c_slave_next_id(identifier);
    open_cfw_cordio_l2c_slave_set_timer_param(handle);
    open_cfw_cordio_wsf_timer_start_sec_candidate(
        OPEN_CFW_L2C_SLAVE_STATE.request_timer,
        OPEN_CFW_L2C_REQUEST_TIMEOUT_SECONDS
    );
    open_cfw_cordio_l2c_data_request(
        OPEN_CFW_L2C_CID_SIGNALING, handle,
        (uint16_t)(OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH + length), packet
    );
}
#endif

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_UPDATE_REQUEST_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_connection_update_request(
    uint16_t handle,
    const struct open_cfw_cordio_l2c_connection_specification *specification
)
{
    uint8_t connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    uint8_t slot;
    uint8_t identifier;
    uint8_t *packet;
    uint8_t *output;
    if (connection_id == 0U || connection_id > OPEN_CFW_L2C_CONNECTIONS
            || specification == NULL) {
        return;
    }
    packet = open_cfw_cordio_l2c_message_allocate(20U);
    if (packet == NULL) {
        return;
    }
    slot = (uint8_t)(connection_id - 1U);
    identifier = OPEN_CFW_L2C_SLAVE_CONTROL.identifier;
    if (identifier == OPEN_CFW_L2C_SIGNAL_ID_INVALID) {
        identifier = 1U;
    }
    output = packet + OPEN_CFW_L2C_PAYLOAD_START;
    output[0] = OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_REQUEST;
    output[1] = identifier;
    open_cfw_cordio_l2c_slave_put_u16(
        output + 2U, OPEN_CFW_L2C_CONNECTION_UPDATE_REQUEST_LENGTH
    );
    open_cfw_cordio_l2c_slave_put_u16(
        output + 4U, specification->interval_minimum
    );
    open_cfw_cordio_l2c_slave_put_u16(
        output + 6U, specification->interval_maximum
    );
    open_cfw_cordio_l2c_slave_put_u16(output + 8U, specification->latency);
    open_cfw_cordio_l2c_slave_put_u16(
        output + 10U, specification->supervision_timeout
    );
    OPEN_CFW_L2C_SLAVE_STATE.last_code[slot] =
        OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_REQUEST;
    OPEN_CFW_L2C_SLAVE_STATE.signaling_id[slot] = identifier;
    OPEN_CFW_L2C_SLAVE_CONTROL.identifier =
        open_cfw_cordio_l2c_slave_next_id(identifier);
    open_cfw_cordio_l2c_slave_set_timer_param(handle);
    open_cfw_cordio_wsf_timer_start_sec_candidate(
        OPEN_CFW_L2C_SLAVE_STATE.request_timer,
        OPEN_CFW_L2C_REQUEST_TIMEOUT_SECONDS
    );
    open_cfw_cordio_l2c_data_request(
        OPEN_CFW_L2C_CID_SIGNALING, handle, 12U, packet
    );
}
#endif

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_HANDLER_INIT_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_slave_handler_initialize(uint8_t handler_id)
{
    OPEN_CFW_L2C_SLAVE_STATE.request_timer[10] =
        OPEN_CFW_L2C_REQUEST_TIMEOUT_EVENT;
    OPEN_CFW_L2C_SLAVE_STATE.request_timer[12] = handler_id;
    OPEN_CFW_L2C_SLAVE_STATE.handler_id = handler_id;
}
#endif

#if defined(OPEN_CFW_L2C_SLAVE_BUILD_ALL) || defined(OPEN_CFW_L2C_SLAVE_HANDLER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_slave_handler(
    uint8_t event, struct open_cfw_cordio_l2c_message_header *message
)
{
    (void)event;
    if (message != NULL
            && message->event == OPEN_CFW_L2C_REQUEST_TIMEOUT_EVENT) {
        open_cfw_cordio_l2c_slave_request_timeout(message);
    }
}
#endif
