/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_MAIN_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_MAIN_H

#include "runtime_cordio_atts_csf.h"
#include "runtime_cordio_atts_ind.h"
#include "runtime_cordio_atts_read.h"

enum {
    OPEN_CFW_ATTS_MAIN_IDLE_TIMEOUT_EVENT = 0x20U,
    OPEN_CFW_ATTS_MAIN_API_EVENT = 0x21U,
    OPEN_CFW_ATTS_MAIN_IND_TIMEOUT_EVENT = 0x22U,
    OPEN_CFW_ATTS_MAIN_SIGN_COMPLETE_EVENT = 0x23U,
    OPEN_CFW_ATTS_MAIN_HASH_COMPLETE_EVENT = 0x24U,
    OPEN_CFW_ATTS_MAIN_DB_HASH_EVENT = 0x15U,
    OPEN_CFW_ATTS_MAIN_CONNECTION_CLOSE_EVENT = 0x28U,
    OPEN_CFW_ATTS_MAIN_IDLE_DISCOVERY = 0x0004U,
    OPEN_CFW_ATTS_MAIN_CONNECTION_IDLE = 0U,
    OPEN_CFW_ATTS_MAIN_CONNECTION_BUSY = 1U,
    OPEN_CFW_ATTS_MAIN_RESPONSE_PENDING = 0x08U,
    OPEN_CFW_ATTS_MAIN_ERROR_RESPONSE = 0x01U,
    OPEN_CFW_ATTS_MAIN_MTU_REQUEST = 0x02U,
    OPEN_CFW_ATTS_MAIN_WRITE_REQUEST = 0x12U,
    OPEN_CFW_ATTS_MAIN_PREPARE_WRITE_REQUEST = 0x16U,
    OPEN_CFW_ATTS_MAIN_VALUE_CONFIRMATION = 0x1EU,
    OPEN_CFW_ATTS_MAIN_READ_MULTIPLE_VARIABLE_REQUEST = 0x20U,
    OPEN_CFW_ATTS_MAIN_WRITE_COMMAND = 0x52U,
    OPEN_CFW_ATTS_MAIN_SIGNED_WRITE_COMMAND = 0xD2U,
    OPEN_CFW_ATTS_MAIN_COMMAND_MASK = 0x40U,
    OPEN_CFW_ATTS_MAIN_METHOD_WRITE_COMMAND = 10U,
    OPEN_CFW_ATTS_MAIN_METHOD_READ_MULTIPLE_VARIABLE = 16U,
    OPEN_CFW_ATTS_MAIN_METHOD_SIGNED_WRITE_COMMAND = 17U,
    OPEN_CFW_ATTS_MAIN_ERR_INVALID_PDU = 0x04U,
    OPEN_CFW_ATTS_MAIN_ERR_NOT_SUPPORTED = 0x06U,
    OPEN_CFW_ATTS_MAIN_ERR_LENGTH = 0x0DU,
    OPEN_CFW_ATTS_MAIN_ERR_NOT_FOUND = 0x0AU,
    OPEN_CFW_ATTS_MAIN_ERR_RESOURCES = 0x11U,
    OPEN_CFW_ATTS_MAIN_DATABASE_HASH_LENGTH = 16U,
    OPEN_CFW_ATTS_MAIN_SET_UUID_128 = 0x01U,
    OPEN_CFW_ATTS_MAIN_SET_VARIABLE_LENGTH = 0x08U
};

typedef void (*open_cfw_cordio_atts_processor_t)(
    struct open_cfw_cordio_atts_connection_control_block *, uint16_t, uint8_t *
);
typedef void (*open_cfw_cordio_atts_message_callback_t)(void *);

struct open_cfw_cordio_atts_interface {
    void (*data_callback)(uint16_t, uint16_t, uint8_t *);
    void (*control_callback)(struct open_cfw_cordio_wsf_message_header *);
    open_cfw_cordio_atts_message_callback_t message_callback;
    void (*connection_callback)(
        struct open_cfw_cordio_att_main_control_block *,
        struct open_cfw_cordio_dm_event *
    );
};

struct open_cfw_cordio_sec_cmac_message {
    struct open_cfw_cordio_wsf_message_header header;
    uint8_t *ciphertext;
    uint8_t *plaintext;
};

struct open_cfw_cordio_att_event {
    struct open_cfw_cordio_wsf_message_header header;
    uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
    uint8_t reserved;
    uint16_t mtu;
};

#ifndef OPEN_CFW_ATTS_MAIN_PRODUCTION
extern struct open_cfw_cordio_atts_ind_connection
    open_cfw_cordio_atts_main_connections[3][3];
extern struct open_cfw_cordio_wsf_queue_candidate
    open_cfw_cordio_atts_main_prepared_write_queues[4];
extern struct open_cfw_cordio_wsf_queue_candidate
    open_cfw_cordio_atts_main_group_queue;
extern struct open_cfw_cordio_atts_interface
    *open_cfw_cordio_atts_main_indication_interface;
extern open_cfw_cordio_atts_message_callback_t
    open_cfw_cordio_atts_main_sign_message_callback;
extern struct open_cfw_cordio_att_main_control_block
    open_cfw_cordio_atts_main_control_blocks[3];
extern struct open_cfw_cordio_atts_interface
    *open_cfw_cordio_atts_main_server_interface;
extern uint8_t open_cfw_cordio_atts_main_handler_id;
extern uint8_t open_cfw_cordio_atts_main_error_test;
extern uint8_t open_cfw_cordio_atts_main_hashable_next_value;
extern void (*open_cfw_cordio_atts_main_application_callback)(
    struct open_cfw_cordio_att_event *
);
extern open_cfw_cordio_atts_processor_t
    open_cfw_cordio_atts_main_processor_table[18];
extern uint8_t open_cfw_cordio_atts_main_minimum_pdu_length[18];
#endif

uint8_t open_cfw_cordio_dm_connection_in_use(uint8_t connection_id);
uint8_t open_cfw_cordio_dm_connection_id_by_handle(uint16_t handle);
uint16_t open_cfw_cordio_dm_connection_check_idle(uint8_t connection_id);
void open_cfw_cordio_dm_connection_set_idle(
    uint8_t connection_id, uint16_t mask, uint8_t idle
);
uint8_t open_cfw_cordio_security_cmac(
    uint8_t *key, uint8_t *message, uint16_t length,
    uint8_t handler_id, uint16_t parameter, uint8_t event
);

void open_cfw_cordio_atts_data_callback(
    uint16_t handle, uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_connection_callback(
    struct open_cfw_cordio_att_main_control_block *main,
    struct open_cfw_cordio_dm_event *event
);
void open_cfw_cordio_atts_message_callback(
    struct open_cfw_cordio_wsf_message_header *message
);
void open_cfw_cordio_atts_l2c_control_callback(
    struct open_cfw_cordio_wsf_message_header *message
);
void open_cfw_cordio_atts_error_response(
    struct open_cfw_cordio_att_main_control_block *main, uint8_t slot,
    uint8_t opcode, uint16_t handle, uint8_t reason
);
void open_cfw_cordio_atts_clear_prepared_writes(
    struct open_cfw_cordio_atts_connection_control_block *connection
);
void open_cfw_cordio_atts_discovery_busy(
    struct open_cfw_cordio_atts_connection_control_block *connection
);
void open_cfw_cordio_atts_process_database_hash_update(
    struct open_cfw_cordio_sec_cmac_message *message
);
void open_cfw_cordio_atts_check_pending_database_hash_read_response(void);
uint16_t open_cfw_cordio_atts_is_hashable_attribute(
    struct open_cfw_cordio_atts_attribute *attribute
);
struct open_cfw_cordio_atts_ind_connection *
open_cfw_cordio_atts_ind_connection_by_id(uint8_t connection_id, uint8_t slot);
struct open_cfw_cordio_atts_ind_connection *
open_cfw_cordio_atts_ind_connection_by_handle(uint16_t handle, uint8_t slot);
void open_cfw_cordio_atts_initialize(void);
uint8_t open_cfw_cordio_atts_hash_database_string(
    uint8_t *key, uint8_t *message, uint16_t length
);
void open_cfw_cordio_atts_calculate_database_hash(void);
void open_cfw_cordio_atts_add_group(struct open_cfw_cordio_atts_group *group);
void open_cfw_cordio_atts_remove_group(uint16_t start_handle);

void open_cfw_cordio_atts_authorization_register(
    open_cfw_cordio_atts_authorization_callback_t callback
);
uint8_t open_cfw_cordio_atts_set_attribute(
    uint16_t handle, uint16_t value_length, uint8_t *value
);
uint8_t open_cfw_cordio_atts_get_attribute(
    uint16_t handle, uint16_t *length, uint8_t **value
);
void open_cfw_cordio_atts_error_test(uint8_t status);

#endif
