/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the six linked Packetcraft Cordio r20.05c
 * dm_sec_slave.c and dm_sec_master.c functions retained by G2 2.2.6.10.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_DM_SEC_SLAVE_PAIR_RSP_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_SLAVE_REQ_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_SLAVE_LTK_RSP_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_MASTER_SMP_ENCRYPT_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_MASTER_PAIR_REQ_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_MASTER_ENCRYPT_REQ_ONLY)
#define OPEN_CFW_DM_SEC_ROLES_ALL 1
#else
#define OPEN_CFW_DM_SEC_ROLES_ALL 0
#endif

struct open_cfw_dm_sec_role_ccb {
    uint8_t reserved0[12];
    uint16_t handle;
    uint8_t reserved14[2];
    uint8_t connection_id;
    uint8_t reserved17;
    uint8_t using_ltk;
    uint8_t reserved19[5];
    uint8_t temporary_security_level;
};

#ifndef OPEN_CFW_DM_SEC_ROLE_HANDLER_ID
#define OPEN_CFW_DM_SEC_ROLE_HANDLER_ID \
    (*(volatile uint8_t *)(uintptr_t)0x20073B84U)
#endif

#ifndef OPEN_CFW_DM_SEC_ROLE_ZERO_KEY
#define OPEN_CFW_DM_SEC_ROLE_ZERO_KEY \
    ((const uint8_t *)(uintptr_t)0x007856B0U)
#endif

extern void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t size);
extern void open_cfw_retained_cordio_smp_dm_msg_send(void *message);
extern void open_cfw_retained_cordio_wsf_msg_send(
    uint8_t handler_id, void *message);
extern void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16]);
extern struct open_cfw_dm_sec_role_ccb *
open_cfw_retained_cordio_dm_conn_ccb_by_id(uint8_t connection_id);
extern void open_cfw_retained_cordio_hci_le_start_encryption(
    uint16_t handle, const uint8_t random[8], uint16_t diversifier,
    const uint8_t key[16]);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);

#if OPEN_CFW_DM_SEC_ROLES_ALL || \
    defined(OPEN_CFW_DM_SEC_SLAVE_PAIR_RSP_ONLY)
void open_cfw_cordio_dm_sec_slave_pair_response(
    uint8_t connection_id, uint8_t oob, uint8_t authentication,
    uint8_t initiator_keys, uint8_t responder_keys)
{
    uint8_t *message =
        (uint8_t *)open_cfw_retained_cordio_wsf_msg_alloc(8U);

    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[2] = 2U;
        message[4] = oob;
        message[5] = authentication;
        message[6] = initiator_keys & 7U;
        message[7] = responder_keys & 7U;
        open_cfw_retained_cordio_smp_dm_msg_send(message);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ROLES_ALL || defined(OPEN_CFW_DM_SEC_SLAVE_REQ_ONLY)
void open_cfw_cordio_dm_sec_slave_request(
    uint8_t connection_id, uint8_t authentication)
{
    uint8_t *message =
        (uint8_t *)open_cfw_retained_cordio_wsf_msg_alloc(6U);

    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[2] = 5U;
        message[4] = authentication;
        open_cfw_retained_cordio_smp_dm_msg_send(message);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ROLES_ALL || defined(OPEN_CFW_DM_SEC_SLAVE_LTK_RSP_ONLY)
void open_cfw_cordio_dm_sec_slave_ltk_response(
    uint8_t connection_id, unsigned int key_found, uint8_t security_level,
    const uint8_t key[16])
{
    uint8_t *message =
        (uint8_t *)open_cfw_retained_cordio_wsf_msg_alloc(22U);

    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[2] = 0x29U;
        message[20] = (uint8_t)key_found;
        message[21] = security_level;
        if (key_found != 0U) {
            open_cfw_retained_cordio_calc128_copy(message + 4U, key);
        }
        open_cfw_retained_cordio_wsf_msg_send(
            OPEN_CFW_DM_SEC_ROLE_HANDLER_ID, message);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ROLES_ALL || \
    defined(OPEN_CFW_DM_SEC_MASTER_SMP_ENCRYPT_ONLY)
void open_cfw_cordio_dm_sec_master_smp_encrypt_request(
    uint8_t connection_id, uint8_t security_level, const uint8_t key[16])
{
    struct open_cfw_dm_sec_role_ccb *ccb =
        open_cfw_retained_cordio_dm_conn_ccb_by_id(connection_id);

    if (ccb != NULL) {
        ccb->temporary_security_level = security_level;
        ccb->using_ltk = 0U;
        open_cfw_retained_cordio_hci_le_start_encryption(
            ccb->handle, OPEN_CFW_DM_SEC_ROLE_ZERO_KEY, 0U, key);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ROLES_ALL || \
    defined(OPEN_CFW_DM_SEC_MASTER_PAIR_REQ_ONLY)
void open_cfw_cordio_dm_sec_master_pair_request(
    uint8_t connection_id, uint8_t oob, uint8_t authentication,
    uint8_t initiator_keys, uint8_t responder_keys)
{
    uint8_t *message =
        (uint8_t *)open_cfw_retained_cordio_wsf_msg_alloc(8U);

    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[2] = 1U;
        message[4] = oob;
        message[5] = authentication;
        message[6] = initiator_keys & 7U;
        message[7] = responder_keys & 7U;
        open_cfw_retained_cordio_smp_dm_msg_send(message);
    }
}
#endif

#if OPEN_CFW_DM_SEC_ROLES_ALL || \
    defined(OPEN_CFW_DM_SEC_MASTER_ENCRYPT_REQ_ONLY)
void open_cfw_cordio_dm_sec_master_encrypt_request(
    uint8_t connection_id, uint8_t security_level,
    const uint8_t long_term_key[26])
{
    uint8_t *message =
        (uint8_t *)open_cfw_retained_cordio_wsf_msg_alloc(32U);

    if (message != NULL) {
        *(uint16_t *)(void *)message = connection_id;
        message[2] = 0x28U;
        open_cfw_iar_memcpy_void(message + 4U, long_term_key, 26U);
        message[30] = security_level;
        open_cfw_retained_cordio_wsf_msg_send(
            OPEN_CFW_DM_SEC_ROLE_HANDLER_ID, message);
    }
}
#endif
