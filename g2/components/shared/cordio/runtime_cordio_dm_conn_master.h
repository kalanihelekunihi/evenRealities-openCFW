/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_CONN_MASTER_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_CONN_MASTER_H
#include <stddef.h>
#include <stdint.h>
#include "runtime_cordio_dm_conn_slave.h"

struct open_cfw_cordio_dm_conn_master_l2c_indication {
    struct open_cfw_cordio_dm_conn_slave_header header;
    struct open_cfw_cordio_dm_connection_spec *connection_spec;
    uint8_t identifier;
} __attribute__((packed));
#ifndef OPEN_CFW_DM_CONN_MASTER_PRODUCTION
extern uint8_t open_cfw_cordio_dm_conn_master_address_type;
#endif
void open_cfw_cordio_hci_create_connection_cancel(void);
void open_cfw_cordio_dm_device_pass_event_to_privacy(uint8_t event,
    uint8_t parameter,uint8_t advertising_handle,uint8_t connectable);
void open_cfw_cordio_l2c_connection_update_response(uint8_t identifier,
    uint16_t handle,uint16_t result);
void open_cfw_cordio_wsf_task_lock(void);
void open_cfw_cordio_wsf_task_unlock(void);

void open_cfw_cordio_dm_connection_master_action_cancel(
    struct open_cfw_cordio_dm_conn_slave_control *control,void *message);
void open_cfw_cordio_dm_connection_master_action_update(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_slave_update_message *message);
void open_cfw_cordio_dm_connection_master_action_l2c_indication(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_master_l2c_indication *message);
void open_cfw_cordio_dm_connection_master_l2c_indication(uint8_t identifier,
    uint16_t handle,struct open_cfw_cordio_dm_connection_spec *specification);
uint8_t open_cfw_cordio_dm_connection_master_open(uint8_t client_id,
    uint8_t initiating_phys,uint8_t address_type,uint8_t *address);
void open_cfw_cordio_dm_connection_master_set_address_type(uint8_t address_type);

_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_master_l2c_indication,
    connection_spec)==4U,"G2 master L2C spec pointer");
#ifdef OPEN_CFW_DM_CONN_MASTER_PRODUCTION
_Static_assert(offsetof(struct open_cfw_cordio_dm_conn_master_l2c_indication,
    identifier)==8U,"G2 master L2C identifier");
#endif
#endif
