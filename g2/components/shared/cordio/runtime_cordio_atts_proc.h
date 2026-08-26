/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_PROC_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_PROC_H

#include "runtime_cordio_atts_write.h"

enum {
    OPEN_CFW_ATTS_PROC_UUID_16_LENGTH = 2U,
    OPEN_CFW_ATTS_PROC_UUID_128_LENGTH = 16U,
    OPEN_CFW_ATTS_PROC_SET_UUID_128 = 0x01U,
    OPEN_CFW_ATTS_PROC_SET_READ_CALLBACK = 0x04U,
    OPEN_CFW_ATTS_PROC_SET_CCC = 0x20U,
    OPEN_CFW_ATTS_PROC_PERMIT_READ = 0x01U,
    OPEN_CFW_ATTS_PROC_PERMIT_READ_ENCRYPTED = 0x02U,
    OPEN_CFW_ATTS_PROC_PERMIT_READ_AUTHENTICATED = 0x04U,
    OPEN_CFW_ATTS_PROC_PERMIT_READ_AUTHORIZED = 0x08U,
    OPEN_CFW_ATTS_PROC_SECURITY_NONE = 0U,
    OPEN_CFW_ATTS_PROC_SECURITY_ENCRYPTED_AUTHENTICATED = 2U,
    OPEN_CFW_ATTS_PROC_ERR_READ = 0x02U,
    OPEN_CFW_ATTS_PROC_ERR_NOT_SUPPORTED = 0x06U,
    OPEN_CFW_ATTS_PROC_ERR_AUTHORIZATION = 0x08U,
    OPEN_CFW_ATTS_PROC_ERR_NOT_FOUND = 0x0AU,
    OPEN_CFW_ATTS_PROC_ERR_RESOURCES = 0x11U,
    OPEN_CFW_ATTS_PROC_CSF_EATT_BEARER = 0x02U,
    OPEN_CFW_ATTS_PROC_HANDLE_NONE = 0U,
    OPEN_CFW_ATTS_PROC_HANDLE_MAX = 0xFFFFU,
    OPEN_CFW_ATTS_PROC_MTU_REQUEST = 0x02U,
    OPEN_CFW_ATTS_PROC_MTU_RESPONSE = 0x03U,
    OPEN_CFW_ATTS_PROC_FIND_INFO_REQUEST = 0x04U,
    OPEN_CFW_ATTS_PROC_FIND_INFO_RESPONSE = 0x05U,
    OPEN_CFW_ATTS_PROC_READ_REQUEST = 0x0AU,
    OPEN_CFW_ATTS_PROC_READ_RESPONSE = 0x0BU,
    OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_REQUEST = 0x20U,
    OPEN_CFW_ATTS_PROC_READ_MULTI_VAR_RESPONSE = 0x21U,
    OPEN_CFW_ATTS_PROC_METHOD_READ = 5U,
    OPEN_CFW_ATTS_PROC_FIND_HANDLE_16_UUID = 1U,
    OPEN_CFW_ATTS_PROC_FIND_HANDLE_128_UUID = 2U,
    OPEN_CFW_ATTS_PROC_G2_MINIMUM_MTU = 247U
};

typedef uint8_t (*open_cfw_cordio_atts_read_callback_t)(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t opcode,
    uint16_t offset,
    struct open_cfw_cordio_atts_attribute *attribute
);
typedef uint8_t (*open_cfw_cordio_atts_authorization_callback_t)(
    uint8_t connection_id,
    uint8_t permit,
    uint16_t handle
);

#ifndef OPEN_CFW_ATTS_PROC_PRODUCTION
extern struct open_cfw_cordio_wsf_queue_candidate
    open_cfw_cordio_atts_group_queue;
extern open_cfw_cordio_atts_authorization_callback_t
    open_cfw_cordio_atts_authorization_callback;
extern open_cfw_cordio_atts_ccc_write_callback_t
    open_cfw_cordio_atts_proc_ccc_callback;
#endif

uint8_t open_cfw_cordio_att_uuid_compare_16_to_128(
    const uint8_t *uuid16, const uint8_t *uuid128
);
uint8_t open_cfw_cordio_dm_connection_security_level(uint8_t connection_id);
void open_cfw_cordio_atts_csf_get_features(
    uint8_t connection_id, uint8_t *features, uint8_t length
);
uint16_t open_cfw_cordio_hci_get_maximum_receive_acl_length(void);
void open_cfw_cordio_att_set_mtu(
    struct open_cfw_cordio_att_main_control_block *main,
    uint8_t slot,
    uint16_t peer_mtu,
    uint16_t local_mtu
);
void open_cfw_cordio_atts_discovery_busy(
    struct open_cfw_cordio_atts_connection_control_block *connection
);
void open_cfw_cordio_wsf_message_free(void *message);
void open_cfw_cordio_att_message_free(void *message, uint8_t opcode);

uint8_t open_cfw_cordio_atts_uuid_compare(
    struct open_cfw_cordio_atts_attribute *attribute,
    uint8_t uuid_length,
    uint8_t *uuid
);
uint8_t open_cfw_cordio_atts_uuid16_compare(
    uint8_t *uuid16, uint8_t uuid_length, uint8_t *uuid
);
struct open_cfw_cordio_atts_attribute *open_cfw_cordio_atts_find_by_handle(
    uint16_t handle, struct open_cfw_cordio_atts_group **group
);
uint16_t open_cfw_cordio_atts_find_in_range(
    uint16_t start_handle,
    uint16_t end_handle,
    struct open_cfw_cordio_atts_attribute **attribute
);
uint8_t open_cfw_cordio_atts_permissions(
    uint8_t connection_id, uint8_t permit, uint16_t handle, uint8_t permissions
);
void open_cfw_cordio_atts_process_mtu_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_find_information_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_read_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_process_read_multiple_variable_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length, uint8_t *packet
);

#endif
