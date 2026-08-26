/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_PHY_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_PHY_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_dm_dev.h"

enum {
    OPEN_CFW_DM_PHY_COMPONENT = 9U,
    OPEN_CFW_DM_PHY_HCI_READ_COMPLETE = 0x29U,
    OPEN_CFW_DM_PHY_HCI_DEFAULT_COMPLETE = 0x2AU,
    OPEN_CFW_DM_PHY_HCI_UPDATE_COMPLETE = 0x2BU,
    OPEN_CFW_DM_PHY_READ_INDICATION = 0x44U,
    OPEN_CFW_DM_PHY_DEFAULT_INDICATION = 0x45U,
    OPEN_CFW_DM_PHY_UPDATE_INDICATION = 0x46U,
    OPEN_CFW_DM_PHY_FEATURE_MASK = 0x0900U
};

struct open_cfw_cordio_dm_phy_connection {
    uint8_t peer_address[6];
    uint8_t local_address[6];
    uint16_t handle;
    uint16_t idle_mask;
    uint8_t connection_id;
    uint8_t updating;
    uint8_t using_ltk;
    uint8_t peer_address_type;
    uint8_t local_address_type;
    uint8_t state;
    uint8_t in_use;
    uint8_t security_level;
    uint8_t temporary_security_level;
    uint8_t role;
    uint8_t local_resolvable_address[6];
    uint8_t peer_resolvable_address[6];
    uint32_t features;
    uint8_t features_present;
};

struct open_cfw_cordio_dm_phy_event {
    struct open_cfw_cordio_dm_device_message_header header;
    uint8_t status;
    uint8_t reserved;
    uint16_t handle;
    uint8_t transmit_phy;
    uint8_t receive_phy;
};

#ifndef OPEN_CFW_DM_PHY_PRODUCTION
extern void (*open_cfw_cordio_dm_phy_host_callback)(void *event);
extern uintptr_t open_cfw_cordio_dm_phy_host_interface;
#endif

struct open_cfw_cordio_dm_phy_connection *
open_cfw_cordio_dm_connection_control_by_handle(uint16_t handle);
struct open_cfw_cordio_dm_phy_connection *
open_cfw_cordio_dm_connection_control_by_id(uint8_t connection_id);
void open_cfw_cordio_hci_read_phy(uint16_t handle);
void open_cfw_cordio_hci_set_default_phy(
    uint8_t all_phys, uint8_t transmit_phys, uint8_t receive_phys);
void open_cfw_cordio_hci_set_phy(
    uint16_t handle, uint8_t all_phys, uint8_t transmit_phys,
    uint8_t receive_phys, uint16_t phy_options);
void open_cfw_cordio_hci_set_supported_features(
    uint64_t feature_mask, uint8_t enable);
void open_cfw_cordio_wsf_task_lock(void);
void open_cfw_cordio_wsf_task_unlock(void);

void open_cfw_cordio_dm_phy_hci_handler(
    struct open_cfw_cordio_dm_phy_event *event);
void open_cfw_cordio_dm_phy_action_read(
    struct open_cfw_cordio_dm_phy_connection *connection,
    struct open_cfw_cordio_dm_phy_event *event);
void open_cfw_cordio_dm_phy_action_default(
    struct open_cfw_cordio_dm_phy_event *event);
void open_cfw_cordio_dm_phy_action_update(
    struct open_cfw_cordio_dm_phy_connection *connection,
    struct open_cfw_cordio_dm_phy_event *event);
void open_cfw_cordio_dm_phy_read(uint8_t connection_id);
void open_cfw_cordio_dm_phy_set_default(
    uint8_t all_phys, uint8_t transmit_phys, uint8_t receive_phys);
void open_cfw_cordio_dm_phy_set(
    uint8_t connection_id, uint8_t all_phys, uint8_t transmit_phys,
    uint8_t receive_phys, uint16_t phy_options);
void open_cfw_cordio_dm_phy_initialize(void);

_Static_assert(offsetof(struct open_cfw_cordio_dm_phy_connection, handle) == 12U,
    "G2 DM connection handle offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_phy_connection,
    connection_id) == 16U, "G2 DM connection identifier offset");
_Static_assert(sizeof(struct open_cfw_cordio_dm_phy_connection) == 48U,
    "G2 DM connection control block size");
_Static_assert(offsetof(struct open_cfw_cordio_dm_phy_event, status) == 4U,
    "G2 PHY event status offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_phy_event, handle) == 6U,
    "G2 PHY event handle offset");
_Static_assert(sizeof(struct open_cfw_cordio_dm_phy_event) == 10U,
    "G2 PHY event ABI");

#endif
