/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the eight linked Packetcraft Cordio r20.05c
 * dm_sec.c functions retained by G2 2.2.6.10.  Four additional public APIs
 * have no body, caller, or stored pointer in the authenticated stock image.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_DM_SEC_HCI_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_MESSAGE_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_CALLBACK_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_AUTH_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_INIT_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_GET_CSRK_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_GET_IRK_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_RESET_ONLY)
#define OPEN_CFW_DM_SEC_ALL 1
#else
#define OPEN_CFW_DM_SEC_ALL 0
#endif

struct open_cfw_dm_sec_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_dm_sec_ccb {
    uint8_t reserved0[12];
    uint16_t handle;
    uint8_t reserved14[2];
    uint8_t connection_id;
    uint8_t reserved17;
    uint8_t using_ltk;
    uint8_t reserved19[4];
    uint8_t security_level;
    uint8_t temporary_security_level;
};

struct open_cfw_dm_sec_encrypt_event {
    struct open_cfw_dm_sec_header header;
    uint8_t using_ltk;
};

#ifndef OPEN_CFW_DM_SEC_CALLBACK
typedef void (*open_cfw_dm_sec_callback)(void *message);
#define OPEN_CFW_DM_SEC_CALLBACK(message) \
    (((open_cfw_dm_sec_callback *)(uintptr_t)0x20073B80U)[0]((message)))
#endif

#ifndef OPEN_CFW_DM_SEC_ATT_CALLBACK
typedef void (*open_cfw_dm_sec_att_callback)(void *message);
#define OPEN_CFW_DM_SEC_ATT_CALLBACK \
    (*(open_cfw_dm_sec_att_callback *)(uintptr_t)0x20071334U)
#endif

#ifndef OPEN_CFW_DM_SEC_SET_INTERFACE
#define OPEN_CFW_DM_SEC_SET_INTERFACE(value) \
    (((void **)(uintptr_t)0x20000694U)[5] = (value))
#endif

#ifndef OPEN_CFW_DM_SEC_INTERFACE
#define OPEN_CFW_DM_SEC_INTERFACE ((void *)(uintptr_t)0x0078A898U)
#endif

#ifndef OPEN_CFW_DM_SEC_LOCAL_IRK
#define OPEN_CFW_DM_SEC_LOCAL_IRK \
    (*(uint8_t **)(uintptr_t)0x20074114U)
#endif

#ifndef OPEN_CFW_DM_SEC_LOCAL_CSRK
#define OPEN_CFW_DM_SEC_LOCAL_CSRK \
    (*(uint8_t **)(uintptr_t)0x20074118U)
#endif

#ifndef OPEN_CFW_DM_SEC_ZERO_KEY
#define OPEN_CFW_DM_SEC_ZERO_KEY ((const uint8_t *)(uintptr_t)0x007856B0U)
#endif

extern struct open_cfw_dm_sec_ccb *open_cfw_retained_cordio_dm_conn_ccb_by_handle(
    uint16_t handle);
extern struct open_cfw_dm_sec_ccb *open_cfw_retained_cordio_dm_conn_ccb_by_id(
    uint8_t connection_id);
extern int open_cfw_retained_iar_memcmp(
    const void *left, const void *right, uint32_t size);
extern uint8_t *open_cfw_retained_cordio_smp_dm_get_stk(
    uint8_t connection_id, uint8_t *security_level);
extern unsigned int open_cfw_retained_cordio_smp_dm_lesc_enabled(
    uint8_t connection_id);
extern void open_cfw_retained_cordio_hci_le_ltk_request_reply(
    uint16_t handle, const uint8_t key[16]);
extern void open_cfw_retained_cordio_hci_le_ltk_request_negative_reply(
    uint16_t handle);
extern void open_cfw_retained_cordio_dm_conn_set_idle(
    uint8_t connection_id, uint8_t idle_mask, uint8_t idle_value);
extern void open_cfw_retained_cordio_smp_dm_encrypt_indication(void *message);
extern void open_cfw_retained_cordio_hci_le_start_encryption(
    uint16_t handle, const uint8_t random[8], uint16_t diversifier,
    const uint8_t key[16]);
extern void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t size);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);
extern void open_cfw_retained_cordio_smp_dm_msg_send(void *message);
extern void open_cfw_retained_cordio_smp_db_init(void);

void open_cfw_cordio_dm_sec_smp_callback_execute(void *message);

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_HCI_ONLY)
void open_cfw_cordio_dm_sec_hci_handler(void *message)
{
    uint8_t *event = (uint8_t *)message;
    struct open_cfw_dm_sec_ccb *ccb =
        open_cfw_retained_cordio_dm_conn_ccb_by_handle(
            *(uint16_t *)(void *)event);

    if (ccb == NULL) {
        return;
    }

    if (event[2] == 0x10U) {
        uint16_t diversifier = *(uint16_t *)(void *)(event + 14U);

        if (diversifier == 0U &&
            open_cfw_retained_iar_memcmp(
                event + 6U, OPEN_CFW_DM_SEC_ZERO_KEY, 8U) == 0) {
            uint8_t security_level;
            uint8_t *key = open_cfw_retained_cordio_smp_dm_get_stk(
                ccb->connection_id, &security_level);
            if (key != NULL) {
                ccb->temporary_security_level = security_level;
                ccb->using_ltk = 0U;
                open_cfw_retained_cordio_hci_le_ltk_request_reply(
                    *(uint16_t *)(void *)event, key);
                return;
            }
        } else if (open_cfw_retained_cordio_smp_dm_lesc_enabled(
                       ccb->connection_id) != 0U) {
            open_cfw_retained_cordio_hci_le_ltk_request_negative_reply(
                *(uint16_t *)(void *)event);
            return;
        }

        open_cfw_retained_cordio_dm_conn_set_idle(
            ccb->connection_id, 2U, 1U);
        ccb->using_ltk = 1U;
        *(uint16_t *)(void *)event = ccb->connection_id;
        event[2] = 0x30U;
        OPEN_CFW_DM_SEC_CALLBACK(message);
    } else if (event[2] == 0x0EU || event[2] == 0x0FU) {
        struct open_cfw_dm_sec_encrypt_event indication;

        open_cfw_retained_cordio_dm_conn_set_idle(
            ccb->connection_id, 2U, 0U);
        indication.header.param = ccb->connection_id;
        indication.header.status = event[3];
        if (event[3] == 0U) {
            indication.header.event = 0x2CU;
            ccb->security_level = ccb->temporary_security_level;
            indication.using_ltk = ccb->using_ltk;
        } else {
            indication.header.event = 0x2DU;
            indication.using_ltk = 0U;
        }
        open_cfw_cordio_dm_sec_smp_callback_execute(&indication);
        indication.header.param = ccb->connection_id;
        indication.header.status = event[3];
        open_cfw_retained_cordio_smp_dm_encrypt_indication(&indication);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_MESSAGE_ONLY)
void open_cfw_cordio_dm_sec_message_handler(void *message)
{
    uint8_t *bytes = (uint8_t *)message;
    struct open_cfw_dm_sec_ccb *ccb =
        open_cfw_retained_cordio_dm_conn_ccb_by_id((uint8_t)bytes[0]);

    if (ccb == NULL) {
        return;
    }
    if (bytes[2] == 0x28U) {
        open_cfw_retained_cordio_dm_conn_set_idle(
            ccb->connection_id, 2U, 1U);
        ccb->temporary_security_level = bytes[30];
        ccb->using_ltk = 1U;
        open_cfw_retained_cordio_hci_le_start_encryption(
            ccb->handle, bytes + 20U,
            *(uint16_t *)(void *)(bytes + 28U), bytes + 4U);
    } else if (bytes[2] == 0x29U) {
        if (bytes[20] != 0U) {
            ccb->temporary_security_level = bytes[21];
            open_cfw_retained_cordio_hci_le_ltk_request_reply(
                ccb->handle, bytes + 4U);
        } else {
            open_cfw_retained_cordio_dm_conn_set_idle(
                ccb->connection_id, 2U, 0U);
            open_cfw_retained_cordio_hci_le_ltk_request_negative_reply(
                ccb->handle);
        }
    }
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_CALLBACK_ONLY)
void open_cfw_cordio_dm_sec_smp_callback_execute(void *message)
{
    uint8_t event = ((uint8_t *)message)[2];
    open_cfw_dm_sec_att_callback callback = OPEN_CFW_DM_SEC_ATT_CALLBACK;

    if ((event == 0x2AU || event == 0x2CU) && callback != NULL) {
        callback(message);
    }
    OPEN_CFW_DM_SEC_CALLBACK(message);
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_AUTH_ONLY)
void open_cfw_cordio_dm_sec_auth_response(
    uint8_t connection_id, uint8_t authentication_length,
    const uint8_t *authentication_data)
{
    uint8_t *message =
        (uint8_t *)open_cfw_retained_cordio_wsf_msg_alloc(22U);

    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[2] = 4U;
        message[20] = authentication_length;
        if (authentication_data != NULL) {
            open_cfw_iar_memcpy_void(
                message + 4U, authentication_data, authentication_length);
        }
        open_cfw_retained_cordio_smp_dm_msg_send(message);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_INIT_ONLY)
void open_cfw_cordio_dm_sec_init(void)
{
    OPEN_CFW_DM_SEC_SET_INTERFACE(OPEN_CFW_DM_SEC_INTERFACE);
    OPEN_CFW_DM_SEC_LOCAL_IRK = (uint8_t *)OPEN_CFW_DM_SEC_ZERO_KEY;
    OPEN_CFW_DM_SEC_LOCAL_CSRK = OPEN_CFW_DM_SEC_LOCAL_IRK;
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_GET_CSRK_ONLY)
uint8_t *open_cfw_cordio_dm_sec_get_local_csrk(void)
{
    return OPEN_CFW_DM_SEC_LOCAL_CSRK;
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_GET_IRK_ONLY)
uint8_t *open_cfw_cordio_dm_sec_get_local_irk(void)
{
    return OPEN_CFW_DM_SEC_LOCAL_IRK;
}
#endif

#if OPEN_CFW_DM_SEC_ALL || defined(OPEN_CFW_DM_SEC_RESET_ONLY)
void open_cfw_cordio_dm_sec_reset(void)
{
    open_cfw_retained_cordio_smp_db_init();
}
#endif
