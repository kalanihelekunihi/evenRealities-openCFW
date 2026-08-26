/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_ADV_LEG_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_ADV_LEG_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_dm_adv.h"

enum {
    OPEN_CFW_DM_ADV_LEG_DEFAULT_HANDLE = 0U,
    OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED = 1U,
    OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED_LOW_DUTY = 4U,
    OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING = 1U,
    OPEN_CFW_DM_ADV_LEG_STATE_STARTING_DIRECTED = 2U,
    OPEN_CFW_DM_ADV_LEG_STATE_STARTING = 3U,
    OPEN_CFW_DM_ADV_LEG_STATE_STOPPING_DIRECTED = 4U,
    OPEN_CFW_DM_ADV_LEG_STATE_STOPPING = 5U,
    OPEN_CFW_DM_ADV_LEG_MESSAGE_TIMEOUT = 7U,
    OPEN_CFW_DM_ADV_LEG_DEVICE_RPA_START = 12U,
    OPEN_CFW_DM_ADV_LEG_DEVICE_RPA_STOP = 13U,
    OPEN_CFW_DM_ADV_LEG_START_INDICATION = 0x21U,
    OPEN_CFW_DM_ADV_LEG_STOP_INDICATION = 0x22U,
    OPEN_CFW_DM_ADV_LEG_HCI_ADV_ENABLE_COMPLETE = 53U,
    OPEN_CFW_DM_ADV_LEG_HCI_ADVERTISING_TIMEOUT = 0x3CU,
    OPEN_CFW_DM_ADV_LEG_DATA_MAXIMUM = 31U
};

struct open_cfw_cordio_dm_adv_legacy_timer {
    uint32_t next;
    struct open_cfw_cordio_dm_message_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t started;
    uint8_t reserved[2];
};

struct open_cfw_cordio_dm_adv_legacy_config_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t advertising_handle;
    uint8_t advertising_type;
    uint8_t peer_address_type;
    uint8_t peer_address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
    uint8_t scan_request_notification_enabled;
};

struct open_cfw_cordio_dm_adv_legacy_set_data_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t advertising_handle;
    uint8_t operation;
    uint8_t location;
    uint8_t length;
    uint8_t data[];
};

struct open_cfw_cordio_dm_adv_legacy_start_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t number_of_sets;
    uint8_t advertising_handle[OPEN_CFW_DM_ADV_SETS];
    uint16_t duration[OPEN_CFW_DM_ADV_SETS];
    uint8_t maximum_extended_events[OPEN_CFW_DM_ADV_SETS];
};

union open_cfw_cordio_dm_adv_legacy_message {
    struct open_cfw_cordio_dm_message_header header;
    struct open_cfw_cordio_dm_adv_legacy_config_message configure;
    struct open_cfw_cordio_dm_adv_legacy_set_data_message set_data;
    struct open_cfw_cordio_dm_adv_legacy_start_message start;
};

struct open_cfw_cordio_dm_adv_legacy_function_interface {
    void (*reset)(void);
    void (*hci_handler)(struct open_cfw_cordio_dm_message_header *event);
    void (*message_handler)(struct open_cfw_cordio_dm_message_header *message);
};

#ifndef OPEN_CFW_DM_ADV_LEG_PRODUCTION
extern uint8_t open_cfw_cordio_dm_adv_legacy_type;
extern const struct open_cfw_cordio_dm_adv_legacy_function_interface
    *open_cfw_cordio_dm_adv_registered_interface;
extern uintptr_t open_cfw_cordio_dm_dev_adv_set_random_address_callback;
#endif

uint8_t open_cfw_cordio_dm_legacy_link_layer_address_type(uint8_t type);
void open_cfw_cordio_hci_set_legacy_advertising_parameters(
    uint16_t interval_minimum, uint16_t interval_maximum,
    uint8_t advertising_type, uint8_t own_address_type,
    uint8_t peer_address_type, const uint8_t *peer_address,
    uint8_t channel_map, uint8_t filter_policy
);
void open_cfw_cordio_hci_set_legacy_advertising_data(
    uint8_t length, const uint8_t *data
);
void open_cfw_cordio_hci_set_legacy_scan_response_data(
    uint8_t length, const uint8_t *data
);
void open_cfw_cordio_hci_set_legacy_advertising_enable(uint8_t enabled);
void open_cfw_cordio_wsf_timer_start_ms(void *timer, uint32_t milliseconds);
void open_cfw_cordio_wsf_timer_stop(void *timer);
void open_cfw_cordio_dm_device_pass_private_event(
    uint8_t event, uint8_t parameter, uint8_t advertising_handle,
    uint8_t connectable
);
void open_cfw_cordio_dm_adv_legacy_application_callback(void *event);

void open_cfw_cordio_dm_adv_legacy_configure_parameters(
    uint8_t advertising_type, uint8_t peer_address_type,
    const uint8_t *peer_address
);
void open_cfw_cordio_dm_adv_legacy_action_configure(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_set_data(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_start(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_stop(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_remove_set(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_clear_sets(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_set_random_address(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_action_timeout(
    union open_cfw_cordio_dm_adv_legacy_message *message
);
void open_cfw_cordio_dm_adv_legacy_reset(void);
void open_cfw_cordio_dm_adv_legacy_hci_handler(
    struct open_cfw_cordio_dm_message_header *event
);
void open_cfw_cordio_dm_adv_legacy_message_handler(
    struct open_cfw_cordio_dm_message_header *message
);
void open_cfw_cordio_dm_adv_legacy_start_directed(
    uint8_t advertising_type, uint16_t duration, uint8_t address_type,
    const uint8_t *address
);
void open_cfw_cordio_dm_adv_legacy_stop_directed(void);
void open_cfw_cordio_dm_adv_legacy_connected(void);
void open_cfw_cordio_dm_adv_legacy_connect_failed(void);
void open_cfw_cordio_dm_adv_legacy_initialize(void);
uint8_t open_cfw_cordio_dm_adv_mode_legacy(void);

_Static_assert(sizeof(struct open_cfw_cordio_dm_adv_legacy_timer) == 16U,
    "G2 legacy advertising timer ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_adv_legacy_timer,
    message.event) == 6U, "G2 legacy advertising timer event offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_adv_legacy_set_data_message,
    data) == 8U, "Ambiq flexible-array advertising payload ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_adv_legacy_start_message,
    duration) == 8U, "G2 advertising-start duration ABI");

#endif
