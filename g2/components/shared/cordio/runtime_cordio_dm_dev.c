/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_dm_dev.h"

#if !defined(OPEN_CFW_DM_DEV_ACTION_RESET_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_HCI_RESET_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_HCI_VENDOR_COMMAND_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_HCI_VENDOR_EVENT_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_HCI_HARDWARE_ERROR_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_HCI_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_MESSAGE_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_PASS_PRIVACY_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_PASS_CTE_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_RESET_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_SET_RANDOM_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_VENDOR_INIT_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_WHITE_LIST_ADD_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_WHITE_LIST_REMOVE_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_WHITE_LIST_CLEAR_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_FILTER_INTERNAL_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_FILTER_ONLY) && \
    !defined(OPEN_CFW_DM_DEV_FILTER_EXTENDED_ONLY)
#define OPEN_CFW_DM_DEV_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_DM_DEV_PRODUCTION
#define OPEN_CFW_DM_DEV_LOCAL_ADDRESS ((uint8_t *)0x20073B78U)
#define OPEN_CFW_DM_DEV_CALLBACK (*(uintptr_t *)0x20073B80U)
#define OPEN_CFW_DM_DEV_HANDLER_ID (*(uint8_t *)0x20073B84U)
#define OPEN_CFW_DM_DEV_RESETTING (*(uint8_t *)0x20073B88U)
#define OPEN_CFW_DM_DEV_ADV_FILTER ((uint8_t *)0x20073B89U)
#define OPEN_CFW_DM_DEV_SCAN_FILTER (*(uint8_t *)0x20073B8BU)
#define OPEN_CFW_DM_DEV_INIT_FILTER (*(uint8_t *)0x20073B8CU)
#define OPEN_CFW_DM_DEV_SYNC_OPTIONS (*(uint8_t *)0x20073B8DU)
#define OPEN_CFW_DM_DEV_INTERFACES ((const uintptr_t *)0x20000694U)
#else
#define OPEN_CFW_DM_DEV_LOCAL_ADDRESS \
    open_cfw_cordio_dm_device_main_control.local_address
#define OPEN_CFW_DM_DEV_CALLBACK open_cfw_cordio_dm_device_main_control.callback
#define OPEN_CFW_DM_DEV_HANDLER_ID \
    open_cfw_cordio_dm_device_main_control.handler_id
#define OPEN_CFW_DM_DEV_RESETTING open_cfw_cordio_dm_device_main_control.resetting
#define OPEN_CFW_DM_DEV_ADV_FILTER \
    open_cfw_cordio_dm_device_main_control.advertising_filter_policy
#define OPEN_CFW_DM_DEV_SCAN_FILTER \
    open_cfw_cordio_dm_device_main_control.scanning_filter_policy
#define OPEN_CFW_DM_DEV_INIT_FILTER \
    open_cfw_cordio_dm_device_main_control.initiator_filter_policy
#define OPEN_CFW_DM_DEV_SYNC_OPTIONS \
    open_cfw_cordio_dm_device_main_control.synchronization_options
#define OPEN_CFW_DM_DEV_INTERFACES open_cfw_cordio_dm_device_function_interfaces
#endif

static __attribute__((unused)) void open_cfw_dm_dev_callback(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    uintptr_t callback = OPEN_CFW_DM_DEV_CALLBACK;
    if (callback != (uintptr_t)0U) {
        ((void (*)(void *))callback)(event);
    }
}

static __attribute__((unused)) const struct
open_cfw_cordio_dm_device_function_interface *open_cfw_dm_dev_interface(
    uint8_t component)
{
    uintptr_t address;
    if (component >= OPEN_CFW_DM_DEVICE_COMPONENTS) {
        return NULL;
    }
    address = OPEN_CFW_DM_DEV_INTERFACES[component];
    if (address == (uintptr_t)0U) {
        return NULL;
    }
    return (const struct open_cfw_cordio_dm_device_function_interface *)address;
}

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_ACTION_RESET_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_action_reset(
    struct open_cfw_cordio_dm_device_message_header *message)
{
    uint8_t component;
    (void)message;
    if (OPEN_CFW_DM_DEV_RESETTING != 0U) {
        return;
    }
    OPEN_CFW_DM_DEV_RESETTING = 1U;
    for (component = 0U; component < OPEN_CFW_DM_DEVICE_COMPONENTS;
            ++component) {
        const struct open_cfw_cordio_dm_device_function_interface *interface =
            open_cfw_dm_dev_interface(component);
        if (interface != NULL && interface->reset != NULL) {
            interface->reset();
        }
    }
    open_cfw_cordio_hci_reset_sequence();
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || defined(OPEN_CFW_DM_DEV_HCI_RESET_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_hci_reset_complete(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    if (event == NULL) return;
    OPEN_CFW_DM_DEV_RESETTING = 0U;
    event->event = OPEN_CFW_DM_RESET_COMPLETE;
    open_cfw_dm_dev_callback(event);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_HCI_VENDOR_COMMAND_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_hci_vendor_command_complete(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    if (event == NULL) return;
    event->event = OPEN_CFW_DM_VENDOR_COMMAND_COMPLETE;
    open_cfw_dm_dev_callback(event);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_HCI_VENDOR_EVENT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_hci_vendor_event(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    if (event == NULL) return;
    event->event = OPEN_CFW_DM_VENDOR_EVENT;
    open_cfw_dm_dev_callback(event);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_HCI_HARDWARE_ERROR_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_hci_hardware_error(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    if (event == NULL) return;
    event->event = OPEN_CFW_DM_HARDWARE_ERROR;
    open_cfw_dm_dev_callback(event);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_HCI_HANDLER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_hci_handler(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    if (event == NULL) return;
    switch (event->event) {
    case 0U: open_cfw_cordio_dm_device_hci_reset_complete(event); break;
    case 18U: open_cfw_cordio_dm_device_hci_vendor_command_complete(event); break;
    case 19U: open_cfw_cordio_dm_device_hci_vendor_event(event); break;
    case 20U: open_cfw_cordio_dm_device_hci_hardware_error(event); break;
    default: break;
    }
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_MESSAGE_HANDLER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_message_handler(
    struct open_cfw_cordio_dm_device_message_header *message)
{
    if (message == NULL || (message->event & 0x07U) != 0U) return;
    open_cfw_cordio_dm_device_action_reset(message);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_PASS_PRIVACY_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_pass_event_to_privacy(
    uint8_t event, uint8_t parameter, uint8_t advertising_handle,
    uint8_t connectable)
{
    struct open_cfw_cordio_dm_device_privacy_message message = {0};
    const struct open_cfw_cordio_dm_device_function_interface *interface =
        open_cfw_dm_dev_interface(OPEN_CFW_DM_DEVICE_PRIVACY_COMPONENT);
    message.header.parameter = parameter;
    message.header.event = event;
    message.advertising_handle = advertising_handle;
    message.connectable = (uint8_t)(connectable != 0U);
    if (interface != NULL && interface->message_handler != NULL) {
        interface->message_handler(&message.header);
    }
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || defined(OPEN_CFW_DM_DEV_PASS_CTE_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_pass_event_to_connection_cte(
    uint8_t state, uint8_t connection_id)
{
    struct open_cfw_cordio_dm_device_message_header message = {0};
    const struct open_cfw_cordio_dm_device_function_interface *interface =
        open_cfw_dm_dev_interface(OPEN_CFW_DM_CONNECTION_CTE_COMPONENT);
    message.parameter = connection_id;
    message.event = OPEN_CFW_DM_CONNECTION_CTE_STATE;
    message.status = state;
    if (interface != NULL && interface->message_handler != NULL) {
        interface->message_handler(&message);
    }
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || defined(OPEN_CFW_DM_DEV_RESET_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_reset(void)
{
    struct open_cfw_cordio_dm_device_message_header *message;
    OPEN_CFW_DM_DEV_RESETTING = 0U;
    message = (struct open_cfw_cordio_dm_device_message_header *)
        open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*message));
    if (message != NULL) {
        message->event = OPEN_CFW_DM_DEVICE_RESET_REQUEST;
        open_cfw_cordio_wsf_message_send_candidate(
            OPEN_CFW_DM_DEV_HANDLER_ID, message);
    }
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || defined(OPEN_CFW_DM_DEV_SET_RANDOM_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_set_random_address(const uint8_t *address)
{
    uint8_t index;
    if (address == NULL) return;
    for (index = 0U; index < OPEN_CFW_DM_DEVICE_ADDRESS_BYTES; ++index) {
        OPEN_CFW_DM_DEV_LOCAL_ADDRESS[index] = address[index];
    }
    open_cfw_cordio_hci_set_random_address(address);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || defined(OPEN_CFW_DM_DEV_VENDOR_INIT_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_dm_device_vendor_initialize(uint8_t parameter)
{
    (void)parameter;
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_WHITE_LIST_ADD_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_white_list_add(
    uint8_t address_type, const uint8_t *address)
{
    if (address != NULL) open_cfw_cordio_hci_white_list_add(address_type, address);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_WHITE_LIST_REMOVE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_white_list_remove(
    uint8_t address_type, const uint8_t *address)
{
    if (address != NULL) open_cfw_cordio_hci_white_list_remove(address_type, address);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_WHITE_LIST_CLEAR_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_device_white_list_clear(void)
{
    open_cfw_cordio_hci_white_list_clear();
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_FILTER_INTERNAL_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_device_set_filter_policy_internal(
    uint8_t advertising_handle, uint8_t mode, uint8_t policy)
{
    switch (mode) {
    case 0U:
        if (advertising_handle < OPEN_CFW_DM_DEVICE_ADV_SETS && policy <= 3U) {
            OPEN_CFW_DM_DEV_ADV_FILTER[advertising_handle] = policy; return 1U;
        }
        break;
    case 1U:
        if (policy <= 3U) { OPEN_CFW_DM_DEV_SCAN_FILTER = policy; return 1U; }
        break;
    case 2U:
        if (policy <= 1U) { OPEN_CFW_DM_DEV_INIT_FILTER = policy; return 1U; }
        break;
    case 3U:
        if (policy <= 1U) {
            OPEN_CFW_DM_DEV_SYNC_OPTIONS = (uint8_t)(
                (OPEN_CFW_DM_DEV_SYNC_OPTIONS & (uint8_t)~1U) | policy);
            return 1U;
        }
        break;
    default: break;
    }
    return 0U;
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || defined(OPEN_CFW_DM_DEV_FILTER_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_device_set_filter_policy(uint8_t mode, uint8_t policy)
{
    return open_cfw_cordio_dm_device_set_filter_policy_internal(0U, mode, policy);
}
#endif

#if defined(OPEN_CFW_DM_DEV_BUILD_ALL) || \
    defined(OPEN_CFW_DM_DEV_FILTER_EXTENDED_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_device_set_extended_filter_policy(
    uint8_t advertising_handle, uint8_t mode, uint8_t policy)
{
    return open_cfw_cordio_dm_device_set_filter_policy_internal(
        advertising_handle, mode, policy);
}
#endif
