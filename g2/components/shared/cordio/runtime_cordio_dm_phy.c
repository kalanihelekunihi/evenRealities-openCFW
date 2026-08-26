/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_dm_phy.h"

#if !defined(OPEN_CFW_DM_PHY_HCI_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_ACTION_READ_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_ACTION_DEFAULT_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_ACTION_UPDATE_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_READ_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_SET_DEFAULT_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_SET_ONLY) && \
    !defined(OPEN_CFW_DM_PHY_INIT_ONLY)
#define OPEN_CFW_DM_PHY_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_DM_PHY_PRODUCTION
#define OPEN_CFW_DM_PHY_CALLBACK \
    (*(void (**)(void *))(uintptr_t)0x20071334U)
#define OPEN_CFW_DM_PHY_SET_INTERFACE(value) \
    (((uintptr_t *)(uintptr_t)0x20000694U)[OPEN_CFW_DM_PHY_COMPONENT] = (value))
#define OPEN_CFW_DM_PHY_INTERFACE ((uintptr_t)0x0078A85CU)
#else
void (*open_cfw_cordio_dm_phy_host_callback)(void *event);
uintptr_t open_cfw_cordio_dm_phy_host_interface;
#define OPEN_CFW_DM_PHY_CALLBACK open_cfw_cordio_dm_phy_host_callback
#define OPEN_CFW_DM_PHY_SET_INTERFACE(value) \
    (open_cfw_cordio_dm_device_function_interfaces[OPEN_CFW_DM_PHY_COMPONENT] = \
        (value))
#define OPEN_CFW_DM_PHY_INTERFACE open_cfw_cordio_dm_phy_host_interface
#endif

static __attribute__((unused)) void open_cfw_dm_phy_callback(void *event)
{
    void (*callback)(void *) = OPEN_CFW_DM_PHY_CALLBACK;
    if (callback != NULL && event != NULL) callback(event);
}

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_ACTION_READ_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_action_read(
    struct open_cfw_cordio_dm_phy_connection *connection,
    struct open_cfw_cordio_dm_phy_event *event)
{
    struct open_cfw_cordio_dm_phy_event indication = {0};
    if (connection == NULL || event == NULL) return;
    indication.header.parameter = connection->connection_id;
    indication.header.event = OPEN_CFW_DM_PHY_READ_INDICATION;
    indication.header.status = event->status;
    indication.status = event->status;
    indication.handle = connection->handle;
    indication.transmit_phy = event->transmit_phy;
    indication.receive_phy = event->receive_phy;
    open_cfw_dm_phy_callback(&indication);
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_ACTION_DEFAULT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_action_default(
    struct open_cfw_cordio_dm_phy_event *event)
{
    struct open_cfw_cordio_dm_phy_event indication = {0};
    if (event == NULL) return;
    indication.header.event = OPEN_CFW_DM_PHY_DEFAULT_INDICATION;
    indication.header.status = event->status;
    indication.status = event->status;
    open_cfw_dm_phy_callback(&indication);
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_ACTION_UPDATE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_action_update(
    struct open_cfw_cordio_dm_phy_connection *connection,
    struct open_cfw_cordio_dm_phy_event *event)
{
    struct open_cfw_cordio_dm_phy_event indication = {0};
    if (connection == NULL || event == NULL) return;
    indication.header.parameter = connection->connection_id;
    indication.header.event = OPEN_CFW_DM_PHY_UPDATE_INDICATION;
    indication.header.status = event->status;
    indication.status = event->status;
    indication.handle = connection->handle;
    indication.transmit_phy = event->transmit_phy;
    indication.receive_phy = event->receive_phy;
    open_cfw_dm_phy_callback(&indication);
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_HCI_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_hci_handler(
    struct open_cfw_cordio_dm_phy_event *event)
{
    struct open_cfw_cordio_dm_phy_connection *connection;
    if (event == NULL) return;
    if (event->header.event == OPEN_CFW_DM_PHY_HCI_DEFAULT_COMPLETE) {
        open_cfw_cordio_dm_phy_action_default(event);
        return;
    }
    connection = open_cfw_cordio_dm_connection_control_by_handle(
        event->header.parameter);
    if (connection == NULL) return;
    if (event->header.event == OPEN_CFW_DM_PHY_HCI_READ_COMPLETE) {
        open_cfw_cordio_dm_phy_action_read(connection, event);
    } else if (event->header.event == OPEN_CFW_DM_PHY_HCI_UPDATE_COMPLETE) {
        open_cfw_cordio_dm_phy_action_update(connection, event);
    }
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_READ_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_read(
    uint8_t connection_id)
{
    struct open_cfw_cordio_dm_phy_connection *connection;
    open_cfw_cordio_wsf_task_lock();
    connection = open_cfw_cordio_dm_connection_control_by_id(connection_id);
    open_cfw_cordio_wsf_task_unlock();
    if (connection != NULL) open_cfw_cordio_hci_read_phy(connection->handle);
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_SET_DEFAULT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_set_default(
    uint8_t all_phys, uint8_t transmit_phys, uint8_t receive_phys)
{
    open_cfw_cordio_hci_set_default_phy(
        all_phys, transmit_phys, receive_phys);
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_SET_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_set(
    uint8_t connection_id, uint8_t all_phys, uint8_t transmit_phys,
    uint8_t receive_phys, uint16_t phy_options)
{
    struct open_cfw_cordio_dm_phy_connection *connection;
    open_cfw_cordio_wsf_task_lock();
    connection = open_cfw_cordio_dm_connection_control_by_id(connection_id);
    open_cfw_cordio_wsf_task_unlock();
    if (connection != NULL) {
        open_cfw_cordio_hci_set_phy(
            connection->handle, all_phys, transmit_phys, receive_phys,
            phy_options);
    }
}
#endif

#if defined(OPEN_CFW_DM_PHY_BUILD_ALL) || defined(OPEN_CFW_DM_PHY_INIT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_dm_phy_initialize(void)
{
    open_cfw_cordio_wsf_task_lock();
    OPEN_CFW_DM_PHY_SET_INTERFACE(OPEN_CFW_DM_PHY_INTERFACE);
    open_cfw_cordio_hci_set_supported_features(
        (uint64_t)OPEN_CFW_DM_PHY_FEATURE_MASK, 1U);
    open_cfw_cordio_wsf_task_unlock();
}
#endif
