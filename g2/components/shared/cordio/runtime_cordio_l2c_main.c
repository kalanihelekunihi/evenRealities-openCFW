/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_l2c.h"

#if !defined(OPEN_CFW_L2C_MAIN_DEFAULT_DATA_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_DEFAULT_CID_DATA_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_DEFAULT_CONTROL_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_SIGNALING_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_ACL_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_FLOW_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_REJECT_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_ALLOCATE_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_REGISTER_ONLY) && \
    !defined(OPEN_CFW_L2C_MAIN_DATA_REQUEST_ONLY)
#define OPEN_CFW_L2C_MAIN_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_L2C_PRODUCTION
#define OPEN_CFW_L2C_CONTROL \
    (*(struct open_cfw_cordio_l2c_control_block *)0x200737D8U)
#define OPEN_CFW_L2C_DEFAULT_DATA_CALLBACK \
    ((open_cfw_cordio_l2c_data_callback_t)(uintptr_t)0x00530539U)
#define OPEN_CFW_L2C_DEFAULT_CID_CALLBACK \
    ((open_cfw_cordio_l2c_cid_data_callback_t)(uintptr_t)0x00530641U)
#define OPEN_CFW_L2C_DEFAULT_CONTROL_CALLBACK \
    ((open_cfw_cordio_l2c_control_callback_t)(uintptr_t)0x0053076DU)
#define OPEN_CFW_L2C_SIGNALING_CALLBACK \
    ((open_cfw_cordio_l2c_data_callback_t)(uintptr_t)0x0053076FU)
#define OPEN_CFW_L2C_ACL_CALLBACK \
    ((void (*)(uint8_t *))(uintptr_t)0x005308E7U)
#define OPEN_CFW_L2C_FLOW_CALLBACK \
    ((void (*)(uint16_t, uint8_t))(uintptr_t)0x00530AA5U)
#else
#define OPEN_CFW_L2C_CONTROL open_cfw_cordio_l2c_control_block
#define OPEN_CFW_L2C_DEFAULT_DATA_CALLBACK \
    open_cfw_cordio_l2c_default_data_callback
#define OPEN_CFW_L2C_DEFAULT_CID_CALLBACK \
    open_cfw_cordio_l2c_default_cid_data_callback
#define OPEN_CFW_L2C_DEFAULT_CONTROL_CALLBACK \
    open_cfw_cordio_l2c_default_control_callback
#define OPEN_CFW_L2C_SIGNALING_CALLBACK \
    open_cfw_cordio_l2c_receive_signaling_packet
#define OPEN_CFW_L2C_ACL_CALLBACK open_cfw_cordio_l2c_hci_acl_callback
#define OPEN_CFW_L2C_FLOW_CALLBACK open_cfw_cordio_l2c_hci_flow_callback
#endif

static __attribute__((unused)) uint16_t open_cfw_cordio_l2c_main_get_u16(
    const uint8_t *input
)
{
    return (uint16_t)input[0] | ((uint16_t)input[1] << 8);
}

static __attribute__((unused)) void open_cfw_cordio_l2c_main_put_u16(
    uint8_t *output, uint16_t value
)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8);
}

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_DEFAULT_DATA_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_default_data_callback(
    uint16_t handle, uint16_t length, uint8_t *packet
)
{
    (void)handle;
    (void)length;
    (void)packet;
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_DEFAULT_CID_DATA_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_default_cid_data_callback(
    uint16_t handle, uint16_t cid, uint16_t length, uint8_t *packet
)
{
    (void)handle;
    (void)cid;
    (void)length;
    (void)packet;
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_DEFAULT_CONTROL_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_default_control_callback(
    struct open_cfw_cordio_l2c_message_header *message
)
{
    (void)message;
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_SIGNALING_ONLY)
__attribute__((used, noinline)) void
open_cfw_cordio_l2c_receive_signaling_packet(
    uint16_t handle, uint16_t length, uint8_t *packet
)
{
    uint8_t connection_id;
    uint8_t role;
    open_cfw_cordio_l2c_data_callback_t callback = NULL;
    if (packet == NULL || length < OPEN_CFW_L2C_SIGNAL_HEADER_LENGTH) {
        return;
    }
    connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    if (connection_id == 0U || connection_id > OPEN_CFW_L2C_CONNECTIONS) {
        return;
    }
    role = open_cfw_cordio_dm_connection_role(connection_id);
    if (role == OPEN_CFW_L2C_ROLE_MASTER) {
        callback = OPEN_CFW_L2C_CONTROL.master_signaling_callback;
    } else if (role == OPEN_CFW_L2C_ROLE_SLAVE) {
        callback = OPEN_CFW_L2C_CONTROL.slave_signaling_callback;
    }
    if (callback != NULL) {
        callback(handle, length, packet);
    }
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_ACL_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_hci_acl_callback(
    uint8_t *packet
)
{
    uint16_t handle;
    uint16_t hci_length;
    uint16_t payload_length = 0U;
    uint16_t cid;
    open_cfw_cordio_l2c_data_callback_t data_callback = NULL;
    if (packet == NULL) {
        return;
    }
    handle = open_cfw_cordio_l2c_main_get_u16(packet)
        & OPEN_CFW_L2C_HCI_HANDLE_MASK;
    hci_length = open_cfw_cordio_l2c_main_get_u16(packet + 2U);
    if (hci_length >= OPEN_CFW_L2C_HEADER_LENGTH) {
        payload_length = open_cfw_cordio_l2c_main_get_u16(packet + 4U);
    }
    if (hci_length == (uint16_t)(payload_length + OPEN_CFW_L2C_HEADER_LENGTH)
            && payload_length <= (uint16_t)(0xFFFFU - OPEN_CFW_L2C_HEADER_LENGTH)) {
        cid = open_cfw_cordio_l2c_main_get_u16(packet + 6U);
        if (cid == OPEN_CFW_L2C_CID_SIGNALING) {
            data_callback = OPEN_CFW_L2C_CONTROL.signaling_callback;
        } else if (cid == OPEN_CFW_L2C_CID_ATT) {
            data_callback = OPEN_CFW_L2C_CONTROL.att_data_callback;
        } else if (cid == OPEN_CFW_L2C_CID_SMP) {
            data_callback = OPEN_CFW_L2C_CONTROL.smp_data_callback;
        }
        if (data_callback != NULL) {
            data_callback(handle, payload_length, packet);
        } else if (cid != OPEN_CFW_L2C_CID_SIGNALING
                && cid != OPEN_CFW_L2C_CID_ATT
                && cid != OPEN_CFW_L2C_CID_SMP
                && OPEN_CFW_L2C_CONTROL.cid_data_callback != NULL) {
            OPEN_CFW_L2C_CONTROL.cid_data_callback(
                handle, cid, payload_length, packet
            );
        }
    }
    open_cfw_cordio_wsf_message_free_candidate(packet);
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_FLOW_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_hci_flow_callback(
    uint16_t handle, uint8_t flow_disabled
)
{
    struct open_cfw_cordio_l2c_message_header message;
    uint8_t connection_id = open_cfw_cordio_dm_connection_id_by_handle(handle);
    if (connection_id == 0U || connection_id > OPEN_CFW_L2C_CONNECTIONS) {
        return;
    }
    message.parameter = connection_id;
    message.event = flow_disabled;
    message.status = 0U;
    if (OPEN_CFW_L2C_CONTROL.att_control_callback != NULL) {
        OPEN_CFW_L2C_CONTROL.att_control_callback(&message);
    }
    message.event = flow_disabled;
    if (OPEN_CFW_L2C_CONTROL.smp_control_callback != NULL) {
        OPEN_CFW_L2C_CONTROL.smp_control_callback(&message);
    }
    message.event = flow_disabled;
    if (OPEN_CFW_L2C_CONTROL.coc_control_callback != NULL) {
        OPEN_CFW_L2C_CONTROL.coc_control_callback(&message);
    }
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_REJECT_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_send_command_reject(
    uint16_t handle, uint8_t identifier, uint16_t reason
)
{
    uint8_t *packet = open_cfw_cordio_l2c_message_allocate(14U);
    if (packet != NULL) {
        uint8_t *output = packet + OPEN_CFW_L2C_PAYLOAD_START;
        output[0] = OPEN_CFW_L2C_SIGNAL_COMMAND_REJECT;
        output[1] = identifier;
        open_cfw_cordio_l2c_main_put_u16(
            output + 2U, OPEN_CFW_L2C_COMMAND_REJECT_LENGTH
        );
        open_cfw_cordio_l2c_main_put_u16(output + 4U, reason);
        open_cfw_cordio_l2c_data_request(
            OPEN_CFW_L2C_CID_SIGNALING, handle, 6U, packet
        );
    }
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_ALLOCATE_ONLY)
__attribute__((used, noinline)) void *open_cfw_cordio_l2c_message_allocate(
    uint16_t length
)
{
    return open_cfw_cordio_wsf_message_data_allocate_candidate(length, 0U);
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_INITIALIZE_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_initialize(void)
{
    OPEN_CFW_L2C_CONTROL.att_data_callback =
        OPEN_CFW_L2C_DEFAULT_DATA_CALLBACK;
    OPEN_CFW_L2C_CONTROL.smp_data_callback =
        OPEN_CFW_L2C_DEFAULT_DATA_CALLBACK;
    OPEN_CFW_L2C_CONTROL.signaling_callback =
        OPEN_CFW_L2C_SIGNALING_CALLBACK;
    OPEN_CFW_L2C_CONTROL.att_control_callback =
        OPEN_CFW_L2C_DEFAULT_CONTROL_CALLBACK;
    OPEN_CFW_L2C_CONTROL.smp_control_callback =
        OPEN_CFW_L2C_DEFAULT_CONTROL_CALLBACK;
    OPEN_CFW_L2C_CONTROL.coc_control_callback =
        OPEN_CFW_L2C_DEFAULT_CONTROL_CALLBACK;
    OPEN_CFW_L2C_CONTROL.cid_data_callback =
        OPEN_CFW_L2C_DEFAULT_CID_CALLBACK;
    OPEN_CFW_L2C_CONTROL.identifier = 1U;
    open_cfw_cordio_hci_acl_register(
        OPEN_CFW_L2C_ACL_CALLBACK,
        OPEN_CFW_L2C_FLOW_CALLBACK
    );
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_REGISTER_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_register(
    uint16_t cid, open_cfw_cordio_l2c_data_callback_t data_callback,
    open_cfw_cordio_l2c_control_callback_t control_callback
)
{
    if (data_callback == NULL) {
        data_callback = OPEN_CFW_L2C_DEFAULT_DATA_CALLBACK;
    }
    if (control_callback == NULL) {
        control_callback = OPEN_CFW_L2C_DEFAULT_CONTROL_CALLBACK;
    }
    if (cid == OPEN_CFW_L2C_CID_ATT) {
        OPEN_CFW_L2C_CONTROL.att_data_callback = data_callback;
        OPEN_CFW_L2C_CONTROL.att_control_callback = control_callback;
    } else if (cid == OPEN_CFW_L2C_CID_SMP) {
        OPEN_CFW_L2C_CONTROL.smp_data_callback = data_callback;
        OPEN_CFW_L2C_CONTROL.smp_control_callback = control_callback;
    }
}
#endif

#if defined(OPEN_CFW_L2C_MAIN_BUILD_ALL) || defined(OPEN_CFW_L2C_MAIN_DATA_REQUEST_ONLY)
__attribute__((used, noinline)) void open_cfw_cordio_l2c_data_request(
    uint16_t cid, uint16_t handle, uint16_t length, uint8_t *packet
)
{
    if (packet == NULL) {
        return;
    }
    if (length > (uint16_t)(0xFFFFU - OPEN_CFW_L2C_HEADER_LENGTH)) {
        open_cfw_cordio_wsf_message_free_candidate(packet);
        return;
    }
    open_cfw_cordio_l2c_main_put_u16(packet, handle);
    open_cfw_cordio_l2c_main_put_u16(
        packet + 2U, (uint16_t)(length + OPEN_CFW_L2C_HEADER_LENGTH)
    );
    open_cfw_cordio_l2c_main_put_u16(packet + 4U, length);
    open_cfw_cordio_l2c_main_put_u16(packet + 6U, cid);
    open_cfw_cordio_hci_send_acl_data(packet);
}
#endif
