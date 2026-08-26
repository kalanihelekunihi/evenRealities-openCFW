/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_L2C_H
#define OPEN_CFW_RUNTIME_CORDIO_L2C_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_L2C_CONNECTIONS = 3U,
    OPEN_CFW_L2C_CID_ATT = 4U,
    OPEN_CFW_L2C_CID_SIGNALING = 5U,
    OPEN_CFW_L2C_CID_SMP = 6U,
    OPEN_CFW_L2C_HEADER_LENGTH = 4U,
    OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH = 4U,
    OPEN_CFW_L2C_PAYLOAD_START = 8U,
    OPEN_CFW_L2C_SIGNAL_COMMAND_REJECT = 1U,
    OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_REQUEST = 0x12U,
    OPEN_CFW_L2C_SIGNAL_CONNECTION_UPDATE_RESPONSE = 0x13U,
    OPEN_CFW_L2C_REJECT_NOT_UNDERSTOOD = 0U,
    OPEN_CFW_L2C_CONNECTION_PARAMETERS_ACCEPTED = 0U,
    OPEN_CFW_L2C_CONNECTION_PARAMETERS_REJECTED = 1U,
    OPEN_CFW_L2C_SIGNAL_ID_INVALID = 0U,
    OPEN_CFW_L2C_CONNECTION_UPDATE_REQUEST_LENGTH = 8U,
    OPEN_CFW_L2C_CONNECTION_UPDATE_RESPONSE_LENGTH = 2U,
    OPEN_CFW_L2C_COMMAND_REJECT_LENGTH = 2U,
    OPEN_CFW_L2C_REQUEST_TIMEOUT_EVENT = 1U,
    OPEN_CFW_L2C_REQUEST_TIMEOUT_SECONDS = 30U,
    OPEN_CFW_L2C_ROLE_MASTER = 0U,
    OPEN_CFW_L2C_ROLE_SLAVE = 1U,
    OPEN_CFW_L2C_HCI_HANDLE_MASK = 0x0FFFU,
    OPEN_CFW_L2C_HCI_INTERVAL_MIN = 6U,
    OPEN_CFW_L2C_HCI_INTERVAL_MAX = 3200U,
    OPEN_CFW_L2C_HCI_LATENCY_MAX = 499U,
    OPEN_CFW_L2C_HCI_SUPERVISION_TIMEOUT_MIN = 10U,
    OPEN_CFW_L2C_HCI_SUPERVISION_TIMEOUT_MAX = 3200U
};

struct open_cfw_cordio_l2c_message_header {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_cordio_l2c_connection_specification {
    uint16_t interval_minimum;
    uint16_t interval_maximum;
    uint16_t latency;
    uint16_t supervision_timeout;
    uint16_t minimum_connection_event_length;
    uint16_t maximum_connection_event_length;
};

typedef void (*open_cfw_cordio_l2c_data_callback_t)(
    uint16_t, uint16_t, uint8_t *
);
typedef void (*open_cfw_cordio_l2c_cid_data_callback_t)(
    uint16_t, uint16_t, uint16_t, uint8_t *
);
typedef void (*open_cfw_cordio_l2c_control_callback_t)(
    struct open_cfw_cordio_l2c_message_header *
);

struct open_cfw_cordio_l2c_control_block {
    open_cfw_cordio_l2c_data_callback_t att_data_callback;
    open_cfw_cordio_l2c_data_callback_t smp_data_callback;
    open_cfw_cordio_l2c_data_callback_t signaling_callback;
    open_cfw_cordio_l2c_control_callback_t att_control_callback;
    open_cfw_cordio_l2c_control_callback_t smp_control_callback;
    open_cfw_cordio_l2c_control_callback_t coc_control_callback;
    open_cfw_cordio_l2c_data_callback_t master_signaling_callback;
    open_cfw_cordio_l2c_data_callback_t slave_signaling_callback;
    open_cfw_cordio_l2c_cid_data_callback_t cid_data_callback;
    uint8_t identifier;
    uint8_t reserved[3];
};

struct open_cfw_cordio_l2c_slave_control_block {
    uint8_t request_timer[16];
    uint8_t handler_id;
    uint8_t last_code[OPEN_CFW_L2C_CONNECTIONS];
    uint8_t signaling_id[OPEN_CFW_L2C_CONNECTIONS];
    uint8_t reserved;
};

#ifndef OPEN_CFW_L2C_PRODUCTION
extern struct open_cfw_cordio_l2c_control_block
    open_cfw_cordio_l2c_control_block;
extern struct open_cfw_cordio_l2c_slave_control_block
    open_cfw_cordio_l2c_slave_control_block;
#endif

uint8_t open_cfw_cordio_dm_connection_id_by_handle(uint16_t handle);
uint8_t open_cfw_cordio_dm_connection_role(uint8_t connection_id);
void open_cfw_cordio_hci_acl_register(
    void (*acl_callback)(uint8_t *),
    void (*flow_callback)(uint16_t, uint8_t)
);
void open_cfw_cordio_hci_send_acl_data(uint8_t *packet);
void *open_cfw_cordio_wsf_message_data_allocate_candidate(
    uint16_t length, uint8_t tailroom
);
void open_cfw_cordio_wsf_message_free_candidate(void *message);
void open_cfw_cordio_wsf_timer_start_sec_candidate(void *timer, uint32_t seconds);
void open_cfw_cordio_wsf_timer_stop_candidate(void *timer);
void open_cfw_cordio_dm_l2c_connection_update_indication(
    uint8_t identifier, uint16_t handle,
    struct open_cfw_cordio_l2c_connection_specification *specification
);
void open_cfw_cordio_dm_l2c_connection_update_confirmation(
    uint16_t handle, uint16_t result
);
void open_cfw_cordio_dm_l2c_command_reject_indication(
    uint16_t handle, uint16_t reason
);

void open_cfw_cordio_l2c_default_data_callback(
    uint16_t, uint16_t, uint8_t *
);
void open_cfw_cordio_l2c_default_cid_data_callback(
    uint16_t, uint16_t, uint16_t, uint8_t *
);
void open_cfw_cordio_l2c_default_control_callback(
    struct open_cfw_cordio_l2c_message_header *
);
void open_cfw_cordio_l2c_receive_signaling_packet(
    uint16_t, uint16_t, uint8_t *
);
void open_cfw_cordio_l2c_hci_acl_callback(uint8_t *);
void open_cfw_cordio_l2c_hci_flow_callback(uint16_t, uint8_t);
void open_cfw_cordio_l2c_send_command_reject(uint16_t, uint8_t, uint16_t);
void *open_cfw_cordio_l2c_message_allocate(uint16_t);
void open_cfw_cordio_l2c_initialize(void);
void open_cfw_cordio_l2c_register(
    uint16_t, open_cfw_cordio_l2c_data_callback_t,
    open_cfw_cordio_l2c_control_callback_t
);
void open_cfw_cordio_l2c_data_request(
    uint16_t, uint16_t, uint16_t, uint8_t *
);

void open_cfw_cordio_l2c_master_receive_signaling_packet(
    uint16_t, uint16_t, uint8_t *
);
void open_cfw_cordio_l2c_master_initialize(void);
void open_cfw_cordio_l2c_connection_update_response(
    uint8_t, uint16_t, uint16_t
);

void open_cfw_cordio_l2c_slave_request_timeout(
    struct open_cfw_cordio_l2c_message_header *
);
void open_cfw_cordio_l2c_slave_receive_signaling_packet(
    uint16_t, uint16_t, uint8_t *
);
void open_cfw_cordio_l2c_slave_initialize(void);
void open_cfw_cordio_l2c_signaling_request(
    uint16_t, uint8_t, uint16_t, const uint8_t *
);
void open_cfw_cordio_l2c_connection_update_request(
    uint16_t, const struct open_cfw_cordio_l2c_connection_specification *
);
void open_cfw_cordio_l2c_slave_handler_initialize(uint8_t);
void open_cfw_cordio_l2c_slave_handler(
    uint8_t, struct open_cfw_cordio_l2c_message_header *
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_l2c_control_block) == 40U,
    "G2 L2CAP control-block ABI");
_Static_assert(offsetof(struct open_cfw_cordio_l2c_control_block,
    master_signaling_callback) == 24U, "G2 L2CAP master callback offset");
_Static_assert(offsetof(struct open_cfw_cordio_l2c_control_block,
    cid_data_callback) == 32U, "G2 L2CAP CID callback offset");
_Static_assert(offsetof(struct open_cfw_cordio_l2c_control_block,
    identifier) == 36U, "G2 L2CAP identifier offset");
_Static_assert(sizeof(struct open_cfw_cordio_l2c_slave_control_block) == 24U,
    "G2 L2CAP slave control-block ABI");
#endif

#endif
