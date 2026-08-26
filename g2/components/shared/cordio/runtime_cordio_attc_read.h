/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTC_READ_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTC_READ_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_attc_write.h"

enum {
    OPEN_CFW_ATTC_READ_FIND_TYPE_BUFFER_LENGTH = 15U,
    OPEN_CFW_ATTC_READ_TYPE_BUFFER_LENGTH = 13U,
    OPEN_CFW_ATTC_READ_BLOB_BUFFER_LENGTH = 13U,
    OPEN_CFW_ATTC_READ_MULTIPLE_BUFFER_LENGTH = 9U,
    OPEN_CFW_ATTC_READ_GROUP_TYPE_BUFFER_LENGTH = 13U,
    OPEN_CFW_ATTC_READ_FIND_TYPE_LENGTH = 7U,
    OPEN_CFW_ATTC_READ_TYPE_LENGTH = 5U,
    OPEN_CFW_ATTC_READ_BLOB_LENGTH = 5U,
    OPEN_CFW_ATTC_READ_MULTIPLE_LENGTH = 1U,
    OPEN_CFW_ATTC_READ_GROUP_TYPE_LENGTH = 5U,
    OPEN_CFW_ATTC_READ_FIND_TYPE_REQUEST = 0x06U,
    OPEN_CFW_ATTC_READ_TYPE_REQUEST = 0x08U,
    OPEN_CFW_ATTC_READ_BLOB_REQUEST = 0x0CU,
    OPEN_CFW_ATTC_READ_MULTIPLE_REQUEST = 0x0EU,
    OPEN_CFW_ATTC_READ_GROUP_TYPE_REQUEST = 0x10U,
    OPEN_CFW_ATTC_READ_MESSAGE_FIND_TYPE = 3U,
    OPEN_CFW_ATTC_READ_MESSAGE_TYPE = 4U,
    OPEN_CFW_ATTC_READ_MESSAGE_LONG = 6U,
    OPEN_CFW_ATTC_READ_MESSAGE_MULTIPLE = 7U,
    OPEN_CFW_ATTC_READ_MESSAGE_GROUP_TYPE = 8U,
    OPEN_CFW_ATTC_READ_SUCCESS = 0U,
    OPEN_CFW_ATTC_READ_INVALID_RESPONSE = 0x13U,
    OPEN_CFW_ATTC_READ_HANDLE_MAX = 0xFFFFU
};

struct open_cfw_cordio_attc_bearer_control_block {
    uint16_t mtu;
    uint8_t control;
};

struct open_cfw_cordio_attc_main_control_block {
    struct open_cfw_cordio_attc_bearer_control_block bearer[3];
    uint16_t handle;
    uint8_t connection_id;
    void *pending_database_hash_response;
};

void open_cfw_cordio_attc_process_find_by_type_response(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet,
    struct open_cfw_cordio_att_event *event
);
void open_cfw_cordio_attc_process_read_long_response(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet,
    struct open_cfw_cordio_att_event *event
);
void open_cfw_cordio_attc_find_by_type_value_request(
    uint8_t connection_id,
    uint16_t start_handle,
    uint16_t end_handle,
    uint16_t uuid16,
    uint16_t value_length,
    uint8_t *value,
    uint8_t continuing
);
void open_cfw_cordio_attc_read_by_type_request(
    uint8_t connection_id,
    uint16_t start_handle,
    uint16_t end_handle,
    uint8_t uuid_length,
    uint8_t *uuid,
    uint8_t continuing
);
void open_cfw_cordio_attc_read_long_request(
    uint8_t connection_id,
    uint16_t handle,
    uint16_t offset,
    uint8_t continuing
);
void open_cfw_cordio_attc_read_multiple_request(
    uint8_t connection_id,
    uint8_t handle_count,
    uint16_t *handles
);
void open_cfw_cordio_attc_read_by_group_type_request(
    uint8_t connection_id,
    uint16_t start_handle,
    uint16_t end_handle,
    uint8_t uuid_length,
    uint8_t *uuid,
    uint8_t continuing
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_attc_bearer_control_block) == 4U,
    "G2 ATT bearer ABI");
_Static_assert(offsetof(struct open_cfw_cordio_attc_main_control_block,
    bearer[1]) == 4U, "G2 ATT bearer stride");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    outstanding_parameters.handles.start_handle) == 18U,
    "G2 ATTC outstanding start-handle offset");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    outstanding_parameters.handles.end_handle) == 20U,
    "G2 ATTC outstanding end-handle offset");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    slot) == 40U, "G2 ATTC bearer-slot offset");
#endif

#endif
