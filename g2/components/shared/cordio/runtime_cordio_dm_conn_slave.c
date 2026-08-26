/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_dm_conn_slave.h"

#if !defined(OPEN_CFW_DM_CONN_SLAVE_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_SLAVE_UPDATE_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_SLAVE_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_SLAVE_L2C_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_SLAVE_L2C_REJECT_ONLY) && \
    !defined(OPEN_CFW_DM_CONN_SLAVE_ACCEPT_ONLY)
#define OPEN_CFW_DM_CONN_SLAVE_ALL 1
#endif

#ifdef OPEN_CFW_DM_CONN_SLAVE_PRODUCTION
#define APPLICATION_CALLBACK \
    (*(open_cfw_cordio_dm_conn_slave_callback_t *)(uintptr_t)0x20071340U)
#else
open_cfw_cordio_dm_conn_slave_callback_t
    open_cfw_cordio_dm_conn_slave_application_callback;
#define APPLICATION_CALLBACK open_cfw_cordio_dm_conn_slave_application_callback
#endif

#if defined(OPEN_CFW_DM_CONN_SLAVE_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_CALLBACK_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_update_callback(
    struct open_cfw_cordio_dm_conn_slave_control *control,uint8_t status)
{
    struct open_cfw_cordio_dm_conn_slave_update_event event={0};
    open_cfw_cordio_dm_conn_slave_callback_t callback=APPLICATION_CALLBACK;
    if(control==NULL||callback==NULL)return;
    event.header.parameter=control->connection_id;
    event.header.event=0x29U;
    event.header.status=status;
    event.status=status;
    event.handle=control->handle;
    callback(&event);
}
#endif

#if defined(OPEN_CFW_DM_CONN_SLAVE_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_UPDATE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_action_update(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_slave_update_message *message)
{
    if(control==NULL||message==NULL)return;
    if((control->features&2U)!=0U &&
       (open_cfw_cordio_hci_get_supported_features()&2U)!=0U){
        open_cfw_cordio_hci_connection_update(control->handle,&message->connection_spec);
    }else if(control->updating==0U){
        control->updating=1U;
        open_cfw_cordio_l2c_connection_update_request(control->handle,&message->connection_spec);
    }else{
        open_cfw_cordio_dm_connection_slave_update_callback(control,0x0CU);
    }
}
#endif

#if defined(OPEN_CFW_DM_CONN_SLAVE_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_CONFIRM_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_action_l2c_confirm(
    struct open_cfw_cordio_dm_conn_slave_control *control,
    struct open_cfw_cordio_dm_conn_slave_confirm_message *message)
{
    if(control==NULL||message==NULL||control->updating==0U)return;
    control->updating=0U;
    if(message->result!=0U)
        open_cfw_cordio_dm_connection_slave_update_callback(control,(uint8_t)message->result);
}
#endif

#if defined(OPEN_CFW_DM_CONN_SLAVE_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_L2C_CONFIRM_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_l2c_confirm(
    uint16_t handle,uint16_t result)
{
    struct open_cfw_cordio_dm_conn_slave_control *control=
        open_cfw_cordio_dm_connection_control_by_handle(handle);
    struct open_cfw_cordio_dm_conn_slave_confirm_message message={0};
    if(control==NULL)return;
    message.header.event=0x73U;
    message.result=result;
    open_cfw_cordio_dm_connection_update_execute(control,&message);
}
#endif

#if defined(OPEN_CFW_DM_CONN_SLAVE_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_L2C_REJECT_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_dm_connection_slave_l2c_reject(
    uint16_t handle,uint16_t result)
{
    struct open_cfw_cordio_dm_conn_slave_reject_event event={0};
    open_cfw_cordio_dm_conn_slave_callback_t callback=APPLICATION_CALLBACK;
    if(callback==NULL)return;
    event.header.event=0x77U;
    event.reason=result;
    event.handle=handle;
    callback(&event);
}
#endif

#if defined(OPEN_CFW_DM_CONN_SLAVE_ALL)||defined(OPEN_CFW_DM_CONN_SLAVE_ACCEPT_ONLY)
__attribute__((used,noinline)) uint8_t open_cfw_cordio_dm_connection_slave_accept(
    uint8_t client_id,uint8_t advertising_handle,uint8_t advertising_type,
    uint16_t duration,uint8_t maximum_events,uint8_t address_type,uint8_t *address)
{
    if(address==NULL)return 0U;
    return open_cfw_cordio_dm_connection_open_accept(client_id,0U,
        advertising_handle,advertising_type,duration,maximum_events,address_type,
        address,1U);
}
#endif
