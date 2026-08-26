/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_dm_adv_leg.h"

#if !defined(OPEN_CFW_DM_ADV_LEG_CONFIG_PARAMETERS_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_CONFIGURE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_SET_DATA_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_START_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_STOP_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_REMOVE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_CLEAR_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_SET_RANDOM_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_ACTION_TIMEOUT_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_RESET_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_HCI_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_MESSAGE_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_START_DIRECTED_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_STOP_DIRECTED_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_CONNECTED_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_CONNECT_FAILED_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_DM_ADV_LEG_MODE_ONLY)
#define OPEN_CFW_DM_ADV_LEG_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_DM_ADV_LEG_PRODUCTION
#define OPEN_CFW_DM_ADV_LEG_CONTROL \
    (*(struct open_cfw_cordio_dm_adv_control_block *)0x20073394U)
#define OPEN_CFW_DM_ADV_LEG_MAIN \
    (*(struct open_cfw_cordio_dm_main_control_block *)0x20073B78U)
#define OPEN_CFW_DM_ADV_LEG_TYPE (*(uint8_t *)0x20074FB3U)
#define OPEN_CFW_DM_ADV_LEG_REGISTERED_INTERFACE \
    (*(const struct open_cfw_cordio_dm_adv_legacy_function_interface **) \
        0x20000694U)
#define OPEN_CFW_DM_ADV_LEG_RANDOM_ADDRESS_CALLBACK \
    (*(uintptr_t *)0x200744F4U)
#else
#define OPEN_CFW_DM_ADV_LEG_CONTROL open_cfw_cordio_dm_adv_control_block
#define OPEN_CFW_DM_ADV_LEG_MAIN open_cfw_cordio_dm_main_control_block
#define OPEN_CFW_DM_ADV_LEG_TYPE open_cfw_cordio_dm_adv_legacy_type
#define OPEN_CFW_DM_ADV_LEG_REGISTERED_INTERFACE \
    open_cfw_cordio_dm_adv_registered_interface
#define OPEN_CFW_DM_ADV_LEG_RANDOM_ADDRESS_CALLBACK \
    open_cfw_cordio_dm_dev_adv_set_random_address_callback
#endif

static __attribute__((unused)) struct open_cfw_cordio_dm_adv_legacy_timer
    *open_cfw_dm_adv_legacy_timer(void)
{
    return (struct open_cfw_cordio_dm_adv_legacy_timer *)(void *)
        OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_timer;
}

static __attribute__((unused)) void open_cfw_dm_adv_legacy_copy_address(
    uint8_t *destination, const uint8_t *source
)
{
    uint8_t index;
    for (index = 0U; index < OPEN_CFW_DM_ADV_ADDRESS_BYTES; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((unused)) uint8_t open_cfw_dm_adv_legacy_is_directed(
    uint8_t advertising_type
)
{
    return (uint8_t)(
        advertising_type == OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED
        || advertising_type ==
            OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED_LOW_DUTY
    );
}

static __attribute__((unused)) void open_cfw_dm_adv_legacy_callback(
    void *event
)
{
#ifdef OPEN_CFW_DM_ADV_LEG_PRODUCTION
    uintptr_t callback = OPEN_CFW_DM_ADV_LEG_MAIN.callback;
    if (callback != 0U) {
        ((void (*)(void *))callback)(event);
    }
#else
    open_cfw_cordio_dm_adv_legacy_application_callback(event);
#endif
}

#if !defined(OPEN_CFW_DM_ADV_LEG_PRODUCTION) && \
    (defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_INITIALIZE_ONLY) || \
    defined(OPEN_CFW_DM_ADV_LEG_MODE_ONLY))
static const struct open_cfw_cordio_dm_adv_legacy_function_interface
    open_cfw_dm_adv_legacy_interface = {
        open_cfw_cordio_dm_adv_legacy_reset,
        open_cfw_cordio_dm_adv_legacy_hci_handler,
        open_cfw_cordio_dm_adv_legacy_message_handler,
    };
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_CONFIG_PARAMETERS_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_configure_parameters(
    uint8_t advertising_type, uint8_t peer_address_type,
    const uint8_t *peer_address
)
{
    if (peer_address == NULL) {
        return;
    }
    open_cfw_cordio_hci_set_legacy_advertising_parameters(
        OPEN_CFW_DM_ADV_LEG_CONTROL.interval_minimum[0],
        OPEN_CFW_DM_ADV_LEG_CONTROL.interval_maximum[0],
        advertising_type,
        open_cfw_cordio_dm_legacy_link_layer_address_type(
            OPEN_CFW_DM_ADV_LEG_MAIN.advertising_address_type
        ),
        peer_address_type,
        peer_address,
        OPEN_CFW_DM_ADV_LEG_CONTROL.channel_map[0],
        OPEN_CFW_DM_ADV_LEG_MAIN.advertising_filter_policy[0]
    );
    OPEN_CFW_DM_ADV_LEG_TYPE = advertising_type;
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_CONFIGURE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_configure(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    if (message == NULL || message->configure.advertising_handle != 0U
            || OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0]
                != OPEN_CFW_DM_ADV_STATE_IDLE
            || open_cfw_dm_adv_legacy_is_directed(
                OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0])) {
        return;
    }
    open_cfw_cordio_dm_adv_legacy_configure_parameters(
        message->configure.advertising_type,
        message->configure.peer_address_type,
        message->configure.peer_address
    );
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_SET_DATA_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_set_data(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    if (message == NULL || message->set_data.advertising_handle != 0U
            || message->set_data.length > OPEN_CFW_DM_ADV_LEG_DATA_MAXIMUM
            || message->set_data.location >
                OPEN_CFW_DM_ADV_DATA_LOCATION_SCAN
            || OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0]
                != OPEN_CFW_DM_ADV_STATE_IDLE) {
        return;
    }
    if (message->set_data.location ==
            OPEN_CFW_DM_ADV_DATA_LOCATION_ADVERTISING) {
        open_cfw_cordio_hci_set_legacy_advertising_data(
            message->set_data.length, message->set_data.data
        );
    } else {
        open_cfw_cordio_hci_set_legacy_scan_response_data(
            message->set_data.length, message->set_data.data
        );
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_START_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_start(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    if (message == NULL || message->start.number_of_sets == 0U
            || message->start.advertising_handle[0] != 0U
            || OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0]
                != OPEN_CFW_DM_ADV_STATE_IDLE
            || open_cfw_dm_adv_legacy_is_directed(
                OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0])) {
        return;
    }
    OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
        OPEN_CFW_DM_ADV_LEG_STATE_STARTING;
    OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_duration[0] =
        message->start.duration[0];
    open_cfw_cordio_hci_set_legacy_advertising_enable(1U);
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_STOP_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_stop(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    (void)message;
    if (OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0]
            == OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING
            && !open_cfw_dm_adv_legacy_is_directed(
                OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0])) {
        OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
            OPEN_CFW_DM_ADV_LEG_STATE_STOPPING;
        open_cfw_cordio_hci_set_legacy_advertising_enable(0U);
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_REMOVE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_remove_set(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    (void)message;
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_CLEAR_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_clear_sets(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    (void)message;
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_SET_RANDOM_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_set_random_address(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    (void)message;
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_ACTION_TIMEOUT_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_action_timeout(
    union open_cfw_cordio_dm_adv_legacy_message *message
)
{
    (void)message;
    if (OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0]
            == OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING) {
        OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
            OPEN_CFW_DM_ADV_LEG_STATE_STOPPING;
        open_cfw_cordio_hci_set_legacy_advertising_enable(0U);
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_RESET_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_adv_legacy_reset(void)
{
    struct open_cfw_cordio_dm_message_header stop_event = {0U, 0U, 0U};
    uint8_t state = OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0];
    if (state == OPEN_CFW_DM_ADV_LEG_STATE_STOPPING
            || (state == OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING
                && OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0]
                    != OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED)) {
        open_cfw_cordio_wsf_timer_stop(open_cfw_dm_adv_legacy_timer());
        stop_event.event = OPEN_CFW_DM_ADV_LEG_STOP_INDICATION;
        open_cfw_dm_adv_legacy_callback(&stop_event);
    }
    open_cfw_cordio_dm_adv_initialize();
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_HCI_HANDLER_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_hci_handler(
    struct open_cfw_cordio_dm_message_header *event
)
{
    uint8_t callback_event = 0U;
    uint8_t state;
    if (event == NULL
            || event->event != OPEN_CFW_DM_ADV_LEG_HCI_ADV_ENABLE_COMPLETE) {
        return;
    }
    state = OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0];
    if (state == OPEN_CFW_DM_ADV_LEG_STATE_STARTING
            || state == OPEN_CFW_DM_ADV_LEG_STATE_STARTING_DIRECTED) {
        if (event->status == 0U) {
            if (state == OPEN_CFW_DM_ADV_LEG_STATE_STARTING) {
                if (OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_duration[0] > 0U) {
                    open_cfw_dm_adv_legacy_timer()->message.event =
                        OPEN_CFW_DM_ADV_LEG_MESSAGE_TIMEOUT;
                    open_cfw_cordio_wsf_timer_start_ms(
                        open_cfw_dm_adv_legacy_timer(),
                        OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_duration[0]
                    );
                }
                if (OPEN_CFW_DM_ADV_LEG_TYPE !=
                        OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED_LOW_DUTY) {
                    callback_event = OPEN_CFW_DM_ADV_LEG_START_INDICATION;
                }
            }
            open_cfw_cordio_dm_device_pass_private_event(
                OPEN_CFW_DM_ADV_LEG_DEVICE_RPA_START,
                OPEN_CFW_DM_ADV_LEG_START_INDICATION, 0U, 0U
            );
            OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0] =
                OPEN_CFW_DM_ADV_LEG_TYPE;
            OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
                OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING;
        } else {
            OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
                OPEN_CFW_DM_ADV_STATE_IDLE;
        }
    } else if (state == OPEN_CFW_DM_ADV_LEG_STATE_STOPPING
            || state == OPEN_CFW_DM_ADV_LEG_STATE_STOPPING_DIRECTED) {
        if (event->status == 0U) {
            if (state == OPEN_CFW_DM_ADV_LEG_STATE_STOPPING) {
                open_cfw_cordio_wsf_timer_stop(open_cfw_dm_adv_legacy_timer());
                callback_event =
                    (OPEN_CFW_DM_ADV_LEG_TYPE ==
                        OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED_LOW_DUTY)
                    ? OPEN_CFW_HCI_ENHANCED_CONNECTION_COMPLETE_EVENT
                    : OPEN_CFW_DM_ADV_LEG_STOP_INDICATION;
            }
            open_cfw_cordio_dm_device_pass_private_event(
                OPEN_CFW_DM_ADV_LEG_DEVICE_RPA_STOP,
                OPEN_CFW_DM_ADV_LEG_STOP_INDICATION, 0U, 0U
            );
            OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0] =
                OPEN_CFW_DM_ADV_NONE;
            OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
                OPEN_CFW_DM_ADV_STATE_IDLE;
        } else {
            OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
                OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING;
        }
    }
    if (callback_event == OPEN_CFW_HCI_ENHANCED_CONNECTION_COMPLETE_EVENT) {
        open_cfw_cordio_dm_adv_generate_connection_complete(
            0U, OPEN_CFW_DM_ADV_LEG_HCI_ADVERTISING_TIMEOUT
        );
    } else if (callback_event != 0U) {
        event->event = callback_event;
        open_cfw_dm_adv_legacy_callback(event);
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_MESSAGE_HANDLER_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_message_handler(
    struct open_cfw_cordio_dm_message_header *message
)
{
    union open_cfw_cordio_dm_adv_legacy_message *typed =
        (union open_cfw_cordio_dm_adv_legacy_message *)(void *)message;
    if (message == NULL) {
        return;
    }
    switch (message->event & 7U) {
    case 0U: open_cfw_cordio_dm_adv_legacy_action_configure(typed); break;
    case 1U: open_cfw_cordio_dm_adv_legacy_action_set_data(typed); break;
    case 2U: open_cfw_cordio_dm_adv_legacy_action_start(typed); break;
    case 3U: open_cfw_cordio_dm_adv_legacy_action_stop(typed); break;
    case 4U: open_cfw_cordio_dm_adv_legacy_action_remove_set(typed); break;
    case 5U: open_cfw_cordio_dm_adv_legacy_action_clear_sets(typed); break;
    case 6U:
        open_cfw_cordio_dm_adv_legacy_action_set_random_address(typed);
        break;
    default: open_cfw_cordio_dm_adv_legacy_action_timeout(typed); break;
    }
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_START_DIRECTED_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_start_directed(
    uint8_t advertising_type, uint16_t duration, uint8_t address_type,
    const uint8_t *address
)
{
    if (address == NULL
            || !open_cfw_dm_adv_legacy_is_directed(advertising_type)
            || OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0]
                != OPEN_CFW_DM_ADV_STATE_IDLE) {
        return;
    }
    open_cfw_cordio_hci_set_legacy_advertising_enable(1U);
    OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
        (advertising_type == OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED)
        ? OPEN_CFW_DM_ADV_LEG_STATE_STARTING_DIRECTED
        : OPEN_CFW_DM_ADV_LEG_STATE_STARTING;
    OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_duration[0] = duration;
    open_cfw_dm_adv_legacy_copy_address(
        OPEN_CFW_DM_ADV_LEG_CONTROL.peer_address[0], address
    );
    OPEN_CFW_DM_ADV_LEG_CONTROL.peer_address_type[0] = address_type;
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_STOP_DIRECTED_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_stop_directed(void)
{
    uint8_t state = OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0];
    if (state == OPEN_CFW_DM_ADV_LEG_STATE_ADVERTISING
            || state == OPEN_CFW_DM_ADV_LEG_STATE_STARTING
            || state == OPEN_CFW_DM_ADV_LEG_STATE_STARTING_DIRECTED) {
        OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
            (OPEN_CFW_DM_ADV_LEG_TYPE ==
                OPEN_CFW_DM_ADV_LEG_CONNECTABLE_DIRECTED)
            ? OPEN_CFW_DM_ADV_LEG_STATE_STOPPING_DIRECTED
            : OPEN_CFW_DM_ADV_LEG_STATE_STOPPING;
        open_cfw_cordio_hci_set_legacy_advertising_enable(0U);
    }
}
#endif

static __attribute__((unused)) void open_cfw_dm_adv_legacy_finish_directed(void)
{
    open_cfw_cordio_wsf_timer_stop(open_cfw_dm_adv_legacy_timer());
    open_cfw_cordio_dm_device_pass_private_event(
        OPEN_CFW_DM_ADV_LEG_DEVICE_RPA_STOP,
        OPEN_CFW_DM_ADV_LEG_STOP_INDICATION, 0U, 0U
    );
    OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_type[0] = OPEN_CFW_DM_ADV_NONE;
    OPEN_CFW_DM_ADV_LEG_CONTROL.advertising_state[0] =
        OPEN_CFW_DM_ADV_STATE_IDLE;
}

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_CONNECTED_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_connected(void)
{
    open_cfw_dm_adv_legacy_finish_directed();
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_CONNECT_FAILED_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_connect_failed(void)
{
    open_cfw_dm_adv_legacy_finish_directed();
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_INITIALIZE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_adv_legacy_initialize(void)
{
    open_cfw_cordio_wsf_task_lock_candidate();
#ifdef OPEN_CFW_DM_ADV_LEG_PRODUCTION
    OPEN_CFW_DM_ADV_LEG_REGISTERED_INTERFACE =
        (const struct open_cfw_cordio_dm_adv_legacy_function_interface *)
            0x0078A808U;
#else
    OPEN_CFW_DM_ADV_LEG_REGISTERED_INTERFACE =
        &open_cfw_dm_adv_legacy_interface;
#endif
    open_cfw_cordio_dm_adv_initialize();
    OPEN_CFW_DM_ADV_LEG_RANDOM_ADDRESS_CALLBACK = 0U;
    open_cfw_cordio_wsf_task_unlock_candidate();
}
#endif

#if defined(OPEN_CFW_DM_ADV_LEG_BUILD_ALL) || \
    defined(OPEN_CFW_DM_ADV_LEG_MODE_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_adv_mode_legacy(void)
{
#ifdef OPEN_CFW_DM_ADV_LEG_PRODUCTION
    return (uint8_t)(OPEN_CFW_DM_ADV_LEG_REGISTERED_INTERFACE
        == (const struct open_cfw_cordio_dm_adv_legacy_function_interface *)
            0x0078A808U);
#else
    return (uint8_t)(OPEN_CFW_DM_ADV_LEG_REGISTERED_INTERFACE
        == &open_cfw_dm_adv_legacy_interface);
#endif
}
#endif
