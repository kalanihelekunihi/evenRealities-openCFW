/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_dm_conn_master.h"
#if !defined(OPEN_CFW_DM_CONN_MASTER_CANCEL_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_UPDATE_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_L2C_ACTION_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_L2C_INDICATION_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_OPEN_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_MASTER_SET_ADDRESS_ONLY)
#define OPEN_CFW_DM_CONN_MASTER_ALL 1
#endif
#ifdef OPEN_CFW_DM_CONN_MASTER_PRODUCTION
#define CONNECTION_ADDRESS_TYPE (*(uint8_t *)(uintptr_t)0x20073B85U)
#else
uint8_t open_cfw_cordio_dm_conn_master_address_type;
#define CONNECTION_ADDRESS_TYPE open_cfw_cordio_dm_conn_master_address_type
#endif

#if defined(OPEN_CFW_DM_CONN_MASTER_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_CANCEL_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_action_cancel(
    struct open_cfw_cordio_dm_conn_slave_control *control,void *message)
{
    (void)control;(void)message;
    open_cfw_cordio_hci_create_connection_cancel();
    open_cfw_cordio_dm_device_pass_event_to_privacy(0x0EU,1U,0U,0U);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_UPDATE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_action_update(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_slave_update_message *message)
{
    if(control==NULL||message==NULL)return;
    open_cfw_cordio_hci_connection_update(control->handle,&message->connection_spec);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_L2C_ACTION_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_action_l2c_indication(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_master_l2c_indication *message)
{
    if(control==NULL||message==NULL||message->connection_spec==NULL)return;
    open_cfw_cordio_l2c_connection_update_response(message->identifier,
        control->handle,0U);
    open_cfw_cordio_hci_connection_update(control->handle,
        message->connection_spec);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_L2C_INDICATION_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_l2c_indication(
    uint8_t identifier,uint16_t handle,
    struct open_cfw_cordio_dm_connection_spec *specification)
{
    struct open_cfw_cordio_dm_conn_slave_control *control=
        open_cfw_cordio_dm_connection_control_by_handle(handle);
    struct open_cfw_cordio_dm_conn_master_l2c_indication message={0};
    if(control==NULL||specification==NULL)return;
    message.header.event=0x72U;message.connection_spec=specification;
    message.identifier=identifier;
    open_cfw_cordio_dm_connection_update_execute(control,&message);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_OPEN_ONLY)
__attribute__((used,noinline)) uint8_t open_cfw_cordio_dm_connection_master_open(
    uint8_t client_id,uint8_t initiating_phys,uint8_t address_type,uint8_t *address)
{
    if(address==NULL)return 0U;
    return open_cfw_cordio_dm_connection_open_accept(client_id,initiating_phys,
        0U,0U,0U,0U,address_type,address,0U);
}
#endif
#if defined(OPEN_CFW_DM_CONN_MASTER_ALL)||defined(OPEN_CFW_DM_CONN_MASTER_SET_ADDRESS_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_master_set_address_type(
    uint8_t address_type)
{
    open_cfw_cordio_wsf_task_lock();CONNECTION_ADDRESS_TYPE=address_type;
    open_cfw_cordio_wsf_task_unlock();
}
#endif
