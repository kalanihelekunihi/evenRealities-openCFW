/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_READ_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_READ_H

#include "runtime_cordio_atts_proc.h"

enum {
    OPEN_CFW_ATTS_READ_HANDLE_NONE = 0U,
    OPEN_CFW_ATTS_READ_HANDLE_MAX = 0xFFFFU,
    OPEN_CFW_ATTS_READ_UUID_16_LENGTH = 2U,
    OPEN_CFW_ATTS_READ_UUID_128_LENGTH = 16U,
    OPEN_CFW_ATTS_READ_PRIMARY_SERVICE_UUID = 0x2800U,
    OPEN_CFW_ATTS_READ_SECONDARY_SERVICE_UUID = 0x2801U,
    OPEN_CFW_ATTS_READ_PAYLOAD_START = 8U,
    OPEN_CFW_ATTS_READ_HEADER_LENGTH = 1U,
    OPEN_CFW_ATTS_READ_PERMIT = 0x01U,
    OPEN_CFW_ATTS_READ_SET_CALLBACK = 0x04U,
    OPEN_CFW_ATTS_READ_SET_CCC = 0x20U,
    OPEN_CFW_ATTS_READ_METHOD = 5U,
    OPEN_CFW_ATTS_READ_SUCCESS = 0U,
    OPEN_CFW_ATTS_READ_ERR_HANDLE = 0x01U,
    OPEN_CFW_ATTS_READ_ERR_INVALID_PDU = 0x04U,
    OPEN_CFW_ATTS_READ_ERR_OFFSET = 0x07U,
    OPEN_CFW_ATTS_READ_ERR_NOT_FOUND = 0x0AU,
    OPEN_CFW_ATTS_READ_ERR_GROUP_TYPE = 0x10U,
    OPEN_CFW_ATTS_READ_ERR_RESOURCES = 0x11U,
    OPEN_CFW_ATTS_READ_BLOB_REQUEST = 0x0CU,
    OPEN_CFW_ATTS_READ_BLOB_RESPONSE = 0x0DU,
    OPEN_CFW_ATTS_FIND_TYPE_REQUEST = 0x06U,
    OPEN_CFW_ATTS_FIND_TYPE_RESPONSE = 0x07U,
    OPEN_CFW_ATTS_READ_TYPE_REQUEST = 0x08U,
    OPEN_CFW_ATTS_READ_TYPE_RESPONSE = 0x09U,
    OPEN_CFW_ATTS_READ_MULTIPLE_REQUEST = 0x0EU,
    OPEN_CFW_ATTS_READ_MULTIPLE_RESPONSE = 0x0FU,
    OPEN_CFW_ATTS_READ_GROUP_TYPE_REQUEST = 0x10U,
    OPEN_CFW_ATTS_READ_GROUP_TYPE_RESPONSE = 0x11U,
    OPEN_CFW_ATTS_FIND_TYPE_FIXED_LENGTH = 7U,
    OPEN_CFW_ATTS_READ_TYPE_FIXED_LENGTH = 5U,
    OPEN_CFW_ATTS_READ_GROUP_TYPE_FIXED_LENGTH = 5U
};

struct open_cfw_cordio_atts_pending_database_hash_response {
    uint16_t start_handle;
    uint16_t handle;
};

#ifndef OPEN_CFW_ATTS_READ_PRODUCTION
extern uint8_t open_cfw_cordio_atts_primary_service_uuid[2];
extern uint8_t open_cfw_cordio_atts_secondary_service_uuid[2];
extern uint8_t open_cfw_cordio_atts_database_hash_uuid[2];
#endif

uint8_t open_cfw_cordio_atts_csf_get_hash_update_status(void);

uint16_t open_cfw_cordio_atts_find_uuid_in_range(
    uint16_t start_handle, uint16_t end_handle, uint8_t uuid_length,
    uint8_t *uuid, struct open_cfw_cordio_atts_attribute **attribute,
    struct open_cfw_cordio_atts_group **group
);
uint16_t open_cfw_cordio_atts_find_service_group_end(uint16_t start_handle);
void open_cfw_cordio_atts_process_read_blob_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_find_type_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_read_type_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_read_multiple_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_read_group_type_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);

#endif
