/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_dm_conn_master_leg.h"
#if !defined(OPEN_CFW_DM_CONN_MASTER_LEG_OPEN_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_LEG_ACTION_OPEN_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_LEG_INIT_ONLY)
#define OPEN_CFW_DM_CONN_MASTER_LEG_ALL 1
#endif
#ifdef OPEN_CFW_DM_CONN_MASTER_LEG_PRODUCTION
#define SCAN_INTERVAL ((uint16_t *)(uintptr_t)0x20071360U)
#define SCAN_WINDOW ((uint16_t *)(uintptr_t)0x20071364U)
#define CONN_SPEC ((struct open_cfw_cordio_dm_connection_spec *)(uintptr_t)0x20071348U)
#define INIT_FILTER (*(uint8_t *)(uintptr_t)0x20073B8CU)
#define CONN_ADDR_TYPE (*(uint8_t *)(uintptr_t)0x20073B85U)
#define ACTION_SETS ((uintptr_t *)(uintptr_t)0x20073FE4U)
#define UPDATE_ACTION_SETS ((uintptr_t *)(uintptr_t)0x20073FD8U)
#define MASTER_ACTION_TABLE ((uintptr_t)0x0078D424U)
#define MASTER_UPDATE_ACTION_TABLE ((uintptr_t)0x0078D41CU)
#else
uint16_t open_cfw_cordio_dm_conn_master_leg_scan_interval[2];
uint16_t open_cfw_cordio_dm_conn_master_leg_scan_window[2];
struct open_cfw_cordio_dm_connection_spec open_cfw_cordio_dm_conn_master_leg_connection_spec[2];
uint8_t open_cfw_cordio_dm_conn_master_leg_initiator_filter_policy;
uint8_t open_cfw_cordio_dm_conn_master_leg_connection_address_type;
uintptr_t open_cfw_cordio_dm_conn_master_leg_action_sets[3];
uintptr_t open_cfw_cordio_dm_conn_master_leg_update_action_sets[3];
uintptr_t open_cfw_cordio_dm_conn_master_leg_master_action_table;
uintptr_t open_cfw_cordio_dm_conn_master_leg_master_update_action_table;
#define SCAN_INTERVAL open_cfw_cordio_dm_conn_master_leg_scan_interval
#define SCAN_WINDOW open_cfw_cordio_dm_conn_master_leg_scan_window
#define CONN_SPEC open_cfw_cordio_dm_conn_master_leg_connection_spec
#define INIT_FILTER open_cfw_cordio_dm_conn_master_leg_initiator_filter_policy
#define CONN_ADDR_TYPE open_cfw_cordio_dm_conn_master_leg_connection_address_type
#define ACTION_SETS open_cfw_cordio_dm_conn_master_leg_action_sets
#define UPDATE_ACTION_SETS open_cfw_cordio_dm_conn_master_leg_update_action_sets
#define MASTER_ACTION_TABLE open_cfw_cordio_dm_conn_master_leg_master_action_table
#define MASTER_UPDATE_ACTION_TABLE open_cfw_cordio_dm_conn_master_leg_master_update_action_table
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_LEG_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_LEG_OPEN_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_legacy_open(
    uint8_t initiating_phys,uint8_t address_type,uint8_t *address)
{
    uint8_t index;
    if (address==NULL || (initiating_phys&1U)==0U) return;
    index=open_cfw_cordio_dm_scan_phy_to_index(1U);
    if (index>=2U) return;
    open_cfw_cordio_hci_create_connection(SCAN_INTERVAL[index],SCAN_WINDOW[index],
        INIT_FILTER,address_type,address,
        open_cfw_cordio_dm_link_layer_address_type(CONN_ADDR_TYPE),&CONN_SPEC[index]);
    open_cfw_cordio_dm_device_pass_event_to_privacy(0x30U,1U,0U,0U);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_LEG_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_LEG_ACTION_OPEN_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_legacy_action_open(
    void *connection,struct open_cfw_cordio_dm_connection_open_message *message)
{
    (void)connection;if(message==NULL)return;
    open_cfw_cordio_dm_connection_master_legacy_open(message->initiating_phys,
        message->address_type,message->peer_address);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_LEG_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_LEG_INIT_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_legacy_initialize(void)
{
    open_cfw_cordio_wsf_task_lock();ACTION_SETS[1]=MASTER_ACTION_TABLE;
    UPDATE_ACTION_SETS[1]=MASTER_UPDATE_ACTION_TABLE;open_cfw_cordio_wsf_task_unlock();
}
#endif
