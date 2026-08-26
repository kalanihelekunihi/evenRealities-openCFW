/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_l2c.h"

#if !defined(OPEN_CFW_L2C_MASTER_RECEIVE_ONLY) && \
    !defined(OPEN_CFW_L2C_MASTER_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_L2C_MASTER_RESPONSE_ONLY)
#define OPEN_CFW_L2C_MASTER_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_L2C_PRODUCTION
#define OPEN_CFW_L2C_MASTER_CONTROL \
    (*(struct open_cfw_cordio_l2c_control_block *)0x200737D8U)
#define OPEN_CFW_L2C_MASTER_RECEIVE_CALLBACK \
    ((open_cfw_cordio_l2c_data_callback_t)(uintptr_t)0x00536FBDU)
#else
#define OPEN_CFW_L2C_MASTER_CONTROL open_cfw_cordio_l2c_control_block
#define OPEN_CFW_L2C_MASTER_RECEIVE_CALLBACK \
    open_cfw_cordio_l2c_master_receive_signaling_packet
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_l2c_master_get_u16(
    const uint8_t *input
)
{
    return (uint16_t)input[0] | ((uint16_t)input[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_l2c_master_put_u16(
    uint8_t *output, uint16_t value
)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8);
}

#if defined(OPEN_CFW_L2C_MASTER_BUILD_ALL) || defined(OPEN_CFW_L2C_MASTER_RECEIVE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_master_receive_signaling_packet(
    uint16_t handle, uint16_t l2c_length, uint8_t *packet
)
{
    struct open_cfw_cordio_l2c_connection_specification specification;
    uint8_t *input;
    uint8_t code;
    uint8_t identifier;
    uint16_t parameter_length;
    if (packet == NULL || l2c_length < OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH) {
        return;
    }
    input = packet + OPEN_CFW_L2C_PAYLOAD_START;
    code = input[0];
    identifier = input[1];
    parameter_length = open_cfw_cordio_l2c_master_get_u16(input + 2U);
    input += OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH;
    if (l2c_length != (uint16_t)(parameter_length
            + OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH)
            || code != OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_REQUEST
            || parameter_length !=
                OPEN_CFW_L2C_CONNECTION_UPDATE_REQUEST_LENGTH) {
        if (code != OPEN_CFW_L2C_SIGNAL_COMMAND_REJECT) {
            open_cfw_cordio_l2c_send_command_reject(
                handle, identifier, OPEN_CFW_L2C_REJECT_NOT_UNDERSTOOD
            );
        }
        return;
    }
    specification.interval_minimum =
        open_cfw_cordio_l2c_master_get_u16(input);
    specification.interval_maximum =
        open_cfw_cordio_l2c_master_get_u16(input + 2U);
    specification.latency = open_cfw_cordio_l2c_master_get_u16(input + 4U);
    specification.supervision_timeout =
        open_cfw_cordio_l2c_master_get_u16(input + 6U);
    specification.minimum_connection_event_length = 0U;
    specification.maximum_connection_event_length = 0U;
    if (specification.interval_minimum < OPEN_CFW_L2C_HCI_INTERVAL_MIN
            || specification.interval_minimum >
                OPEN_CFW_L2C_HCI_INTERVAL_MAX
            || specification.interval_minimum > specification.interval_maximum
            || specification.interval_maximum < OPEN_CFW_L2C_HCI_INTERVAL_MIN
            || specification.interval_maximum >
                OPEN_CFW_L2C_HCI_INTERVAL_MAX
            || specification.latency > OPEN_CFW_L2C_HCI_LATENCY_MAX
            || specification.supervision_timeout <
                OPEN_CFW_L2C_HCI_SUPERVISION_TIMEOUT_MIN
            || specification.supervision_timeout >
                OPEN_CFW_L2C_HCI_SUPERVISION_TIMEOUT_MAX) {
        open_cfw_cordio_l2c_connection_update_response(
            identifier, handle, OPEN_CFW_L2C_CONNECTION_PARAMETERS_REJECTED
        );
        return;
    }
    open_cfw_cordio_dm_l2c_connection_update_indication(
        identifier, handle, &specification
    );
}
#endif

#if defined(OPEN_CFW_L2C_MASTER_BUILD_ALL) || defined(OPEN_CFW_L2C_MASTER_INITIALIZE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_master_initialize(void)
{
    OPEN_CFW_L2C_MASTER_CONTROL.master_signaling_callback =
        OPEN_CFW_L2C_MASTER_RECEIVE_CALLBACK;
}
#endif

#if defined(OPEN_CFW_L2C_MASTER_BUILD_ALL) || defined(OPEN_CFW_L2C_MASTER_RESPONSE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_connection_update_response(
    uint8_t identifier, uint16_t handle, uint16_t result
)
{
    uint8_t *packet = open_cfw_cordio_l2c_message_allocate(14U);
    if (packet != NULL) {
        uint8_t *output = packet + OPEN_CFW_L2C_PAYLOAD_START;
        output[0] = OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_RESPONSE;
        output[1] = identifier;
        open_cfw_cordio_l2c_master_put_u16(
            output + 2U, OPEN_CFW_L2C_CONNECTION_UPDATE_RESPONSE_LENGTH
        );
        open_cfw_cordio_l2c_master_put_u16(output + 4U, result);
        open_cfw_cordio_l2c_data_request(
            OPEN_CFW_L2C_CID_SIGNALING, handle, 6U, packet
        );
    }
}
#endif
