/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTC_WRITE_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTC_WRITE_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_ATTC_WRITE_L2C_PAYLOAD_START = 8U,
    OPEN_CFW_ATTC_WRITE_COMMAND_BUFFER_LENGTH = 11U,
    OPEN_CFW_ATTC_PREPARE_REQUEST_BUFFER_LENGTH = 13U,
    OPEN_CFW_ATTC_EXECUTE_REQUEST_BUFFER_LENGTH = 10U,
    OPEN_CFW_ATTC_WRITE_COMMAND_LENGTH = 3U,
    OPEN_CFW_ATTC_EXECUTE_REQUEST_LENGTH = 2U,
    OPEN_CFW_ATTC_PREPARE_RESPONSE_VALUE_PREFIX = 4U,
    OPEN_CFW_ATTC_PDU_WRITE_COMMAND = 0x52U,
    OPEN_CFW_ATTC_PDU_PREPARE_WRITE_REQUEST = 0x16U,
    OPEN_CFW_ATTC_PDU_EXECUTE_WRITE_REQUEST = 0x18U,
    OPEN_CFW_ATTC_MESSAGE_WRITE_COMMAND = 10U,
    OPEN_CFW_ATTC_MESSAGE_PREPARE_WRITE = 11U,
    OPEN_CFW_ATTC_MESSAGE_EXECUTE_WRITE = 12U,
    OPEN_CFW_ATTC_CONTINUING = 1U,
    OPEN_CFW_ATTC_NOT_CONTINUING = 0U
};

struct open_cfw_cordio_wsf_message_header {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

union open_cfw_cordio_attc_packet_parameter;

struct open_cfw_cordio_attc_api_message {
    struct open_cfw_cordio_wsf_message_header header;
    union open_cfw_cordio_attc_packet_parameter *packet;
    uint16_t handle;
    uint8_t slot;
};

struct open_cfw_cordio_attc_prepare_parameter {
    uint16_t length;
    uint16_t offset;
    uint8_t *value;
};

union open_cfw_cordio_attc_packet_parameter {
    uint16_t length;
    struct {
        uint16_t length;
        uint16_t offset;
    } offset;
    struct {
        uint16_t length;
        uint16_t start_handle;
        uint16_t end_handle;
    } handles;
    struct open_cfw_cordio_attc_prepare_parameter *prepare;
};

union open_cfw_cordio_attc_out_parameter {
    uint16_t length;
    struct {
        uint16_t length;
        uint16_t offset;
    } offset;
    struct {
        uint16_t length;
        uint16_t start_handle;
        uint16_t end_handle;
    } handles;
    struct open_cfw_cordio_attc_prepare_parameter prepare;
};

struct open_cfw_cordio_attc_connection_control_block {
    void *main;
    struct open_cfw_cordio_attc_api_message outstanding_request;
    union open_cfw_cordio_attc_out_parameter outstanding_parameters;
    uint8_t outstanding_timer[16];
    uint8_t slot;
    uint8_t connection_id;
    uint16_t pending_write_handles[1];
};

struct open_cfw_cordio_att_event {
    struct open_cfw_cordio_wsf_message_header header;
    uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
    uint16_t mtu;
};

void *open_cfw_cordio_att_message_allocate(uint16_t length);
void open_cfw_cordio_attc_send_message(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t message_id,
    union open_cfw_cordio_attc_packet_parameter *packet,
    uint8_t continuing
);

union open_cfw_cordio_attc_packet_parameter *
open_cfw_cordio_attc_prepare_write_allocate_message(uint16_t buffer_length);
void open_cfw_cordio_attc_process_prepare_write_response(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet,
    struct open_cfw_cordio_att_event *event
);
void open_cfw_cordio_attc_write_command(
    uint8_t connection_id,
    uint16_t handle,
    uint16_t value_length,
    uint8_t *value
);
void open_cfw_cordio_attc_prepare_write_request(
    uint8_t connection_id,
    uint16_t handle,
    uint16_t offset,
    uint16_t value_length,
    uint8_t *value,
    uint8_t value_by_reference,
    uint8_t continuing
);
void open_cfw_cordio_attc_execute_write_request(
    uint8_t connection_id,
    uint8_t write_all
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(union open_cfw_cordio_attc_packet_parameter) == 8U,
    "G2 ATTC packet-parameter ABI");
_Static_assert(sizeof(struct open_cfw_cordio_attc_prepare_parameter) == 8U,
    "G2 ATTC prepare-parameter ABI");
_Static_assert(sizeof(struct open_cfw_cordio_attc_api_message) == 12U,
    "G2 ATTC API-message ABI");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    outstanding_request.header.status) == 7U,
    "G2 ATTC outstanding-status offset");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    outstanding_parameters.prepare.length) == 16U,
    "G2 ATTC outstanding prepare-length offset");
_Static_assert(sizeof(struct open_cfw_cordio_attc_connection_control_block)
    == 44U, "G2 ATTC connection-control-block ABI");
_Static_assert(offsetof(struct open_cfw_cordio_att_event, value) == 4U,
    "G2 ATT event value offset");
_Static_assert(offsetof(struct open_cfw_cordio_att_event, value_length) == 8U,
    "G2 ATT event value-length offset");
#endif

#endif
