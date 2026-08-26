/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_ADV_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_ADV_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_DM_ADV_SETS = 2U,
    OPEN_CFW_DM_ADV_ADDRESS_BYTES = 6U,
    OPEN_CFW_DM_ADV_NONE = 0xFFU,
    OPEN_CFW_DM_ADV_SLOW_INTERVAL_MINIMUM = 1600U,
    OPEN_CFW_DM_ADV_SLOW_INTERVAL_MAXIMUM = 1920U,
    OPEN_CFW_DM_ADV_CHANNEL_ALL = 7U,
    OPEN_CFW_DM_ADV_FILTER_NONE = 0U,
    OPEN_CFW_DM_ADV_STATE_IDLE = 0U,
    OPEN_CFW_DM_ADV_ADDRESS_PUBLIC = 0U,
    OPEN_CFW_DM_ROLE_SLAVE = 1U,
    OPEN_CFW_HCI_ENHANCED_CONNECTION_COMPLETE_EVENT = 2U,
    OPEN_CFW_DM_ADV_DATA_LOCATION_ADVERTISING = 0U,
    OPEN_CFW_DM_ADV_DATA_LOCATION_SCAN = 1U,
    OPEN_CFW_DM_ADV_MAXIMUM_DATA_LENGTH = 236U,
    OPEN_CFW_DM_ADV_MAXIMUM_ELEMENT_VALUE_LENGTH = 29U,
    OPEN_CFW_DM_ADV_TYPE_SHORT_NAME = 8U,
    OPEN_CFW_DM_ADV_TYPE_LOCAL_NAME = 9U,
    OPEN_CFW_DM_ADV_MESSAGE_CONFIGURE = 0U,
    OPEN_CFW_DM_ADV_MESSAGE_SET_DATA = 1U,
    OPEN_CFW_DM_ADV_MESSAGE_START = 2U,
    OPEN_CFW_DM_ADV_MESSAGE_STOP = 3U,
    OPEN_CFW_DM_ADV_MESSAGE_REMOVE = 4U,
    OPEN_CFW_DM_ADV_MESSAGE_CLEAR = 5U,
    OPEN_CFW_DM_ADV_MESSAGE_SET_RANDOM_ADDRESS = 6U
};

struct open_cfw_cordio_dm_message_header {
    uint16_t parameter;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_cordio_dm_connection_complete_event {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t status;
    uint16_t handle;
    uint8_t role;
    uint8_t address_type;
    uint8_t peer_address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
    uint16_t connection_interval;
    uint16_t connection_latency;
    uint16_t supervision_timeout;
    uint8_t clock_accuracy;
    uint8_t local_resolvable_address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
    uint8_t peer_resolvable_address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
};

struct open_cfw_cordio_dm_adv_control_block {
    uint8_t advertising_timer[16];
    uint16_t interval_minimum[OPEN_CFW_DM_ADV_SETS];
    uint16_t interval_maximum[OPEN_CFW_DM_ADV_SETS];
    uint8_t advertising_type[OPEN_CFW_DM_ADV_SETS];
    uint8_t channel_map[OPEN_CFW_DM_ADV_SETS];
    uint8_t local_address_type;
    uint8_t advertising_state[OPEN_CFW_DM_ADV_SETS];
    uint16_t advertising_duration[OPEN_CFW_DM_ADV_SETS];
    uint8_t advertising_enabled;
    uint8_t peer_address[OPEN_CFW_DM_ADV_SETS][OPEN_CFW_DM_ADV_ADDRESS_BYTES];
    uint8_t peer_address_type[OPEN_CFW_DM_ADV_SETS];
};

struct open_cfw_cordio_dm_main_control_block {
    uint8_t local_address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
    uint8_t reserved_address_alignment[2];
    uint32_t callback;
    uint8_t handler_id;
    uint8_t connection_address_type;
    uint8_t advertising_address_type;
    uint8_t scan_address_type;
    uint8_t resetting;
    uint8_t advertising_filter_policy[OPEN_CFW_DM_ADV_SETS];
    uint8_t scan_filter_policy;
    uint8_t initiator_filter_policy;
    uint8_t synchronization_options;
    uint8_t link_layer_privacy_enabled;
};

#ifndef OPEN_CFW_DM_ADV_PRODUCTION
extern struct open_cfw_cordio_dm_adv_control_block
    open_cfw_cordio_dm_adv_control_block;
extern struct open_cfw_cordio_dm_main_control_block
    open_cfw_cordio_dm_main_control_block;
#endif

void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t length);
void open_cfw_cordio_wsf_message_send_candidate(uint8_t handler_id, void *message);
void open_cfw_cordio_wsf_task_lock_candidate(void);
void open_cfw_cordio_wsf_task_unlock_candidate(void);
void open_cfw_cordio_dm_device_pass_hci_event_to_connection(
    struct open_cfw_cordio_dm_connection_complete_event *event
);

void open_cfw_cordio_dm_adv_control_block_initialize(uint8_t advertising_handle);
void open_cfw_cordio_dm_adv_initialize(void);
void open_cfw_cordio_dm_adv_generate_connection_complete(
    uint8_t advertising_handle, uint8_t status
);
void open_cfw_cordio_dm_adv_configure(
    uint8_t advertising_handle, uint8_t advertising_type,
    uint8_t peer_address_type, const uint8_t *peer_address
);
void open_cfw_cordio_dm_adv_set_data(
    uint8_t advertising_handle, uint8_t operation, uint8_t location,
    uint8_t length, const uint8_t *data
);
void open_cfw_cordio_dm_adv_start(
    uint8_t number_of_sets, const uint8_t *advertising_handles,
    const uint16_t *durations, const uint8_t *maximum_extended_events
);
void open_cfw_cordio_dm_adv_stop(
    uint8_t number_of_sets, const uint8_t *advertising_handles
);
void open_cfw_cordio_dm_adv_remove_set(uint8_t advertising_handle);
void open_cfw_cordio_dm_adv_clear_sets(void);
void open_cfw_cordio_dm_adv_set_random_address(
    uint8_t advertising_handle, const uint8_t *address
);
void open_cfw_cordio_dm_adv_set_interval(
    uint8_t advertising_handle, uint16_t interval_minimum,
    uint16_t interval_maximum
);
void open_cfw_cordio_dm_adv_set_channel_map(
    uint8_t advertising_handle, uint8_t channel_map
);
void open_cfw_cordio_dm_adv_set_address_type(uint8_t address_type);
uint8_t open_cfw_cordio_dm_adv_set_element(
    uint8_t advertising_data_type, uint8_t length, const uint8_t *value,
    uint16_t *advertising_data_length, uint8_t *advertising_data,
    uint16_t advertising_data_buffer_length
);
uint8_t open_cfw_cordio_dm_adv_set_name(
    uint8_t length, const uint8_t *value, uint16_t *advertising_data_length,
    uint8_t *advertising_data, uint16_t advertising_data_buffer_length
);

_Static_assert(sizeof(struct open_cfw_cordio_dm_message_header) == 4U,
    "G2 DM message-header ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_connection_complete_event,
    handle) == 6U, "G2 enhanced connection-complete handle offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_connection_complete_event,
    peer_address) == 10U, "G2 enhanced connection-complete peer offset");
_Static_assert(sizeof(struct open_cfw_cordio_dm_connection_complete_event) == 36U,
    "G2 enhanced connection-complete ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_adv_control_block,
    interval_minimum) == 16U, "G2 DM advertising interval offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_adv_control_block,
    advertising_type) == 24U, "G2 DM advertising type offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_adv_control_block,
    peer_address_type) == 49U, "G2 DM advertising peer-type offset");
_Static_assert(sizeof(struct open_cfw_cordio_dm_adv_control_block) == 52U,
    "G2 DM advertising control-block ABI");
_Static_assert(offsetof(struct open_cfw_cordio_dm_main_control_block,
    handler_id) == 12U, "G2 DM handler offset");
_Static_assert(offsetof(struct open_cfw_cordio_dm_main_control_block,
    advertising_filter_policy) == 17U, "G2 DM advertising-filter offset");
_Static_assert(sizeof(struct open_cfw_cordio_dm_main_control_block) == 24U,
    "G2 DM main control-block ABI");

#endif
