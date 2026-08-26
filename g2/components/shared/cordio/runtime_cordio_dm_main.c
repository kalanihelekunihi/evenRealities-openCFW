/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_dm_main.h"

#if !defined(OPEN_CFW_DM_MAIN_HCI_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_EMPTY_RESET_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_EMPTY_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_PASS_CONNECTION_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_REGISTER_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_FIND_AD_TYPE_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_HANDLER_INIT_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_LL_PRIVACY_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_LL_ADDRESS_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_HOST_ADDRESS_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_SIZE_EVENT_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_SCAN_INTERNAL_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_SCAN_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_INIT_INTERNAL_ONLY) && \
    !defined(OPEN_CFW_DM_MAIN_INIT_ONLY)
#define OPEN_CFW_DM_MAIN_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_DM_MAIN_PRODUCTION
#define OPEN_CFW_DM_MAIN_CALLBACK (*(uintptr_t *)0x20073B80U)
#define OPEN_CFW_DM_MAIN_HANDLER_ID (*(uint8_t *)0x20073B84U)
#define OPEN_CFW_DM_MAIN_RESETTING (*(uint8_t *)0x20073B88U)
#define OPEN_CFW_DM_MAIN_LL_PRIVACY (*(uint8_t *)0x20073B8EU)
#define OPEN_CFW_DM_MAIN_INTERFACES ((const uintptr_t *)0x20000694U)
#define OPEN_CFW_DM_MAIN_DEFAULT_INTERFACE ((uintptr_t)0x0078A850U)
#define OPEN_CFW_DM_MAIN_HCI_ROUTE ((const uint8_t *)0x006E006CU)
#define OPEN_CFW_DM_MAIN_EVENT_LENGTH ((const uint16_t *)0x006D1904U)
#define OPEN_CFW_DM_MAIN_HCI_CALLBACK_ENTRY \
    ((void (*)(struct open_cfw_cordio_dm_device_message_header *)) \
        (uintptr_t)0x004D299DU)
#define OPEN_CFW_DM_MAIN_SCAN_INTERNAL_ENTRY \
    ((uint8_t (*)(uint8_t, uint8_t))(uintptr_t)0x004D2B01U)
#define OPEN_CFW_DM_MAIN_INIT_INTERNAL_ENTRY \
    ((uint8_t (*)(uint8_t, uint8_t))(uintptr_t)0x004D2B4DU)
#else
#define OPEN_CFW_DM_MAIN_CALLBACK open_cfw_cordio_dm_device_main_control.callback
#define OPEN_CFW_DM_MAIN_HANDLER_ID \
    open_cfw_cordio_dm_device_main_control.handler_id
#define OPEN_CFW_DM_MAIN_RESETTING open_cfw_cordio_dm_device_main_control.resetting
#define OPEN_CFW_DM_MAIN_LL_PRIVACY \
    open_cfw_cordio_dm_main_host_link_layer_privacy
#define OPEN_CFW_DM_MAIN_INTERFACES open_cfw_cordio_dm_device_function_interfaces
#define OPEN_CFW_DM_MAIN_DEFAULT_INTERFACE open_cfw_cordio_dm_default_interface
uint8_t open_cfw_cordio_dm_main_host_link_layer_privacy;
static const uint8_t open_cfw_dm_main_host_hci_route[90] = {
    7,3,3,3,3,3,2,4,4,4,4,4,5,5,5,5,5,7,7,7,7,6,6,6,6,6,6,5,5,4,
    4,7,7,4,7,4,4,5,5,4,4,9,9,9,2,2,0,0,11,11,11,7,2,0,2,0,10,1,11,
    12,12,13,13,13,13,13,13,13,16,16,22,13,16,16,16,4,17,17,20,20,20,
    20,20,20,18,18,19,19,19,19
};
static const uint16_t open_cfw_dm_main_host_event_length[92] = {
    4,4,4,12,4,4,28,36,10,14,6,4,6,4,6,34,16,8,6,36,100,20,6,4,10,10,
    6,6,6,12,12,6,14,14,8,6,10,6,10,8,10,12,4,4,36,6,6,22,22,6,26,26,
    8,8,16,16,14,28,28,8,8,8,8,8,8,8,8,10,40,6,10,40,10,10,6,6,6,44,
    32,16,60,6,56,56,6,6,28,8,4,6,6,136
};
#define OPEN_CFW_DM_MAIN_HCI_ROUTE open_cfw_dm_main_host_hci_route
#define OPEN_CFW_DM_MAIN_EVENT_LENGTH open_cfw_dm_main_host_event_length
#define OPEN_CFW_DM_MAIN_HCI_CALLBACK_ENTRY \
    open_cfw_cordio_dm_hci_event_callback
#define OPEN_CFW_DM_MAIN_SCAN_INTERNAL_ENTRY \
    open_cfw_cordio_dm_scan_phy_to_index_internal
#define OPEN_CFW_DM_MAIN_INIT_INTERNAL_ENTRY \
    open_cfw_cordio_dm_initiator_phy_to_index_internal
#endif

static __attribute__((unused)) const struct
open_cfw_cordio_dm_device_function_interface *open_cfw_dm_main_interface(
    uint8_t component)
{
    uintptr_t address;
    if (component >= OPEN_CFW_DM_DEVICE_COMPONENTS) return NULL;
    address = OPEN_CFW_DM_MAIN_INTERFACES[component];
    if (address == (uintptr_t)0U) return NULL;
    return (const struct open_cfw_cordio_dm_device_function_interface *)address;
}

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_HCI_CALLBACK_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_hci_event_callback(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    const struct open_cfw_cordio_dm_device_function_interface *interface;
    uint8_t component;
    if (event == NULL || event->event >= OPEN_CFW_DM_MAIN_HCI_ROUTES) return;
    if (OPEN_CFW_DM_MAIN_RESETTING != 0U && event->event != 0U) return;
    component = OPEN_CFW_DM_MAIN_HCI_ROUTE[event->event];
    interface = open_cfw_dm_main_interface(component);
    if (interface != NULL && interface->hci_handler != NULL) {
        interface->hci_handler(event);
    }
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_EMPTY_RESET_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_empty_reset(void) {}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_EMPTY_HANDLER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_empty_handler(
    struct open_cfw_cordio_dm_device_message_header *message)
{
    (void)message;
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || \
    defined(OPEN_CFW_DM_MAIN_PASS_CONNECTION_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_pass_hci_event_to_connection(
    struct open_cfw_cordio_dm_device_message_header *event)
{
    const struct open_cfw_cordio_dm_device_function_interface *interface =
        open_cfw_dm_main_interface(OPEN_CFW_DM_MAIN_CONNECTION_COMPONENT);
    if (event != NULL && interface != NULL && interface->hci_handler != NULL) {
        interface->hci_handler(event);
    }
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_REGISTER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_register_callback(
    uintptr_t callback)
{
    uint16_t maximum;
    OPEN_CFW_DM_MAIN_CALLBACK = callback;
    if (callback == (uintptr_t)0U
            || OPEN_CFW_DM_MAIN_INTERFACES[OPEN_CFW_DM_MAIN_LESC_COMPONENT]
                == OPEN_CFW_DM_MAIN_DEFAULT_INTERFACE) return;
    maximum = open_cfw_cordio_hci_get_maximum_receive_acl_length();
    if (maximum < 4U || 65U > (uint16_t)(maximum - 4U)) {
        struct open_cfw_cordio_dm_device_message_header event = {0};
        event.event = OPEN_CFW_DM_MAIN_ERROR_EVENT;
        event.status = 1U;
        ((void (*)(void *))callback)(&event);
    }
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_FIND_AD_TYPE_ONLY)
__attribute__((used, noinline)) uint8_t *open_cfw_cordio_dm_find_advertising_type(
    uint8_t advertising_type, uint16_t data_length, uint8_t *data)
{
    while (data != NULL && data_length >= 2U && data[0] != 0U
            && data[0] < data_length) {
        if (data[1] == advertising_type) return data;
        data_length = (uint16_t)(data_length - data[0] - 1U);
        data += data[0] + 1U;
    }
    return NULL;
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_HANDLER_INIT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_handler_initialize(
    uint8_t handler_id)
{
    OPEN_CFW_DM_MAIN_HANDLER_ID = handler_id;
    OPEN_CFW_DM_MAIN_LL_PRIVACY = 0U;
    OPEN_CFW_DM_MAIN_RESETTING = 0U;
    open_cfw_cordio_hci_event_register(OPEN_CFW_DM_MAIN_HCI_CALLBACK_ENTRY);
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_HANDLER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_handler(
    uint32_t event_mask,
    struct open_cfw_cordio_dm_device_message_header *message)
{
    const struct open_cfw_cordio_dm_device_function_interface *interface;
    uint8_t component;
    (void)event_mask;
    if (message == NULL || OPEN_CFW_DM_MAIN_RESETTING != 0U) return;
    component = (uint8_t)(message->event >> 3U);
    interface = open_cfw_dm_main_interface(component);
    if (interface != NULL && interface->message_handler != NULL) {
        interface->message_handler(message);
    }
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_LL_PRIVACY_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_link_layer_privacy_enabled(void)
{
    return (uint8_t)(OPEN_CFW_DM_MAIN_LL_PRIVACY != 0U);
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_LL_ADDRESS_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_link_layer_address_type(uint8_t address_type)
{
    if (OPEN_CFW_DM_MAIN_LL_PRIVACY != 0U) {
        if (address_type == 0U) return 2U;
        if (address_type == 1U) return 3U;
    }
    return address_type;
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_HOST_ADDRESS_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_host_address_type(uint8_t address_type)
{
    if (OPEN_CFW_DM_MAIN_LL_PRIVACY != 0U) {
        if (address_type == 2U) return 0U;
        if (address_type == 3U) return 1U;
    }
    return address_type;
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_SIZE_EVENT_ONLY)
__attribute__((used, noinline)) uint16_t open_cfw_cordio_dm_size_of_event(
    const struct open_cfw_cordio_dm_device_message_header *event)
{
    if (event != NULL && event->event >= OPEN_CFW_DM_MAIN_CALLBACK_START
            && event->event <= OPEN_CFW_DM_MAIN_CALLBACK_END) {
        return OPEN_CFW_DM_MAIN_EVENT_LENGTH[
            event->event - OPEN_CFW_DM_MAIN_CALLBACK_START];
    }
    return sizeof(struct open_cfw_cordio_dm_device_message_header);
}
#endif

static __attribute__((unused)) uint8_t open_cfw_dm_main_phy_to_index(
    uint8_t number_of_phys, uint8_t phy)
{
    if (number_of_phys <= 1U) return 0U;
    if (number_of_phys == 2U) return (uint8_t)(phy == 1U ? 0U : 1U);
    if (phy == 1U) return 0U;
    return (uint8_t)(phy == 2U ? 1U : 2U);
}

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_SCAN_INTERNAL_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_scan_phy_to_index_internal(
    uint8_t number_of_phys, uint8_t scan_phy)
{
    return open_cfw_dm_main_phy_to_index(number_of_phys, scan_phy);
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_SCAN_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_scan_phy_to_index(uint8_t scan_phy)
{
    return OPEN_CFW_DM_MAIN_SCAN_INTERNAL_ENTRY(2U, scan_phy);
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_INIT_INTERNAL_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_initiator_phy_to_index_internal(
    uint8_t number_of_phys, uint8_t initiator_phy)
{
    return open_cfw_dm_main_phy_to_index(number_of_phys, initiator_phy);
}
#endif

#if defined(OPEN_CFW_DM_MAIN_BUILD_ALL) || defined(OPEN_CFW_DM_MAIN_INIT_ONLY)
__attribute__((used, noinline)) uint8_t
open_cfw_cordio_dm_initiator_phy_to_index(uint8_t initiator_phy)
{
    return OPEN_CFW_DM_MAIN_INIT_INTERNAL_ENTRY(2U, initiator_phy);
}
#endif
