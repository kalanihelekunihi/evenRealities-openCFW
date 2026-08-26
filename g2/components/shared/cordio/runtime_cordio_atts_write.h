/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_WRITE_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_WRITE_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_wsf_queue_candidate.h"

enum {
    OPEN_CFW_ATTS_WRITE_L2C_PAYLOAD_START = 8U,
    OPEN_CFW_ATTS_WRITE_PERMIT_WRITE = 0x10U,
    OPEN_CFW_ATTS_WRITE_SET_WRITE_CALLBACK = 0x02U,
    OPEN_CFW_ATTS_WRITE_SET_VARIABLE_LENGTH = 0x08U,
    OPEN_CFW_ATTS_WRITE_SET_ALLOW_OFFSET = 0x10U,
    OPEN_CFW_ATTS_WRITE_SET_CCC = 0x20U,
    OPEN_CFW_ATTS_WRITE_METHOD_WRITE = 9U,
    OPEN_CFW_ATTS_WRITE_REQUEST = 0x12U,
    OPEN_CFW_ATTS_WRITE_RESPONSE = 0x13U,
    OPEN_CFW_ATTS_PREPARE_WRITE_REQUEST = 0x16U,
    OPEN_CFW_ATTS_PREPARE_WRITE_RESPONSE = 0x17U,
    OPEN_CFW_ATTS_EXECUTE_WRITE_REQUEST = 0x18U,
    OPEN_CFW_ATTS_EXECUTE_WRITE_RESPONSE = 0x19U,
    OPEN_CFW_ATTS_EXECUTE_WRITE_CANCEL = 0x00U,
    OPEN_CFW_ATTS_EXECUTE_WRITE_ALL = 0x01U,
    OPEN_CFW_ATTS_WRITE_SUCCESS = 0x00U,
    OPEN_CFW_ATTS_WRITE_ERR_HANDLE = 0x01U,
    OPEN_CFW_ATTS_WRITE_ERR_WRITE = 0x03U,
    OPEN_CFW_ATTS_WRITE_ERR_INVALID_PDU = 0x04U,
    OPEN_CFW_ATTS_WRITE_ERR_OFFSET = 0x07U,
    OPEN_CFW_ATTS_WRITE_ERR_QUEUE_FULL = 0x09U,
    OPEN_CFW_ATTS_WRITE_ERR_NOT_LONG = 0x0BU,
    OPEN_CFW_ATTS_WRITE_ERR_LENGTH = 0x0DU,
    OPEN_CFW_ATTS_WRITE_ERR_UNLIKELY = 0x0EU,
    OPEN_CFW_ATTS_WRITE_ERR_RESOURCES = 0x11U,
    OPEN_CFW_ATTS_WRITE_RESPONSE_PENDING = 0x7AU,
    OPEN_CFW_ATTS_WRITE_CCB_RESPONSE_PENDING = 0x08U
};

struct open_cfw_cordio_att_bearer_control_block {
    uint16_t mtu;
    uint8_t control;
    uint8_t reserved;
};

struct open_cfw_cordio_att_main_control_block {
    struct open_cfw_cordio_att_bearer_control_block bearer[3];
    uint16_t handle;
    uint8_t connection_id;
    uint8_t reserved;
    void *pending_database_hash_response;
};

struct open_cfw_cordio_atts_connection_control_block {
    uint8_t indication_timer[0x10];
    struct open_cfw_cordio_att_main_control_block *main;
    uint8_t idle_timer[0x10];
    uint8_t connection_id;
    uint8_t slot;
};

struct open_cfw_cordio_atts_attribute;

typedef uint8_t (*open_cfw_cordio_atts_write_callback_t)(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t opcode,
    uint16_t offset,
    uint16_t length,
    uint8_t *value,
    struct open_cfw_cordio_atts_attribute *attribute
);

typedef uint8_t (*open_cfw_cordio_atts_ccc_write_callback_t)(
    uint8_t connection_id,
    uint8_t method,
    uint16_t handle,
    uint8_t *value
);

struct open_cfw_cordio_atts_attribute {
    uint8_t *uuid;
    uint8_t *value;
    uint16_t *length;
    uint16_t maximum_length;
    uint8_t settings;
    uint8_t permissions;
};

struct open_cfw_cordio_atts_group {
    struct open_cfw_cordio_atts_group *next;
    struct open_cfw_cordio_atts_attribute *attributes;
    void *read_callback;
    open_cfw_cordio_atts_write_callback_t write_callback;
    uint16_t start_handle;
    uint16_t end_handle;
};

struct open_cfw_cordio_atts_prepared_write {
    struct open_cfw_cordio_atts_prepared_write *next;
    uint16_t write_length;
    uint16_t handle;
    uint16_t offset;
    uint8_t packet[1];
};

struct open_cfw_cordio_att_configuration {
    uint32_t discovery_idle_timeout;
    uint16_t mtu;
    uint8_t transaction_timeout;
    uint8_t prepared_write_limit;
};

#ifndef OPEN_CFW_ATTS_WRITE_PRODUCTION
extern struct open_cfw_cordio_wsf_queue_candidate
    open_cfw_cordio_atts_prepared_write_queues[4];
extern struct open_cfw_cordio_att_configuration
    *open_cfw_cordio_att_configuration;
extern open_cfw_cordio_atts_ccc_write_callback_t
    open_cfw_cordio_atts_write_ccc_callback;
#endif

struct open_cfw_cordio_atts_attribute *
open_cfw_cordio_atts_find_by_handle(
    uint16_t handle,
    struct open_cfw_cordio_atts_group **group
);
uint8_t open_cfw_cordio_atts_permissions(
    uint8_t connection_id,
    uint8_t permit,
    uint16_t handle,
    uint8_t permissions
);
void open_cfw_cordio_atts_error_response(
    struct open_cfw_cordio_att_main_control_block *main,
    uint8_t slot,
    uint8_t opcode,
    uint16_t handle,
    uint8_t reason
);
void open_cfw_cordio_atts_clear_prepared_writes(
    struct open_cfw_cordio_atts_connection_control_block *connection
);
void *open_cfw_cordio_att_message_allocate(uint16_t length);
void open_cfw_cordio_att_l2c_data_request(
    struct open_cfw_cordio_att_main_control_block *main,
    uint8_t slot,
    uint16_t length,
    uint8_t *packet
);
struct open_cfw_cordio_att_main_control_block *
open_cfw_cordio_att_control_block_by_connection_id(uint8_t connection_id);
void *open_cfw_cordio_wsf_buffer_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_buffer_free_candidate(void *buffer);

uint8_t open_cfw_cordio_atts_execute_prepared_write(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    struct open_cfw_cordio_atts_prepared_write *prepared
);
void open_cfw_cordio_atts_process_write(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
);
void open_cfw_cordio_atts_process_prepare_write_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
);
void open_cfw_cordio_atts_process_execute_write_request(
    struct open_cfw_cordio_atts_connection_control_block *connection,
    uint16_t length,
    uint8_t *packet
);
void open_cfw_cordio_atts_continue_write_request(
    uint8_t connection_id,
    uint16_t handle,
    uint8_t status
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_atts_attribute) == 16U,
    "G2 ATT attribute ABI");
_Static_assert(offsetof(struct open_cfw_cordio_atts_attribute, maximum_length)
    == 12U, "G2 ATT attribute maximum-length offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_attribute, settings) == 14U,
    "G2 ATT attribute settings offset");
_Static_assert(sizeof(struct open_cfw_cordio_atts_group) == 20U,
    "G2 ATT group ABI");
_Static_assert(offsetof(struct open_cfw_cordio_atts_group, write_callback) == 12U,
    "G2 ATT group write-callback offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_connection_control_block,
    main) == 0x10U, "G2 ATTS CCB main offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_connection_control_block,
    connection_id) == 0x24U, "G2 ATTS CCB connection-ID offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_connection_control_block,
    slot) == 0x25U, "G2 ATTS CCB slot offset");
_Static_assert(offsetof(struct open_cfw_cordio_att_main_control_block,
    connection_id) == 0x0EU, "G2 ATT main CCB connection-ID offset");
_Static_assert(sizeof(struct open_cfw_cordio_atts_prepared_write) == 12U,
    "G2 prepared-write allocation ABI");
_Static_assert(offsetof(struct open_cfw_cordio_atts_prepared_write, packet)
    == 10U, "G2 prepared-write packet offset");
_Static_assert(offsetof(struct open_cfw_cordio_att_configuration,
    prepared_write_limit) == 7U, "G2 ATT configuration limit offset");
#endif

#endif
