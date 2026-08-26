/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_DEV_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_DEV_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_DM_DEVICE_COMPONENTS = 21U,
    OPEN_CFW_DM_DEVICE_PRIVACY_COMPONENT = 1U,
    OPEN_CFW_DM_CONNECTION_CTE_COMPONENT = 13U,
    OPEN_CFW_DM_DEVICE_ADV_SETS = 2U,
    OPEN_CFW_DM_DEVICE_ADDRESS_BYTES = 6U,
    OPEN_CFW_DM_DEVICE_RESET_REQUEST = 0x38U,
    OPEN_CFW_DM_CONNECTION_CTE_STATE = 0x6FU,
    OPEN_CFW_DM_RESET_COMPLETE = 0x20U,
    OPEN_CFW_DM_HARDWARE_ERROR = 0x79U,
    OPEN_CFW_DM_VENDOR_EVENT = 0x7AU,
    OPEN_CFW_DM_VENDOR_COMMAND_COMPLETE = 0x7BU
};

struct open_cfw_cordio_dm_device_message_header {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_cordio_dm_device_privacy_message {
    struct open_cfw_cordio_dm_device_message_header header;
    uint8_t advertising_handle;
    uint8_t connectable;
};

struct open_cfw_cordio_dm_device_function_interface {
    void (*reset)(void);
    void (*hci_handler)(struct open_cfw_cordio_dm_device_message_header *event);
    void (*message_handler)(struct open_cfw_cordio_dm_device_message_header *message);
};

#ifndef OPEN_CFW_DM_DEV_PRODUCTION
struct open_cfw_cordio_dm_device_main_control {
    uint8_t local_address[OPEN_CFW_DM_DEVICE_ADDRESS_BYTES];
    uintptr_t callback;
    uint8_t handler_id;
    uint8_t resetting;
    uint8_t advertising_filter_policy[OPEN_CFW_DM_DEVICE_ADV_SETS];
    uint8_t scanning_filter_policy;
    uint8_t initiator_filter_policy;
    uint8_t synchronization_options;
};

extern struct open_cfw_cordio_dm_device_main_control
    open_cfw_cordio_dm_device_main_control;
extern uintptr_t open_cfw_cordio_dm_device_function_interfaces[
    OPEN_CFW_DM_DEVICE_COMPONENTS
];
#endif

void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_message_send_candidate(uint8_t handler_id, void *message);
void open_cfw_cordio_hci_reset_sequence(void);
void open_cfw_cordio_hci_set_random_address(const uint8_t *address);
void open_cfw_cordio_hci_white_list_add(uint8_t address_type, const uint8_t *address);
void open_cfw_cordio_hci_white_list_remove(uint8_t address_type, const uint8_t *address);
void open_cfw_cordio_hci_white_list_clear(void);

void open_cfw_cordio_dm_device_action_reset(
    struct open_cfw_cordio_dm_device_message_header *message);
void open_cfw_cordio_dm_device_hci_reset_complete(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_device_hci_vendor_command_complete(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_device_hci_vendor_event(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_device_hci_hardware_error(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_device_hci_handler(
    struct open_cfw_cordio_dm_device_message_header *event);
void open_cfw_cordio_dm_device_message_handler(
    struct open_cfw_cordio_dm_device_message_header *message);
void open_cfw_cordio_dm_device_pass_event_to_privacy(
    uint8_t event, uint8_t parameter, uint8_t advertising_handle,
    uint8_t connectable);
void open_cfw_cordio_dm_device_pass_event_to_connection_cte(
    uint8_t state, uint8_t connection_id);
void open_cfw_cordio_dm_device_reset(void);
void open_cfw_cordio_dm_device_set_random_address(const uint8_t *address);
void open_cfw_cordio_dm_device_vendor_initialize(uint8_t parameter);

void open_cfw_cordio_dm_device_white_list_add(
    uint8_t address_type, const uint8_t *address);
void open_cfw_cordio_dm_device_white_list_remove(
    uint8_t address_type, const uint8_t *address);
void open_cfw_cordio_dm_device_white_list_clear(void);
uint8_t open_cfw_cordio_dm_device_set_filter_policy_internal(
    uint8_t advertising_handle, uint8_t mode, uint8_t policy);
uint8_t open_cfw_cordio_dm_device_set_filter_policy(
    uint8_t mode, uint8_t policy);
uint8_t open_cfw_cordio_dm_device_set_extended_filter_policy(
    uint8_t advertising_handle, uint8_t mode, uint8_t policy);

_Static_assert(sizeof(struct open_cfw_cordio_dm_device_message_header) == 4U,
    "G2 WSF message header ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_device_message_header,
    event) == 2U, "G2 WSF event offset");
_Static_assert(sizeof(struct open_cfw_cordio_dm_device_privacy_message) == 6U,
    "G2 DM privacy bridge ABI");

#endif
