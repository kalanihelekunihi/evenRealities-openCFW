/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_CONN_SLAVE_LEG_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_CONN_SLAVE_LEG_H
#include <stdint.h>
#include "runtime_cordio_dm_conn_master_leg.h"
#ifndef OPEN_CFW_DM_CONN_SLAVE_LEG_PRODUCTION
extern uintptr_t open_cfw_cordio_dm_conn_slave_leg_action_sets[3];
extern uintptr_t open_cfw_cordio_dm_conn_slave_leg_update_action_sets[3];
extern uintptr_t open_cfw_cordio_dm_conn_slave_leg_action_table;
extern uintptr_t open_cfw_cordio_dm_conn_slave_leg_update_action_table;
#endif
void open_cfw_cordio_dm_advertising_start_directed(uint8_t type,uint16_t duration,uint8_t address_type,uint8_t *address);
void open_cfw_cordio_dm_advertising_stop_directed(void);
void open_cfw_cordio_dm_advertising_connected(void);
void open_cfw_cordio_dm_advertising_connect_failed(void);
void open_cfw_cordio_dm_connection_action_opened(void *connection,void *message);
void open_cfw_cordio_dm_connection_action_failed(void *connection,void *message);
void open_cfw_cordio_dm_connection_slave_legacy_action_accept(void *connection,struct open_cfw_cordio_dm_connection_open_message *message);
void open_cfw_cordio_dm_connection_slave_legacy_action_cancel(void *connection,void *message);
void open_cfw_cordio_dm_connection_slave_legacy_action_accepted(void *connection,void *message);
void open_cfw_cordio_dm_connection_slave_legacy_action_failed(void *connection,void *message);
void open_cfw_cordio_dm_connection_slave_legacy_initialize(void);
#endif
