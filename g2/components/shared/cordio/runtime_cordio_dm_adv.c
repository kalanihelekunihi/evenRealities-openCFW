/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_dm_adv.h"

#if !defined(OPEN_CFW_DM_ADV_CB_INIT_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_INIT_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_CONN_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_CONFIGURE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_DATA_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_START_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_STOP_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_REMOVE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_CLEAR_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_RANDOM_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_INTERVAL_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_CHANNEL_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_ADDRESS_TYPE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_ELEMENT_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_SET_NAME_ONLY)
#define OPEN_CFW_DM_ADV_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_DM_ADV_PRODUCTION
#define OPEN_CFW_DM_ADV_CONTROL \
    (*(struct open_cfw_cordio_dm_adv_control_block *)0x20073394U)
#define OPEN_CFW_DM_MAIN_CONTROL \
    (*(struct open_cfw_cordio_dm_main_control_block *)0x20073B78U)
#else
#define OPEN_CFW_DM_ADV_CONTROL open_cfw_cordio_dm_adv_control_block
#define OPEN_CFW_DM_MAIN_CONTROL open_cfw_cordio_dm_main_control_block
#endif

struct open_cfw_dm_adv_configure_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t advertising_handle;
    uint8_t advertising_type;
    uint8_t peer_address_type;
    uint8_t peer_address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
    uint8_t scan_request_notification_enabled;
};

struct open_cfw_dm_adv_set_data_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t advertising_handle;
    uint8_t operation;
    uint8_t location;
    uint8_t length;
    uint8_t data[];
};

struct open_cfw_dm_adv_start_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t number_of_sets;
    uint8_t advertising_handle[OPEN_CFW_DM_ADV_SETS];
    uint16_t duration[OPEN_CFW_DM_ADV_SETS];
    uint8_t maximum_extended_events[OPEN_CFW_DM_ADV_SETS];
};

struct open_cfw_dm_adv_stop_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t number_of_sets;
    uint8_t advertising_handle[OPEN_CFW_DM_ADV_SETS];
};

struct open_cfw_dm_adv_remove_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t advertising_handle;
};

struct open_cfw_dm_adv_random_address_message {
    struct open_cfw_cordio_dm_message_header header;
    uint8_t advertising_handle;
    uint8_t address[OPEN_CFW_DM_ADV_ADDRESS_BYTES];
};

static __attribute__((unused)) void open_cfw_dm_adv_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length
)
{
    uint16_t index;
    for (index = 0U; index < length; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((unused)) void open_cfw_dm_adv_move_left(
    uint8_t *destination, const uint8_t *source, uint16_t length
)
{
    open_cfw_dm_adv_copy(destination, source, length);
}

static __attribute__((unused)) uint8_t open_cfw_dm_adv_data_is_valid(
    const uint8_t *data, uint16_t length
)
{
    uint16_t offset = 0U;
    while (offset < length) {
        uint16_t element = data[offset];
        if (element == 0U || element > (uint16_t)(length - offset - 1U)) {
            return 0U;
        }
        offset = (uint16_t)(offset + element + 1U);
    }
    return (uint8_t)(offset == length);
}

static __attribute__((unused)) uint8_t *open_cfw_dm_adv_find(
    uint8_t type, uint16_t length, uint8_t *data
)
{
    uint16_t offset = 0U;
    while (offset < length) {
        if (data[offset + 1U] == type) {
            return data + offset;
        }
        offset = (uint16_t)(offset + data[offset] + 1U);
    }
    return NULL;
}

static __attribute__((unused)) void open_cfw_dm_adv_remove_element(
    uint8_t *element, uint16_t *data_length, uint8_t *data
)
{
    uint16_t total = (uint16_t)element[0] + 1U;
    uint16_t offset = (uint16_t)(element - data);
    uint16_t remaining = (uint16_t)(*data_length - offset - total);
    open_cfw_dm_adv_move_left(element, element + total, remaining);
    *data_length = (uint16_t)(*data_length - total);
}

static __attribute__((unused)) uint8_t open_cfw_dm_adv_handle_valid(
    uint8_t advertising_handle
)
{
    return (uint8_t)(advertising_handle < OPEN_CFW_DM_ADV_SETS);
}

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || defined(OPEN_CFW_DM_ADV_CB_INIT_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_control_block_initialize(uint8_t advertising_handle)
{
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)) {
        return;
    }
    OPEN_CFW_DM_ADV_CONTROL.advertising_type[advertising_handle] =
        OPEN_CFW_DM_ADV_NONE;
    OPEN_CFW_DM_ADV_CONTROL.interval_minimum[advertising_handle] =
        OPEN_CFW_DM_ADV_SLOW_INTERVAL_MINIMUM;
    OPEN_CFW_DM_ADV_CONTROL.interval_maximum[advertising_handle] =
        OPEN_CFW_DM_ADV_SLOW_INTERVAL_MAXIMUM;
    OPEN_CFW_DM_ADV_CONTROL.channel_map[advertising_handle] =
        OPEN_CFW_DM_ADV_CHANNEL_ALL;
    OPEN_CFW_DM_MAIN_CONTROL.advertising_filter_policy[advertising_handle] =
        OPEN_CFW_DM_ADV_FILTER_NONE;
    OPEN_CFW_DM_ADV_CONTROL.advertising_state[advertising_handle] =
        OPEN_CFW_DM_ADV_STATE_IDLE;
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || defined(OPEN_CFW_DM_ADV_INIT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_initialize(void)
{
    uint8_t advertising_handle;
    for (advertising_handle = 0U;
         advertising_handle < OPEN_CFW_DM_ADV_SETS;
         ++advertising_handle) {
        open_cfw_cordio_dm_adv_control_block_initialize(advertising_handle);
    }
    OPEN_CFW_DM_ADV_CONTROL.advertising_timer[12] =
        OPEN_CFW_DM_MAIN_CONTROL.handler_id;
    OPEN_CFW_DM_MAIN_CONTROL.advertising_address_type =
        OPEN_CFW_DM_ADV_ADDRESS_PUBLIC;
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_CONN_COMPLETE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_generate_connection_complete(
    uint8_t advertising_handle, uint8_t status
)
{
    struct open_cfw_cordio_dm_connection_complete_event event;
    uint8_t *bytes = (uint8_t *)&event;
    uint16_t index;
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)) {
        return;
    }
    for (index = 0U; index < sizeof(event); ++index) {
        bytes[index] = 0U;
    }
    event.header.event = OPEN_CFW_HCI_ENHANCED_CONNECTION_COMPLETE_EVENT;
    event.header.status = status;
    event.status = status;
    event.role = OPEN_CFW_DM_ROLE_SLAVE;
    event.address_type =
        OPEN_CFW_DM_ADV_CONTROL.peer_address_type[advertising_handle];
    open_cfw_dm_adv_copy(
        event.peer_address,
        OPEN_CFW_DM_ADV_CONTROL.peer_address[advertising_handle],
        OPEN_CFW_DM_ADV_ADDRESS_BYTES
    );
    open_cfw_cordio_dm_device_pass_hci_event_to_connection(&event);
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_CONFIGURE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_configure(
    uint8_t advertising_handle, uint8_t advertising_type,
    uint8_t peer_address_type, const uint8_t *peer_address
)
{
    struct open_cfw_dm_adv_configure_message *message;
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)
            || peer_address == NULL) {
        return;
    }
    message = open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->header.parameter = 0U;
        message->header.event = OPEN_CFW_DM_ADV_MESSAGE_CONFIGURE;
        message->header.status = 0U;
        message->advertising_handle = advertising_handle;
        message->advertising_type = advertising_type;
        message->peer_address_type = peer_address_type;
        open_cfw_dm_adv_copy(
            message->peer_address, peer_address, OPEN_CFW_DM_ADV_ADDRESS_BYTES
        );
        message->scan_request_notification_enabled = 0U;
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_DATA_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_set_data(
    uint8_t advertising_handle, uint8_t operation, uint8_t location,
    uint8_t length, const uint8_t *data
)
{
    struct open_cfw_dm_adv_set_data_message *message;
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)
            || (location != OPEN_CFW_DM_ADV_DATA_LOCATION_ADVERTISING
                && location != OPEN_CFW_DM_ADV_DATA_LOCATION_SCAN)
            || length > OPEN_CFW_DM_ADV_MAXIMUM_DATA_LENGTH
            || (length != 0U && data == NULL)) {
        return;
    }
    message = open_cfw_cordio_wsf_message_allocate_candidate(
        (uint16_t)(sizeof(*message) + length)
    );
    if (message != NULL) {
        message->header.parameter = 0U;
        message->header.event = OPEN_CFW_DM_ADV_MESSAGE_SET_DATA;
        message->header.status = 0U;
        message->advertising_handle = advertising_handle;
        message->operation = operation;
        message->location = location;
        message->length = length;
        if (length != 0U) {
            open_cfw_dm_adv_copy(message->data, data, length);
        }
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || defined(OPEN_CFW_DM_ADV_START_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_start(
    uint8_t number_of_sets, const uint8_t *advertising_handles,
    const uint16_t *durations, const uint8_t *maximum_extended_events
)
{
    struct open_cfw_dm_adv_start_message *message;
    uint8_t index;
    if (number_of_sets > OPEN_CFW_DM_ADV_SETS
            || (number_of_sets != 0U
                && (advertising_handles == NULL || durations == NULL
                    || maximum_extended_events == NULL))) {
        return;
    }
    for (index = 0U; index < number_of_sets; ++index) {
        if (!open_cfw_dm_adv_handle_valid(advertising_handles[index])) {
            return;
        }
    }
    message = open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->header.parameter = 0U;
        message->header.event = OPEN_CFW_DM_ADV_MESSAGE_START;
        message->header.status = 0U;
        message->number_of_sets = number_of_sets;
        for (index = 0U; index < OPEN_CFW_DM_ADV_SETS; ++index) {
            message->advertising_handle[index] = 0U;
            message->duration[index] = 0U;
            message->maximum_extended_events[index] = 0U;
        }
        for (index = 0U; index < number_of_sets; ++index) {
            message->advertising_handle[index] = advertising_handles[index];
            message->duration[index] = durations[index];
            message->maximum_extended_events[index] =
                maximum_extended_events[index];
        }
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || defined(OPEN_CFW_DM_ADV_STOP_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_stop(
    uint8_t number_of_sets, const uint8_t *advertising_handles
)
{
    struct open_cfw_dm_adv_stop_message *message;
    uint8_t index;
    if (number_of_sets > OPEN_CFW_DM_ADV_SETS
            || (number_of_sets != 0U && advertising_handles == NULL)) {
        return;
    }
    for (index = 0U; index < number_of_sets; ++index) {
        if (!open_cfw_dm_adv_handle_valid(advertising_handles[index])) {
            return;
        }
    }
    message = open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->header.parameter = 0U;
        message->header.event = OPEN_CFW_DM_ADV_MESSAGE_STOP;
        message->header.status = 0U;
        message->number_of_sets = number_of_sets;
        for (index = 0U; index < OPEN_CFW_DM_ADV_SETS; ++index) {
            message->advertising_handle[index] = 0U;
        }
        for (index = 0U; index < number_of_sets; ++index) {
            message->advertising_handle[index] = advertising_handles[index];
        }
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || defined(OPEN_CFW_DM_ADV_REMOVE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_remove_set(uint8_t advertising_handle)
{
    struct open_cfw_dm_adv_remove_message *message;
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)) {
        return;
    }
    message = open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->header.parameter = 0U;
        message->header.event = OPEN_CFW_DM_ADV_MESSAGE_REMOVE;
        message->header.status = 0U;
        message->advertising_handle = advertising_handle;
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || defined(OPEN_CFW_DM_ADV_CLEAR_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_clear_sets(void)
{
    struct open_cfw_cordio_dm_message_header *message =
        open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->parameter = 0U;
        message->event = OPEN_CFW_DM_ADV_MESSAGE_CLEAR;
        message->status = 0U;
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_RANDOM_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_set_random_address(
    uint8_t advertising_handle, const uint8_t *address
)
{
    struct open_cfw_dm_adv_random_address_message *message;
    if (!open_cfw_dm_adv_handle_valid(advertising_handle) || address == NULL) {
        return;
    }
    message = open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->header.parameter = 0U;
        message->header.event = OPEN_CFW_DM_ADV_MESSAGE_SET_RANDOM_ADDRESS;
        message->header.status = 0U;
        message->advertising_handle = advertising_handle;
        open_cfw_dm_adv_copy(
            message->address, address, OPEN_CFW_DM_ADV_ADDRESS_BYTES
        );
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_MAIN_CONTROL.handler_id, message
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_INTERVAL_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_set_interval(
    uint8_t advertising_handle, uint16_t interval_minimum,
    uint16_t interval_maximum
)
{
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)
            || interval_minimum > interval_maximum) {
        return;
    }
    open_cfw_cordio_wsf_task_lock_candidate();
    OPEN_CFW_DM_ADV_CONTROL.interval_minimum[advertising_handle] =
        interval_minimum;
    OPEN_CFW_DM_ADV_CONTROL.interval_maximum[advertising_handle] =
        interval_maximum;
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_CHANNEL_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_set_channel_map(
    uint8_t advertising_handle, uint8_t channel_map
)
{
    if (!open_cfw_dm_adv_handle_valid(advertising_handle)
            || channel_map == 0U
            || (channel_map & (uint8_t)~OPEN_CFW_DM_ADV_CHANNEL_ALL) != 0U) {
        return;
    }
    open_cfw_cordio_wsf_task_lock_candidate();
    OPEN_CFW_DM_ADV_CONTROL.channel_map[advertising_handle] = channel_map;
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_ADDRESS_TYPE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_set_address_type(uint8_t address_type)
{
    open_cfw_cordio_wsf_task_lock_candidate();
    OPEN_CFW_DM_MAIN_CONTROL.advertising_address_type = address_type;
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_ELEMENT_ONLY)
__attribute__((used, noinline)) uint8_t open_cfw_cordio_dm_adv_set_element(
    uint8_t advertising_data_type, uint8_t length, const uint8_t *value,
    uint16_t *advertising_data_length, uint8_t *advertising_data,
    uint16_t advertising_data_buffer_length
)
{
    uint8_t *element;
    uint32_t new_length;
    if (advertising_data_length == NULL || advertising_data == NULL
            || length > OPEN_CFW_DM_ADV_MAXIMUM_ELEMENT_VALUE_LENGTH
            || (length != 0U && value == NULL)
            || *advertising_data_length > advertising_data_buffer_length
            || !open_cfw_dm_adv_data_is_valid(
                advertising_data, *advertising_data_length)) {
        return 0U;
    }
    element = open_cfw_dm_adv_find(
        advertising_data_type, *advertising_data_length, advertising_data
    );
    if (element != NULL && element[0] == (uint8_t)(length + 1U)) {
        open_cfw_dm_adv_copy(element + 2U, value, length);
        return 1U;
    }
    if (element != NULL) {
        new_length = (uint32_t)*advertising_data_length
            - ((uint32_t)element[0] + 1U) + length + 2U;
        if (new_length > advertising_data_buffer_length) {
            return 0U;
        }
        open_cfw_dm_adv_remove_element(
            element, advertising_data_length, advertising_data
        );
    }
    new_length = (uint32_t)*advertising_data_length + length + 2U;
    if (new_length > advertising_data_buffer_length) {
        return 0U;
    }
    element = advertising_data + *advertising_data_length;
    element[0] = (uint8_t)(length + 1U);
    element[1] = advertising_data_type;
    open_cfw_dm_adv_copy(element + 2U, value, length);
    *advertising_data_length = (uint16_t)new_length;
    return 1U;
}
#endif

#if defined(OPEN_CFW_DM_ADV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_SET_NAME_ONLY)
__attribute__((used, noinline)) uint8_t open_cfw_cordio_dm_adv_set_name(
    uint8_t length, const uint8_t *value, uint16_t *advertising_data_length,
    uint8_t *advertising_data, uint16_t advertising_data_buffer_length
)
{
    uint8_t *element;
    uint16_t available;
    uint8_t type = OPEN_CFW_DM_ADV_TYPE_LOCAL_NAME;
    if (advertising_data_length == NULL || advertising_data == NULL
            || length > OPEN_CFW_DM_ADV_MAXIMUM_ELEMENT_VALUE_LENGTH
            || (length != 0U && value == NULL)
            || *advertising_data_length > advertising_data_buffer_length
            || !open_cfw_dm_adv_data_is_valid(
                advertising_data, *advertising_data_length)) {
        return 0U;
    }
    element = open_cfw_dm_adv_find(
        OPEN_CFW_DM_ADV_TYPE_LOCAL_NAME,
        *advertising_data_length, advertising_data
    );
    if (element == NULL) {
        element = open_cfw_dm_adv_find(
            OPEN_CFW_DM_ADV_TYPE_SHORT_NAME,
            *advertising_data_length, advertising_data
        );
    }
    if (element != NULL) {
        open_cfw_dm_adv_remove_element(
            element, advertising_data_length, advertising_data
        );
    }
    available = (uint16_t)(
        advertising_data_buffer_length - *advertising_data_length
    );
    if (available < 2U) {
        return 0U;
    }
    if ((uint16_t)(length + 2U) > available) {
        length = (uint8_t)(available - 2U);
        type = OPEN_CFW_DM_ADV_TYPE_SHORT_NAME;
    }
    element = advertising_data + *advertising_data_length;
    element[0] = (uint8_t)(length + 1U);
    element[1] = type;
    open_cfw_dm_adv_copy(element + 2U, value, length);
    *advertising_data_length = (uint16_t)(
        *advertising_data_length + length + 2U
    );
    return 1U;
}
#endif

_Static_assert(sizeof(struct open_cfw_dm_adv_configure_message) == 14U,
    "G2 DM configure-message ABI");
_Static_assert(offsetof(struct open_cfw_dm_adv_set_data_message, data) == 8U,
    "G2 Ambiq inline advertising-data ABI");
_Static_assert(sizeof(struct open_cfw_dm_adv_start_message) == 14U,
    "G2 DM start-message ABI");
_Static_assert(sizeof(struct open_cfw_dm_adv_stop_message) == 8U,
    "G2 DM stop-message ABI");
_Static_assert(sizeof(struct open_cfw_dm_adv_remove_message) == 6U,
    "G2 DM remove-message ABI");
_Static_assert(sizeof(struct open_cfw_dm_adv_random_address_message) == 12U,
    "G2 DM random-address-message ABI");
