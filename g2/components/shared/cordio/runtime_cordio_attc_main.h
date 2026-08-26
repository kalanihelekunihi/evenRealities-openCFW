/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTC_MAIN_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTC_MAIN_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_attc_proc.h"

enum {
    OPEN_CFW_ATTC_MAIN_CONNECTIONS = 3U,
    OPEN_CFW_ATTC_MAIN_BEARERS = 3U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_NONE = 0U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_MTU = 1U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_READ_MULTIPLE_VARIABLE = 16U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_SIGNED_WRITE = 17U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_CMAC_COMPLETE = 18U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_CANCEL = 19U,
    OPEN_CFW_ATTC_MAIN_MESSAGE_TIMEOUT = 20U,
    OPEN_CFW_ATTC_MAIN_CONNECTION_OPEN_EVENT = 0x27U,
    OPEN_CFW_ATTC_MAIN_CONNECTION_CLOSE_EVENT = 0x28U,
    OPEN_CFW_ATTC_MAIN_PDU_EXECUTE_WRITE_RESPONSE = 0x19U,
    OPEN_CFW_ATTC_MAIN_PDU_VALUE_NOTIFICATION = 0x1BU,
    OPEN_CFW_ATTC_MAIN_PDU_VALUE_INDICATION = 0x1DU,
    OPEN_CFW_ATTC_MAIN_PDU_MULTIPLE_VALUE_NOTIFICATION = 0x23U,
    OPEN_CFW_ATTC_MAIN_DEFAULT_MTU = 23U,
    OPEN_CFW_ATTC_MAIN_PREPARE_REQUEST_LENGTH = 5U,
    OPEN_CFW_ATTC_MAIN_L2C_PAYLOAD_START = 8U,
    OPEN_CFW_ATTC_MAIN_MTU_SENT = 0x01U,
    OPEN_CFW_ATTC_MAIN_FLOW_DISABLED = 0x02U,
    OPEN_CFW_ATTC_MAIN_TRANSACTION_TIMEOUT = 0x04U,
    OPEN_CFW_ATTC_MAIN_CONFIRM_PENDING = 0x10U,
    OPEN_CFW_ATTC_MAIN_SUCCESS = 0U,
    OPEN_CFW_ATTC_MAIN_ERROR_MEMORY = 0x70U,
    OPEN_CFW_ATTC_MAIN_ERROR_TIMEOUT = 0x71U,
    OPEN_CFW_ATTC_MAIN_ERROR_OVERFLOW = 0x72U,
    OPEN_CFW_ATTC_MAIN_ERROR_CANCELLED = 0x74U,
    OPEN_CFW_ATTC_MAIN_ERROR_MTU_EXCEEDED = 0x77U,
    OPEN_CFW_ATTC_MAIN_G2_HCI_ERROR_BASE = 0xA0U,
    OPEN_CFW_ATTC_MAIN_WRITE_COMMAND_RESPONSE = 10U,
    OPEN_CFW_ATTC_MAIN_MASTER_ROLE = 0U
};

struct open_cfw_cordio_attc_dm_event {
    struct open_cfw_cordio_wsf_message_header header;
    uint8_t reserved[4];
    uint8_t reason;
};

struct open_cfw_cordio_attc_main_timer {
    struct open_cfw_cordio_attc_main_timer *next;
    uint32_t ticks;
    struct open_cfw_cordio_wsf_message_header message;
    uint8_t handler_id;
    uint8_t is_started;
    uint8_t reserved[2];
};

struct open_cfw_cordio_attc_sign_interface {
    void (*message_callback)(
        struct open_cfw_cordio_attc_connection_control_block *,
        struct open_cfw_cordio_attc_api_message *
    );
    void (*close_callback)(
        struct open_cfw_cordio_attc_connection_control_block *, uint8_t
    );
};

struct open_cfw_cordio_attc_interface {
    void (*data_callback)(uint16_t, uint16_t, uint8_t *);
    void (*control_callback)(struct open_cfw_cordio_wsf_message_header *);
    void (*message_callback)(struct open_cfw_cordio_attc_api_message *);
    void (*connection_callback)(
        struct open_cfw_cordio_attc_main_control_block *,
        struct open_cfw_cordio_attc_dm_event *
    );
};

#ifndef OPEN_CFW_ATTC_MAIN_PRODUCTION
extern struct open_cfw_cordio_attc_connection_control_block
    open_cfw_cordio_attc_main_connections[3][3];
extern const struct open_cfw_cordio_attc_sign_interface
    *open_cfw_cordio_attc_sign_interface;
extern struct open_cfw_cordio_attc_main_control_block
    open_cfw_cordio_attc_main_control_blocks[3];
extern struct open_cfw_cordio_attc_interface
    *open_cfw_cordio_attc_client_interface;
extern struct open_cfw_cordio_attc_interface
    *open_cfw_cordio_attc_stock_interface;
#endif

uint8_t open_cfw_cordio_dm_connection_in_use(uint8_t connection_id);
uint8_t open_cfw_cordio_dm_connection_id_by_handle(uint16_t handle);
uint8_t open_cfw_cordio_dm_connection_role(uint8_t connection_id);
void open_cfw_cordio_att_execute_callback(
    uint8_t connection_id, uint8_t event, uint16_t handle,
    uint8_t status, uint16_t mtu
);
void open_cfw_cordio_wsf_timer_start_sec_candidate(void *, uint32_t);

uint8_t open_cfw_cordio_attc_pending_write_command(
    struct open_cfw_cordio_attc_connection_control_block *, uint16_t
);
void open_cfw_cordio_attc_set_pending_write_command(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_write_command_callback(
    uint8_t, struct open_cfw_cordio_attc_connection_control_block *, uint8_t
);
void open_cfw_cordio_attc_send_simple_request(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_send_continuing_request(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_send_mtu_request(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_send_write_command(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_send_prepare_write_request(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_send_request(
    struct open_cfw_cordio_attc_connection_control_block *
);
void open_cfw_cordio_attc_setup_request(
    struct open_cfw_cordio_attc_connection_control_block *,
    struct open_cfw_cordio_attc_api_message *
);
void open_cfw_cordio_attc_data_callback(uint16_t, uint16_t, uint8_t *);
void open_cfw_cordio_attc_control_callback(
    struct open_cfw_cordio_wsf_message_header *
);
void open_cfw_cordio_attc_connection_callback(
    struct open_cfw_cordio_attc_main_control_block *,
    struct open_cfw_cordio_attc_dm_event *
);
void open_cfw_cordio_attc_message_callback(
    struct open_cfw_cordio_attc_api_message *
);
struct open_cfw_cordio_attc_connection_control_block *
open_cfw_cordio_attc_connection_by_id(uint8_t, uint8_t);
struct open_cfw_cordio_attc_connection_control_block *
open_cfw_cordio_attc_connection_by_handle(uint16_t, uint8_t);
void open_cfw_cordio_attc_free_packet(
    struct open_cfw_cordio_attc_api_message *
);
void open_cfw_cordio_attc_execute_callback(
    uint8_t, uint8_t, uint16_t, uint8_t
);
void open_cfw_cordio_attc_request_clear(
    uint8_t, struct open_cfw_cordio_attc_api_message *, uint8_t
);
void open_cfw_cordio_attc_initialize(void);
void open_cfw_cordio_attc_set_auto_confirm(uint8_t enable);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_attc_main_timer) == 16U,
    "G2 ATTC timer ABI");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    outstanding_timer) == 24U, "G2 ATTC timer offset");
_Static_assert(offsetof(struct open_cfw_cordio_attc_connection_control_block,
    pending_write_handles) == 42U, "G2 ATTC pending-write offset");
_Static_assert(sizeof(struct open_cfw_cordio_attc_dm_event) == 10U,
    "G2 ATTC DM close-event prefix ABI");
#endif

#endif
