/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_CONN_MASTER_LEG_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_CONN_MASTER_LEG_H
#include <stddef.h>
#include <stdint.h>

struct open_cfw_cordio_dm_connection_spec {
    uint16_t interval_minimum, interval_maximum, latency;
    uint16_t supervision_timeout, minimum_ce_length, maximum_ce_length;
};
struct open_cfw_cordio_dm_connection_open_message {
    uint16_t parameter;
    uint8_t event, status, initiating_phys, advertising_handle;
    uint8_t advertising_type, reserved;
    uint16_t duration;
    uint8_t maximum_extended_advertising_events;
    uint8_t peer_address[6];
    uint8_t address_type, client_id;
};
#ifndef OPEN_CFW_DM_CONN_MASTER_LEG_PRODUCTION
extern uint16_t open_cfw_cordio_dm_conn_master_leg_scan_interval[2];
extern uint16_t open_cfw_cordio_dm_conn_master_leg_scan_window[2];
extern struct open_cfw_cordio_dm_connection_spec
    open_cfw_cordio_dm_conn_master_leg_connection_spec[2];
extern uint8_t open_cfw_cordio_dm_conn_master_leg_initiator_filter_policy;
extern uint8_t open_cfw_cordio_dm_conn_master_leg_connection_address_type;
extern uintptr_t open_cfw_cordio_dm_conn_master_leg_action_sets[3];
extern uintptr_t open_cfw_cordio_dm_conn_master_leg_update_action_sets[3];
extern uintptr_t open_cfw_cordio_dm_conn_master_leg_master_action_table;
extern uintptr_t open_cfw_cordio_dm_conn_master_leg_master_update_action_table;
#endif
uint8_t open_cfw_cordio_dm_scan_phy_to_index(uint8_t phy);
uint8_t open_cfw_cordio_dm_link_layer_address_type(uint8_t type);
void open_cfw_cordio_hci_create_connection(uint16_t interval,uint16_t window,
    uint8_t filter,uint8_t peer_type,uint8_t *peer,uint8_t own_type,
    struct open_cfw_cordio_dm_connection_spec *spec);
void open_cfw_cordio_dm_device_pass_event_to_privacy(uint8_t event,
    uint8_t parameter,uint8_t advertising_handle,uint8_t connectable);
void open_cfw_cordio_wsf_task_lock(void);
void open_cfw_cordio_wsf_task_unlock(void);
void open_cfw_cordio_dm_connection_master_legacy_open(uint8_t initiating_phys,
    uint8_t address_type,uint8_t *address);
void open_cfw_cordio_dm_connection_master_legacy_action_open(void *connection,
    struct open_cfw_cordio_dm_connection_open_message *message);
void open_cfw_cordio_dm_connection_master_legacy_initialize(void);
_Static_assert(sizeof(struct open_cfw_cordio_dm_connection_spec)==12U,"G2 conn spec ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_connection_open_message,initiating_phys)==4U,"G2 open PHY offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_connection_open_message,peer_address)==11U,"G2 open address offset");
#endif
