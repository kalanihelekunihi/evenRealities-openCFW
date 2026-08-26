/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTC_PROC_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTC_PROC_H

#include <stdint.h>

#include "runtime_cordio_attc_read.h"
#include "runtime_cordio_wsf_msg_candidate.h"

enum {
    OPEN_CFW_ATTC_PROC_METHOD_ERROR = 0U,
    OPEN_CFW_ATTC_PROC_METHOD_MTU = 1U,
    OPEN_CFW_ATTC_PROC_METHOD_FIND_INFO = 2U,
    OPEN_CFW_ATTC_PROC_METHOD_FIND_TYPE = 3U,
    OPEN_CFW_ATTC_PROC_METHOD_READ_TYPE = 4U,
    OPEN_CFW_ATTC_PROC_METHOD_READ = 5U,
    OPEN_CFW_ATTC_PROC_METHOD_READ_BLOB = 6U,
    OPEN_CFW_ATTC_PROC_METHOD_READ_MULTIPLE = 7U,
    OPEN_CFW_ATTC_PROC_METHOD_READ_GROUP = 8U,
    OPEN_CFW_ATTC_PROC_METHOD_WRITE = 9U,
    OPEN_CFW_ATTC_PROC_METHOD_PREPARE_WRITE = 11U,
    OPEN_CFW_ATTC_PROC_METHOD_VALUE_NOTIFICATION = 13U,
    OPEN_CFW_ATTC_PROC_METHOD_VALUE_INDICATION = 14U,
    OPEN_CFW_ATTC_PROC_METHOD_READ_MULTIPLE_VARIABLE = 16U,
    OPEN_CFW_ATTC_PROC_MAX_RESPONSE_METHOD = 16U,
    OPEN_CFW_ATTC_PROC_FIND_UUID16 = 1U,
    OPEN_CFW_ATTC_PROC_UUID16_LENGTH = 2U,
    OPEN_CFW_ATTC_PROC_UUID128_LENGTH = 16U,
    OPEN_CFW_ATTC_PROC_FLOW_DISABLED = 0x02U,
    OPEN_CFW_ATTC_PROC_TRANSACTION_TIMEOUT = 0x04U,
    OPEN_CFW_ATTC_PROC_CONFIRM_PENDING = 0x10U,
    OPEN_CFW_ATTC_PROC_DEFAULT_MTU = 23U,
    OPEN_CFW_ATTC_PROC_ERROR_TIMEOUT = 0x71U,
    OPEN_CFW_ATTC_PROC_ERROR_INVALID_RESPONSE = 0x73U,
    OPEN_CFW_ATTC_PROC_ERROR_UNDEFINED = 0x75U,
    OPEN_CFW_ATTC_PROC_ERROR_MTU_EXCEEDED = 0x77U,
    OPEN_CFW_ATTC_PROC_PDU_MTU_REQUEST = 0x02U,
    OPEN_CFW_ATTC_PROC_PDU_FIND_INFO_REQUEST = 0x04U,
    OPEN_CFW_ATTC_PROC_PDU_READ_REQUEST = 0x0AU,
    OPEN_CFW_ATTC_PROC_PDU_WRITE_REQUEST = 0x12U,
    OPEN_CFW_ATTC_PROC_PDU_VALUE_CONFIRMATION = 0x1EU,
    OPEN_CFW_ATTC_PROC_MESSAGE_NONE = 0U,
    OPEN_CFW_ATTC_PROC_MESSAGE_CANCEL = 19U,
    OPEN_CFW_ATTC_PROC_MTU_REQUEST_LENGTH = 3U,
    OPEN_CFW_ATTC_PROC_FIND_INFO_REQUEST_LENGTH = 5U,
    OPEN_CFW_ATTC_PROC_READ_REQUEST_LENGTH = 3U,
    OPEN_CFW_ATTC_PROC_WRITE_REQUEST_LENGTH = 3U,
    OPEN_CFW_ATTC_PROC_VALUE_CONFIRMATION_LENGTH = 1U
};

struct open_cfw_cordio_attc_configuration {
    uint32_t discovery_idle_timeout;
    uint16_t mtu;
    uint8_t transaction_timeout;
    uint8_t prepared_write_limit;
};

typedef void (*open_cfw_cordio_attc_callback_t)(
    struct open_cfw_cordio_att_event *event
);

#ifndef OPEN_CFW_ATTC_PROC_PRODUCTION
extern open_cfw_cordio_attc_callback_t open_cfw_cordio_attc_callback;
extern uint8_t open_cfw_cordio_attc_handler_id;
extern uint8_t open_cfw_cordio_attc_auto_confirm;
extern struct open_cfw_cordio_attc_api_message open_cfw_cordio_attc_on_deck[3];
extern struct open_cfw_cordio_attc_configuration
    *open_cfw_cordio_attc_configuration;
#endif

void open_cfw_cordio_att_set_mtu(
    struct open_cfw_cordio_attc_main_control_block *main,
    uint8_t slot,
    uint16_t peer_mtu,
    uint16_t local_mtu
);
uint16_t open_cfw_cordio_hci_get_max_rx_acl_length(void);
void open_cfw_cordio_wsf_timer_stop_candidate(void *timer);
void open_cfw_cordio_attc_free_packet(
    struct open_cfw_cordio_attc_api_message *message
);
void open_cfw_cordio_attc_send_request(
    struct open_cfw_cordio_attc_connection_control_block *connection
);
void open_cfw_cordio_attc_setup_request(
    struct open_cfw_cordio_attc_connection_control_block *connection,
    struct open_cfw_cordio_attc_api_message *message
);
void open_cfw_cordio_wsf_task_lock_candidate(void);
void open_cfw_cordio_wsf_task_unlock_candidate(void);
struct open_cfw_cordio_attc_connection_control_block *
open_cfw_cordio_attc_connection_by_id(uint8_t connection_id, uint8_t slot);
struct open_cfw_cordio_attc_connection_control_block *
open_cfw_cordio_attc_connection_by_handle(uint16_t handle, uint8_t slot);
void open_cfw_cordio_attc_execute_callback(
    uint8_t connection_id,
    uint8_t event,
    uint16_t handle,
    uint8_t status
);
void open_cfw_cordio_att_l2c_data_request(
    struct open_cfw_cordio_attc_main_control_block *main,
    uint8_t slot,
    uint16_t length,
    uint8_t *packet
);

void open_cfw_cordio_attc_process_error_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t,
    uint8_t *, struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_process_mtu_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t,
    uint8_t *, struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_process_find_or_read_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t,
    uint8_t *, struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_process_read_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t,
    uint8_t *, struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_process_write_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t,
    uint8_t *, struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_process_read_multiple_variable_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t,
    uint8_t *, struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_process_multiple_variable_notification(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t, uint8_t *
);
void open_cfw_cordio_attc_process_response(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t, uint8_t *
);
void open_cfw_cordio_attc_process_indication_notification(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t, uint8_t *
);
void open_cfw_cordio_attc_send_message(
    uint8_t, uint16_t, uint8_t,
    union open_cfw_cordio_attc_packet_parameter *, uint8_t
);
void open_cfw_cordio_attc_find_information_request(
    uint8_t, uint16_t, uint16_t, uint8_t
);
void open_cfw_cordio_attc_read_request(uint8_t, uint16_t);
void open_cfw_cordio_attc_write_request(
    uint8_t, uint16_t, uint16_t, uint8_t *
);
void open_cfw_cordio_attc_cancel_request(uint8_t);
void open_cfw_cordio_attc_mtu_request(uint8_t, uint16_t);
void open_cfw_cordio_attc_indication_confirm(uint8_t);

#endif
