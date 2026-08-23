/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the linked Packetcraft Cordio r20.05c
 * dm_sec_lesc.c surface retained by G2 2.2.6.10.  The public source bodies
 * are release-invariant across the admitted r20.05..r20.05c interval; this
 * file expresses only the seven functions present in the firmware image.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_DM_SEC_LESC_HANDLER_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_LESC_GENERATE_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_LESC_SET_KEY_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_LESC_GET_KEY_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_LESC_COMPARE_RSP_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_LESC_COMPARE_VALUE_ONLY) && \
    !defined(OPEN_CFW_DM_SEC_LESC_INIT_ONLY)
#define OPEN_CFW_DM_SEC_LESC_ALL 1
#else
#define OPEN_CFW_DM_SEC_LESC_ALL 0
#endif

struct open_cfw_wsf_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_dm_sec_oob_event {
    struct open_cfw_wsf_header header;
    uint8_t confirm[16];
    uint8_t random[16];
};

#ifndef OPEN_CFW_DM_SEC_LESC_CALLBACK
typedef void (*open_cfw_dm_callback)(void *message);
#define OPEN_CFW_DM_SEC_LESC_CALLBACK(message) \
    (((open_cfw_dm_callback *)(uintptr_t)0x20073B80U)[0]((message)))
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_HANDLER_ID
#define OPEN_CFW_DM_SEC_LESC_HANDLER_ID \
    (*(volatile uint8_t *)(uintptr_t)0x20073B84U)
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_CIPHERTEXT
#define OPEN_CFW_DM_SEC_LESC_CIPHERTEXT(message) \
    (*(uint8_t **)((uint8_t *)(message) + 4U))
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_PLAINTEXT
#define OPEN_CFW_DM_SEC_LESC_PLAINTEXT(message) \
    (*(uint8_t **)((uint8_t *)(message) + 8U))
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_OOB_RANDOM
#define OPEN_CFW_DM_SEC_LESC_OOB_RANDOM \
    (*(uint8_t **)(uintptr_t)0x200744F8U)
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_LOCAL_KEY
#define OPEN_CFW_DM_SEC_LESC_LOCAL_KEY \
    ((uint8_t *)(uintptr_t)0x200726D0U)
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_SET_INTERFACE
#define OPEN_CFW_DM_SEC_LESC_SET_INTERFACE(value) \
    (((void **)(uintptr_t)0x20000694U)[8] = (value))
#endif

#ifndef OPEN_CFW_DM_SEC_LESC_INTERFACE
#define OPEN_CFW_DM_SEC_LESC_INTERFACE ((void *)(uintptr_t)0x0078A8A4U)
#endif

extern void open_cfw_retained_cordio_wsf_buf_free(void *buffer);
extern void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16]);
extern unsigned int open_cfw_retained_cordio_sec_ecc_gen_key(
    uint8_t handler_id, uint16_t parameter, uint8_t event);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);
extern void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t size);
extern void open_cfw_retained_cordio_smp_cancel_with_reattempt(
    uint8_t connection_id, void *header, uint8_t reason);
extern void open_cfw_retained_cordio_smp_dm_msg_send(void *message);

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_HANDLER_ONLY)
void open_cfw_cordio_dm_sec_lesc_message_handler(void *message)
{
    uint8_t *bytes = (uint8_t *)message;

    if (bytes[2] == 0x41U) {
        bytes[2] = 0x34U;
        OPEN_CFW_DM_SEC_LESC_CALLBACK(message);
    } else if (bytes[2] == 0x40U) {
        struct open_cfw_dm_sec_oob_event event;
        uint8_t *random = OPEN_CFW_DM_SEC_LESC_OOB_RANDOM;

        open_cfw_retained_cordio_wsf_buf_free(
            OPEN_CFW_DM_SEC_LESC_PLAINTEXT(message));
        event.header.param = 0U;
        event.header.event = 0x33U;
        event.header.status = 0U;
        open_cfw_retained_cordio_calc128_copy(
            event.confirm, OPEN_CFW_DM_SEC_LESC_CIPHERTEXT(message));
        open_cfw_retained_cordio_calc128_copy(event.random, random);
        open_cfw_retained_cordio_wsf_buf_free(random);
        OPEN_CFW_DM_SEC_LESC_CALLBACK(&event);
    }
}
#endif

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_GENERATE_ONLY)
void open_cfw_cordio_dm_sec_generate_ecc_key_request(void)
{
    (void)open_cfw_retained_cordio_sec_ecc_gen_key(
        OPEN_CFW_DM_SEC_LESC_HANDLER_ID, 0U, 0x41U);
}
#endif

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_SET_KEY_ONLY)
void open_cfw_cordio_dm_sec_set_ecc_key(const void *key)
{
    open_cfw_iar_memcpy_void(OPEN_CFW_DM_SEC_LESC_LOCAL_KEY, key, 96U);
}
#endif

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_GET_KEY_ONLY)
void *open_cfw_cordio_dm_sec_get_ecc_key(void)
{
    return OPEN_CFW_DM_SEC_LESC_LOCAL_KEY;
}
#endif

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_COMPARE_RSP_ONLY)
void open_cfw_cordio_dm_sec_compare_response(
    uint8_t connection_id, unsigned int valid)
{
    struct open_cfw_wsf_header *message =
        (struct open_cfw_wsf_header *)
            open_cfw_retained_cordio_wsf_msg_alloc(22U);

    if (message != NULL) {
        message->param = connection_id;
        if (valid != 0U) {
            message->event = 0x16U;
        } else {
            open_cfw_retained_cordio_smp_cancel_with_reattempt(
                connection_id, message, 0x0CU);
        }
        open_cfw_retained_cordio_smp_dm_msg_send(message);
    }
}
#endif

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_COMPARE_VALUE_ONLY)
uint32_t open_cfw_cordio_dm_sec_get_compare_value(const uint8_t confirm[16])
{
    uint32_t compare = (uint32_t)confirm[15]
        | ((uint32_t)confirm[14] << 8)
        | ((uint32_t)confirm[13] << 16)
        | ((uint32_t)confirm[12] << 24);
    return compare % 1000000U;
}
#endif

#if OPEN_CFW_DM_SEC_LESC_ALL || defined(OPEN_CFW_DM_SEC_LESC_INIT_ONLY)
void open_cfw_cordio_dm_sec_lesc_init(void)
{
    OPEN_CFW_DM_SEC_LESC_SET_INTERFACE(OPEN_CFW_DM_SEC_LESC_INTERFACE);
}
#endif
