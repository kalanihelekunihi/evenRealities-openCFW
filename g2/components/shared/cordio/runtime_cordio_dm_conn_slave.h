/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_CONN_SLAVE_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_CONN_SLAVE_H
#include <stddef.h>
#include <stdint.h>
#include "runtime_cordio_dm_conn_master_leg.h"

struct open_cfw_cordio_dm_conn_slave_header {
    uint16_t parameter;
    uint8_t event, status;
};
struct open_cfw_cordio_dm_conn_slave_control {
    uint8_t peer_address[6], local_address[6];
    uint16_t handle, idle_mask;
    uint8_t connection_id, updating, using_ltk, peer_address_type;
    uint8_t local_address_type, state, in_use, security_level;
    uint8_t temporary_security_level, role;
    uint8_t local_rpa[6], peer_rpa[6], alignment[2];
    uint32_t features;
    uint8_t features_present, tail[3];
};
struct open_cfw_cordio_dm_conn_slave_update_message {
    struct open_cfw_cordio_dm_conn_slave_header header;
    struct open_cfw_cordio_dm_connection_spec connection_spec;
};
struct open_cfw_cordio_dm_conn_slave_confirm_message {
    struct open_cfw_cordio_dm_conn_slave_header header;
    uint16_t result;
};
struct open_cfw_cordio_dm_conn_slave_update_event {
    struct open_cfw_cordio_dm_conn_slave_header header;
    uint8_t status, reserved;
    uint16_t handle;
};
struct open_cfw_cordio_dm_conn_slave_reject_event {
    struct open_cfw_cordio_dm_conn_slave_header header;
    uint16_t reason, handle;
};
typedef void (*open_cfw_cordio_dm_conn_slave_callback_t)(void *event);

#ifndef OPEN_CFW_DM_CONN_SLAVE_PRODUCTION
extern open_cfw_cordio_dm_conn_slave_callback_t
    open_cfw_cordio_dm_conn_slave_application_callback;
#endif
uint64_t open_cfw_cordio_hci_get_supported_features(void);
void open_cfw_cordio_hci_connection_update(uint16_t handle,
    struct open_cfw_cordio_dm_connection_spec *specification);
void open_cfw_cordio_l2c_connection_update_request(uint16_t handle,
    struct open_cfw_cordio_dm_connection_spec *specification);
struct open_cfw_cordio_dm_conn_slave_control *
    open_cfw_cordio_dm_connection_control_by_handle(uint16_t handle);
void open_cfw_cordio_dm_connection_update_execute(
    struct open_cfw_cordio_dm_conn_slave_control *control, void *message);
uint8_t open_cfw_cordio_dm_connection_open_accept(uint8_t client_id,
    uint8_t initiating_phys,uint8_t advertising_handle,uint8_t advertising_type,
    uint16_t duration,uint8_t maximum_events,uint8_t address_type,
    uint8_t *address,uint8_t role);

void open_cfw_cordio_dm_connection_slave_update_callback(
    struct open_cfw_cordio_dm_conn_slave_control *control,uint8_t status);
void open_cfw_cordio_dm_connection_slave_action_update(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_slave_update_message *message);
void open_cfw_cordio_dm_connection_slave_action_l2c_confirm(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_slave_confirm_message *message);
void open_cfw_cordio_dm_connection_slave_l2c_confirm(uint16_t handle,uint16_t result);
void open_cfw_cordio_dm_connection_slave_l2c_reject(uint16_t handle,uint16_t result);
uint8_t open_cfw_cordio_dm_connection_slave_accept(uint8_t client_id,
    uint8_t advertising_handle,uint8_t advertising_type,uint16_t duration,
    uint8_t maximum_events,uint8_t address_type,uint8_t *address);

_Static_assert(sizeof(struct open_cfw_cordio_dm_conn_slave_control)==48U,"G2 CCB size");
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_slave_control,handle)==12U,"G2 CCB handle");
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_slave_control,connection_id)==16U,"G2 CCB ID");
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_slave_control,updating)==17U,"G2 CCB updating");
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_slave_control,features)==40U,"G2 CCB features");
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_slave_update_message,connection_spec)==4U,"G2 update spec");
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_slave_confirm_message,result)==4U,"G2 confirm result");
#endif
