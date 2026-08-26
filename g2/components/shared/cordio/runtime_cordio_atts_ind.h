/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_IND_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_IND_H

#include "runtime_cordio_atts_proc.h"

enum {
    OPEN_CFW_ATTS_IND_CONNECTIONS = 3U,
    OPEN_CFW_ATTS_IND_BEARERS = 3U,
    OPEN_CFW_ATTS_IND_PENDING_NOTIFICATIONS = 10U,
    OPEN_CFW_ATTS_IND_VALUE_NOTIFICATION = 0x1BU,
    OPEN_CFW_ATTS_IND_VALUE_INDICATION = 0x1DU,
    OPEN_CFW_ATTS_IND_MULTIPLE_VALUE_NOTIFICATION = 0x23U,
    OPEN_CFW_ATTS_IND_API_EVENT = 0x21U,
    OPEN_CFW_ATTS_IND_TIMEOUT_EVENT = 0x22U,
    OPEN_CFW_ATTS_IND_VALUE_CONFIRM_EVENT = 0x12U,
    OPEN_CFW_ATTS_IND_MULTIPLE_CONFIRM_EVENT = 0x13U,
    OPEN_CFW_ATTS_IND_CONNECTION_OPEN_EVENT = 0x27U,
    OPEN_CFW_ATTS_IND_CONNECTION_CLOSE_EVENT = 0x28U,
    OPEN_CFW_ATTS_IND_FLOW_DISABLED = 0x02U,
    OPEN_CFW_ATTS_IND_TRANSACTION_TIMEOUT = 0x04U,
    OPEN_CFW_ATTS_IND_ERR_TIMEOUT = 0x71U,
    OPEN_CFW_ATTS_IND_ERR_OVERFLOW = 0x72U,
    OPEN_CFW_ATTS_IND_ERR_MTU_EXCEEDED = 0x77U,
    OPEN_CFW_ATTS_IND_G2_HCI_ERROR_BASE = 0xA0U
};

struct open_cfw_cordio_wsf_message_header {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_cordio_wsf_timer {
    struct open_cfw_cordio_wsf_timer *next;
    struct open_cfw_cordio_wsf_message_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t started;
    uint8_t reserved[2];
};

struct open_cfw_cordio_atts_ind_connection {
    struct open_cfw_cordio_wsf_timer indication_timer;
    struct open_cfw_cordio_att_main_control_block *main;
    struct open_cfw_cordio_wsf_timer idle_timer;
    uint8_t connection_id;
    uint8_t slot;
    uint16_t outstanding_indication_handle;
    uint16_t pending_indication_handle;
    uint16_t pending_notification_handle[OPEN_CFW_ATTS_IND_PENDING_NOTIFICATIONS];
    uint8_t reserved[2];
};

struct open_cfw_cordio_atts_ind_packet {
    uint16_t length;
    uint16_t handle;
    uint8_t reserved[4];
    uint8_t pdu[1];
};

struct open_cfw_cordio_atts_ind_api_message {
    struct open_cfw_cordio_wsf_message_header header;
    struct open_cfw_cordio_atts_ind_packet *packet;
    uint8_t slot;
    uint8_t reserved[3];
};

struct open_cfw_cordio_dm_event {
    struct open_cfw_cordio_wsf_message_header header;
    uint8_t reserved[4];
    uint8_t reason;
};

#ifndef OPEN_CFW_ATTS_IND_PRODUCTION
extern struct open_cfw_cordio_atts_ind_connection
    open_cfw_cordio_atts_ind_connections[3][3];
extern uint8_t open_cfw_cordio_att_handler_id;
extern uint8_t open_cfw_cordio_atts_service_changed_uuid[2];
extern void *open_cfw_cordio_atts_indication_interface;
#endif

void open_cfw_cordio_att_execute_callback(
    uint8_t connection_id, uint8_t event, uint16_t handle,
    uint8_t status, uint16_t mtu
);
uint16_t open_cfw_cordio_att_message_parameter(uint8_t connection_id, uint8_t slot);
void open_cfw_cordio_att_decode_message_parameter(
    uint16_t parameter, uint8_t *connection_id, uint8_t *slot
);
void open_cfw_cordio_wsf_timer_start_seconds(
    struct open_cfw_cordio_wsf_timer *timer, uint32_t seconds
);
void open_cfw_cordio_wsf_timer_stop(struct open_cfw_cordio_wsf_timer *timer);
struct open_cfw_cordio_atts_ind_connection *
open_cfw_cordio_atts_ind_connection_by_id(uint8_t connection_id, uint8_t slot);
void open_cfw_cordio_wsf_task_lock(void);
void open_cfw_cordio_wsf_task_unlock(void);
void *open_cfw_cordio_wsf_message_allocate(uint16_t length);
void open_cfw_cordio_wsf_message_send(uint8_t handler_id, void *message);
uint8_t open_cfw_cordio_atts_csf_is_client_change_aware(
    uint8_t connection_id, uint16_t handle
);
uint8_t open_cfw_cordio_atts_csf_get_change_aware_state(uint8_t connection_id);
void open_cfw_cordio_atts_csf_set_clients_change_awareness_state(
    uint8_t connection_id, uint8_t state
);

uint8_t open_cfw_cordio_atts_ind_pending(
    struct open_cfw_cordio_atts_ind_connection *connection,
    struct open_cfw_cordio_atts_ind_packet *packet
);
void open_cfw_cordio_atts_ind_set_pending_notification(
    struct open_cfw_cordio_atts_ind_connection *connection, uint16_t handle
);
void open_cfw_cordio_atts_ind_execute_callback(
    uint8_t connection_id, uint16_t handle, uint8_t status
);
void open_cfw_cordio_atts_ind_notification_callback(
    uint8_t connection_id,
    struct open_cfw_cordio_atts_ind_connection *connection,
    uint8_t status
);
void open_cfw_cordio_atts_ind_setup_message(
    struct open_cfw_cordio_atts_ind_connection *connection,
    uint8_t connection_id, uint8_t slot,
    struct open_cfw_cordio_atts_ind_packet *packet
);
void open_cfw_cordio_atts_ind_connection_callback(
    struct open_cfw_cordio_att_main_control_block *main,
    struct open_cfw_cordio_dm_event *event
);
void open_cfw_cordio_atts_ind_message_callback(
    struct open_cfw_cordio_atts_ind_api_message *message
);
void open_cfw_cordio_atts_ind_control_callback(
    struct open_cfw_cordio_wsf_message_header *message
);
void open_cfw_cordio_atts_handle_value_indication_notification(
    uint8_t connection_id, uint16_t handle, uint8_t slot,
    uint16_t value_length, uint8_t *value, uint8_t opcode, uint8_t zero_copy
);
void open_cfw_cordio_atts_process_value_confirmation(
    struct open_cfw_cordio_atts_ind_connection *connection,
    uint16_t length, uint8_t *packet
);
void open_cfw_cordio_atts_ind_initialize(void);
void open_cfw_cordio_atts_handle_value_indication(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
);
void open_cfw_cordio_atts_handle_value_notification(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
);
void open_cfw_cordio_atts_handle_value_indication_zero_copy(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
);
void open_cfw_cordio_atts_handle_value_notification_zero_copy(
    uint8_t connection_id, uint16_t handle, uint16_t length, uint8_t *value
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_wsf_timer) == 16U,
    "G2 WSF timer ABI");
_Static_assert(sizeof(struct open_cfw_cordio_atts_ind_connection) == 64U,
    "G2 ATTS indication CCB ABI");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ind_connection,
    connection_id) == 0x24U, "G2 ATTS indication connection offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ind_connection,
    outstanding_indication_handle) == 0x26U,
    "G2 ATTS outstanding indication offset");
_Static_assert(offsetof(struct open_cfw_cordio_atts_ind_connection,
    pending_notification_handle) == 0x2AU,
    "G2 ATTS pending notification offset");
_Static_assert(sizeof(struct open_cfw_cordio_atts_ind_api_message) == 12U,
    "G2 ATTS indication API message ABI");
#endif

#endif
