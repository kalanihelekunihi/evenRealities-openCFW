/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_MAIN_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_MAIN_H

#include <stdint.h>

#include "runtime_cordio_dm_dev.h"

enum {
    OPEN_CFW_DM_MAIN_HCI_ROUTES = 90U,
    OPEN_CFW_DM_MAIN_EVENT_LENGTHS = 92U,
    OPEN_CFW_DM_MAIN_CALLBACK_START = 0x20U,
    OPEN_CFW_DM_MAIN_CALLBACK_END = 0x7BU,
    OPEN_CFW_DM_MAIN_ERROR_EVENT = 0x78U,
    OPEN_CFW_DM_MAIN_LESC_COMPONENT = 8U,
    OPEN_CFW_DM_MAIN_CONNECTION_COMPONENT = 3U
};

#ifndef OPEN_CFW_DM_MAIN_PRODUCTION
extern uintptr_t open_cfw_cordio_dm_default_interface;
extern uint8_t open_cfw_cordio_dm_main_host_link_layer_privacy;
#endif

void open_cfw_cordio_hci_event_register(
    void (*callback)(struct open_cfw_cordio_dm_device_message_header *event));
uint16_t open_cfw_cordio_hci_get_maximum_receive_acl_length(void);

void open_cfw_cordio_dm_hci_event_callback(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_empty_reset(void);
void open_cfw_cordio_dm_empty_handler(
    struct open_cfw_cordio_dm_device_message_header *message);
void open_cfw_cordio_dm_pass_hci_event_to_connection(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_register_callback(uintptr_t callback);
uint8_t *open_cfw_cordio_dm_find_advertising_type(
    uint8_t advertising_type, uint16_t data_length, uint8_t *data);
void open_cfw_cordio_dm_handler_initialize(uint8_t handler_id);
void open_cfw_cordio_dm_handler(
    uint32_t event_mask,
    struct open_cfw_cordio_dm_device_message_header *message);
uint8_t open_cfw_cordio_dm_link_layer_privacy_enabled(void);
uint8_t open_cfw_cordio_dm_link_layer_address_type(uint8_t address_type);
uint8_t open_cfw_cordio_dm_host_address_type(uint8_t address_type);
uint16_t open_cfw_cordio_dm_size_of_event(
    const struct open_cfw_cordio_dm_device_message_header *event);
uint8_t open_cfw_cordio_dm_scan_phy_to_index_internal(
    uint8_t number_of_phys, uint8_t scan_phy);
uint8_t open_cfw_cordio_dm_scan_phy_to_index(uint8_t scan_phy);
uint8_t open_cfw_cordio_dm_initiator_phy_to_index_internal(
    uint8_t number_of_phys, uint8_t initiator_phy);
uint8_t open_cfw_cordio_dm_initiator_phy_to_index(uint8_t initiator_phy);

#endif
