/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_dm_conn_slave_leg.h"
#if !defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ACCEPT_ONLY)&&!defined(OPEN_CFW_DM_CONN_SLAVE_LEG_CANCEL_ONLY)&&!defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ACCEPTED_ONLY)&&!defined(OPEN_CFW_DM_CONN_SLAVE_LEG_FAILED_ONLY)&&!defined(OPEN_CFW_DM_CONN_SLAVE_LEG_INIT_ONLY)
#define OPEN_CFW_DM_CONN_SLAVE_LEG_ALL 1
#endif
#ifdef OPEN_CFW_DM_CONN_SLAVE_LEG_PRODUCTION
#define ACTION_SETS ((uintptr_t *)(uintptr_t)0x20073FE4U)
#define UPDATE_SETS ((uintptr_t *)(uintptr_t)0x20073FD8U)
#define ACTION_TABLE ((uintptr_t)0x00785BE0U)
#define UPDATE_TABLE ((uintptr_t)0x0078D42CU)
#else
uintptr_t open_cfw_cordio_dm_conn_slave_leg_action_sets[3],open_cfw_cordio_dm_conn_slave_leg_update_action_sets[3];
uintptr_t open_cfw_cordio_dm_conn_slave_leg_action_table,open_cfw_cordio_dm_conn_slave_leg_update_action_table;
#define ACTION_SETS open_cfw_cordio_dm_conn_slave_leg_action_sets
#define UPDATE_SETS open_cfw_cordio_dm_conn_slave_leg_update_action_sets
#define ACTION_TABLE open_cfw_cordio_dm_conn_slave_leg_action_table
#define UPDATE_TABLE open_cfw_cordio_dm_conn_slave_leg_update_action_table
#endif
#if defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ACCEPT_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_legacy_action_accept(void *connection,struct open_cfw_cordio_dm_connection_open_message *message){(void)connection;if(message==NULL)return;open_cfw_cordio_dm_advertising_start_directed(message->advertising_type,message->duration,message->address_type,message->peer_address);}
#endif
#if defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_LEG_CANCEL_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_legacy_action_cancel(void *connection,void *message){if(connection==NULL||message==NULL)return;open_cfw_cordio_dm_advertising_stop_directed();open_cfw_cordio_dm_connection_action_failed(connection,message);}
#endif
#if defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ACCEPTED_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_legacy_action_accepted(void *connection,void *message){if(connection==NULL||message==NULL)return;open_cfw_cordio_dm_advertising_connected();open_cfw_cordio_dm_connection_action_opened(connection,message);}
#endif
#if defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_LEG_FAILED_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_legacy_action_failed(void *connection,void *message){if(connection==NULL||message==NULL)return;open_cfw_cordio_dm_advertising_connect_failed();open_cfw_cordio_dm_connection_action_failed(connection,message);}
#endif
#if defined(OPEN_CFW_DM_CONN_SLAVE_LEG_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_LEG_INIT_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_legacy_initialize(void){open_cfw_cordio_wsf_task_lock();ACTION_SETS[2]=ACTION_TABLE;UPDATE_SETS[2]=UPDATE_TABLE;open_cfw_cordio_wsf_task_unlock();}
#endif
