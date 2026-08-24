/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the sixteen Packetcraft Cordio Secure Connections
 * initiator actions linked by G2 2.2.6.10.  The r20/R4 keyReady transition
 * selected by the stock image is retained explicitly.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMPI_SC_AUTH_SELECT_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_SEND_PUBLIC_KEY_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_JWNC_SETUP_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_JWNC_SEND_RANDOM_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_JWNC_F4_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_JWNC_G2_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_PASSKEY_CA_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_PASSKEY_CB_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_PASSKEY_SEND_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_PASSKEY_SEND_RANDOM_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_PASSKEY_CHECK_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_OOB_CB_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_OOB_SEND_RANDOM_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_OOB_PROCESS_RANDOM_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_DH_SEND_ONLY) && \
    !defined(OPEN_CFW_SMPI_SC_DH_VERIFY_ONLY)
#define OPEN_CFW_SMPI_SC_ALL 1
#else
#define OPEN_CFW_SMPI_SC_ALL 0
#endif

#define OPEN_CFW_SMPI_SC_PDU_OFFSET 8U
#define OPEN_CFW_SMPI_SC_HEADER_BYTES 1U
#define OPEN_CFW_SMPI_SC_RANDOM_BYTES 16U
#define OPEN_CFW_SMPI_SC_KEY_BYTES 16U
#define OPEN_CFW_SMPI_SC_PAIR_OOB 2U
#define OPEN_CFW_SMPI_SC_PAIR_MAX_KEY 4U
#define OPEN_CFW_SMPI_SC_OOB_PRESENT 1U
#define OPEN_CFW_SMPI_SC_CMD_CONFIRM 3U
#define OPEN_CFW_SMPI_SC_CMD_RANDOM 4U
#define OPEN_CFW_SMPI_SC_CMD_PUBLIC_KEY 12U
#define OPEN_CFW_SMPI_SC_CMD_DH_CHECK 13U
#define OPEN_CFW_SMPI_SC_EVENT_MAX_ATTEMPTS 13U
#define OPEN_CFW_SMPI_SC_EVENT_PASSKEY_NEXT 26U
#define OPEN_CFW_SMPI_SC_EVENT_PASSKEY_COMPLETE 27U
#define OPEN_CFW_SMPI_SC_EVENT_CMAC_COMPLETE 28U
#define OPEN_CFW_SMPI_SC_EVENT_DH_FAILURE 29U
#define OPEN_CFW_SMPI_SC_ERROR_DH_CHECK 11U
#define OPEN_CFW_SMPI_SC_PASSKEY_BITS 20U

struct open_cfw_smpi_sc_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};
struct open_cfw_smpi_sc_timer {
    uint32_t next;
    struct open_cfw_smpi_sc_header message;
    uint32_t ticks;
    uint8_t handler_id, is_started, reserved[2];
};
union open_cfw_smpi_sc_legacy_scratch {
    uint8_t bytes[64];
    uint32_t alignment;
};
struct open_cfw_smpi_sc_public_key { uint8_t x[32], y[32]; };
struct open_cfw_smpi_sc_scratch {
    uint8_t initiator_random[16], responder_random[16];
    uint8_t ra[16], rb[16], peer_cb[16], peer_ca_or_ea[16];
};
struct open_cfw_smpi_sc_ltk { uint8_t mac[16], temporary_ltk[16]; };
struct open_cfw_smpi_sc_record {
    uint8_t lesc_enabled, authentication_type, keypress_notify;
    uint8_t passkey_position, display, reserved[3];
    struct open_cfw_smpi_sc_public_key *peer_public_key;
    struct open_cfw_smpi_sc_public_key *local_public_key;
    uint8_t *private_key;
    struct open_cfw_smpi_sc_scratch *scratch;
    struct open_cfw_smpi_sc_ltk *ltk;
};
struct open_cfw_smpi_sc_ccb {
    struct open_cfw_smpi_sc_timer response_timer, wait_timer;
    uint8_t pair_request[7], pair_response[7], reserved46[2];
    union open_cfw_smpi_sc_legacy_scratch *legacy_scratch;
    uint8_t *queued_packet;
    uint16_t handle;
    uint8_t initiator, security_request, flow_disabled, connection_id;
    uint8_t state, next_command, authentication, token, attempts;
    uint8_t last_sent_key, key_ready, reserved69[3];
    struct open_cfw_smpi_sc_record *secure_connections;
};
struct open_cfw_smpi_sc_config {
    uint32_t attempt_timeout;
    uint8_t io_capability, minimum_key_length, maximum_key_length;
    uint8_t maximum_attempts, authentication, reserved9[3];
    uint32_t maximum_attempt_timeout, attempt_decrement_timeout;
    uint16_t attempt_exponent;
};
struct open_cfw_smpi_sc_auth_response {
    struct open_cfw_smpi_sc_header header;
    uint8_t data[16];
    uint8_t length;
};
struct open_cfw_smpi_sc_data_message {
    struct open_cfw_smpi_sc_header header;
    uint8_t *packet;
};
struct open_cfw_smpi_sc_aes_message {
    struct open_cfw_smpi_sc_header header;
    uint8_t *ciphertext, *plaintext;
};
union open_cfw_smpi_sc_message {
    struct open_cfw_smpi_sc_header header;
    struct open_cfw_smpi_sc_auth_response authentication;
    struct open_cfw_smpi_sc_data_message data;
    struct open_cfw_smpi_sc_aes_message aes;
};

#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_smpi_sc_record) == 0x1CU,
    "G2 SMP SC record ABI changed");
_Static_assert(sizeof(struct open_cfw_smpi_sc_ccb) == 0x4CU,
    "G2 SMP CCB ABI changed");
_Static_assert(offsetof(struct open_cfw_smpi_sc_ccb, key_ready) == 0x44U,
    "G2 SMP keyReady offset changed");
#endif

#ifndef OPEN_CFW_SMPI_SC_CONFIG
#define OPEN_CFW_SMPI_SC_CONFIG \
    (**(struct open_cfw_smpi_sc_config **)(uintptr_t)0x200004B8U)
#endif
#ifndef OPEN_CFW_SMPI_SC_ZEROS
#define OPEN_CFW_SMPI_SC_ZEROS ((const uint8_t *)(uintptr_t)0x007856B0U)
#endif

extern void open_cfw_retained_cordio_wstr_reverse_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length);
extern void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16]);
extern void open_cfw_retained_cordio_sec_rand(uint8_t *buffer, uint16_t length);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);
extern void *open_cfw_runtime_memory_zero(void *destination, uint32_t size);
extern int open_cfw_retained_iar_memcmp(
    const void *left, const void *right, uint32_t size);
extern void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smpi_sc_ccb *ccb, void *message);
extern void open_cfw_cordio_smp_sc_act_authentication_select(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message);
extern void open_cfw_cordio_smp_sc_send_public_key(
    struct open_cfw_smpi_sc_ccb *ccb, struct open_cfw_smpi_sc_header *message);
extern void open_cfw_cordio_smp_sc_send_random(
    struct open_cfw_smpi_sc_ccb *ccb, struct open_cfw_smpi_sc_header *message,
    uint8_t *random);
extern void open_cfw_cordio_smp_sc_send_pairing_confirm(
    struct open_cfw_smpi_sc_ccb *ccb, struct open_cfw_smpi_sc_header *message,
    uint8_t *confirm);
extern void open_cfw_cordio_smp_sc_send_dh_key_check(
    struct open_cfw_smpi_sc_ccb *ccb, struct open_cfw_smpi_sc_header *message,
    uint8_t *check);
extern void open_cfw_cordio_smp_sc_calculate_f4(
    struct open_cfw_smpi_sc_ccb *ccb, struct open_cfw_smpi_sc_header *message,
    uint8_t *u, uint8_t *v, uint8_t z, uint8_t *x);
extern uint8_t open_cfw_cordio_smp_sc_get_passkey_bit(
    struct open_cfw_smpi_sc_ccb *ccb);
extern void open_cfw_cordio_smp_sc_fail_with_reattempt(
    struct open_cfw_smpi_sc_ccb *ccb);
extern void open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message);
extern void open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message);
extern void open_cfw_cordio_smp_sc_act_calculate_shared_secret(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message);
extern void open_cfw_cordio_smp_db_pairing_failed(uint8_t connection_id);
extern uint8_t open_cfw_cordio_smp_main_get_sc_security_level(
    struct open_cfw_smpi_sc_ccb *ccb);
extern void open_cfw_cordio_dm_sec_master_smp_encrypt_request(
    uint8_t connection_id, uint8_t security_level, const uint8_t key[16]);

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_AUTH_SELECT_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_authentication_select(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{ open_cfw_cordio_smp_sc_act_authentication_select(ccb, message); }
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_SEND_PUBLIC_KEY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_send_public_key(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    ccb->next_command = OPEN_CFW_SMPI_SC_CMD_PUBLIC_KEY;
    open_cfw_cordio_smp_sc_send_public_key(ccb, &message->header);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_JWNC_SETUP_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_jwnc_setup(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_scratch *scratch = ccb->secure_connections->scratch;
    (void)message;
    open_cfw_retained_cordio_sec_rand(scratch->initiator_random, 16U);
    open_cfw_retained_cordio_calc128_copy(scratch->ra, OPEN_CFW_SMPI_SC_ZEROS);
    open_cfw_retained_cordio_calc128_copy(scratch->rb, OPEN_CFW_SMPI_SC_ZEROS);
    ccb->next_command = OPEN_CFW_SMPI_SC_CMD_CONFIRM;
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_JWNC_SEND_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_jwnc_send_random(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_scratch *scratch = ccb->secure_connections->scratch;
    open_cfw_retained_cordio_wstr_reverse_copy(scratch->peer_cb,
        message->data.packet + OPEN_CFW_SMPI_SC_PDU_OFFSET + 1U, 16U);
    ccb->next_command = OPEN_CFW_SMPI_SC_CMD_RANDOM;
    open_cfw_cordio_smp_sc_send_random(ccb, &message->header,
        scratch->initiator_random);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_JWNC_F4_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_jwnc_calculate_f4(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    open_cfw_retained_cordio_wstr_reverse_copy(
        ccb->secure_connections->scratch->responder_random,
        message->data.packet + OPEN_CFW_SMPI_SC_PDU_OFFSET + 1U, 16U);
    open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(ccb, message);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_JWNC_G2_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_jwnc_calculate_g2(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    if (open_cfw_retained_iar_memcmp(
            ccb->secure_connections->scratch->peer_cb,
            message->aes.ciphertext, 16U) != 0) {
        open_cfw_cordio_smp_sc_fail_with_reattempt(ccb);
    } else {
        open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(ccb, message);
    }
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_PASSKEY_CA_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_passkey_calculate_ca(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_record *sc = ccb->secure_connections;
    if (sc->passkey_position == 0U) {
        open_cfw_retained_cordio_calc128_copy(sc->scratch->ra, OPEN_CFW_SMPI_SC_ZEROS);
        open_cfw_retained_cordio_calc128_copy(sc->scratch->rb, OPEN_CFW_SMPI_SC_ZEROS);
        if (message->authentication.length <= 3U) {
            open_cfw_retained_cordio_wstr_reverse_copy(&sc->scratch->ra[13],
                message->authentication.data, message->authentication.length);
            open_cfw_retained_cordio_wstr_reverse_copy(&sc->scratch->rb[13],
                message->authentication.data, message->authentication.length);
        }
    }
    open_cfw_retained_cordio_sec_rand(sc->scratch->initiator_random, 16U);
    open_cfw_cordio_smp_sc_calculate_f4(ccb, &message->header,
        sc->local_public_key->x, sc->peer_public_key->x,
        open_cfw_cordio_smp_sc_get_passkey_bit(ccb),
        sc->scratch->initiator_random);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_PASSKEY_CB_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_passkey_calculate_cb(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_record *sc = ccb->secure_connections;
    open_cfw_retained_cordio_wstr_reverse_copy(sc->scratch->responder_random,
        message->data.packet + OPEN_CFW_SMPI_SC_PDU_OFFSET + 1U, 16U);
    open_cfw_cordio_smp_sc_calculate_f4(ccb, &message->header,
        sc->peer_public_key->x, sc->local_public_key->x,
        open_cfw_cordio_smp_sc_get_passkey_bit(ccb),
        sc->scratch->responder_random);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_PASSKEY_SEND_CONFIRM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_passkey_send_confirm(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{ open_cfw_cordio_smp_sc_send_pairing_confirm(ccb, &message->header, message->aes.ciphertext); }
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_PASSKEY_SEND_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_passkey_send_random(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_scratch *scratch = ccb->secure_connections->scratch;
    open_cfw_retained_cordio_wstr_reverse_copy(scratch->peer_cb,
        message->data.packet + OPEN_CFW_SMPI_SC_PDU_OFFSET + 1U, 16U);
    ccb->next_command = OPEN_CFW_SMPI_SC_CMD_RANDOM;
    open_cfw_cordio_smp_sc_send_random(ccb, &message->header,
        scratch->initiator_random);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_PASSKEY_CHECK_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_passkey_check(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_header header = {ccb->connection_id, 0U, 0U};
    if (open_cfw_retained_iar_memcmp(
            ccb->secure_connections->scratch->peer_cb,
            message->aes.ciphertext, 16U) != 0) {
        open_cfw_cordio_smp_sc_fail_with_reattempt(ccb);
        return;
    }
    ccb->secure_connections->passkey_position++;
    if (ccb->secure_connections->passkey_position >= OPEN_CFW_SMPI_SC_PASSKEY_BITS) {
        header.event = OPEN_CFW_SMPI_SC_EVENT_PASSKEY_COMPLETE;
    } else {
        ccb->next_command = OPEN_CFW_SMPI_SC_CMD_CONFIRM;
        header.event = OPEN_CFW_SMPI_SC_EVENT_PASSKEY_NEXT;
    }
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, &header);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_OOB_CB_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_oob_calculate_cb(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_record *sc = ccb->secure_connections;
    if (ccb->pair_response[OPEN_CFW_SMPI_SC_PAIR_OOB] != OPEN_CFW_SMPI_SC_OOB_PRESENT)
        open_cfw_retained_cordio_calc128_copy(sc->scratch->ra, OPEN_CFW_SMPI_SC_ZEROS);
    if (ccb->pair_request[OPEN_CFW_SMPI_SC_PAIR_OOB] == OPEN_CFW_SMPI_SC_OOB_PRESENT) {
        open_cfw_cordio_smp_sc_calculate_f4(ccb, &message->header,
            sc->peer_public_key->x, sc->peer_public_key->x, 0U, sc->scratch->rb);
    } else {
        struct open_cfw_smpi_sc_aes_message complete;
        open_cfw_retained_cordio_calc128_copy(sc->scratch->rb, OPEN_CFW_SMPI_SC_ZEROS);
        complete.header.param = ccb->connection_id;
        complete.header.event = OPEN_CFW_SMPI_SC_EVENT_CMAC_COMPLETE;
        complete.header.status = 0U;
        complete.plaintext = NULL;
        open_cfw_retained_cordio_smp_state_machine_execute(ccb, &complete);
    }
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_OOB_SEND_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_oob_send_random(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_scratch *scratch = ccb->secure_connections->scratch;
    if (ccb->pair_request[OPEN_CFW_SMPI_SC_PAIR_OOB] == OPEN_CFW_SMPI_SC_OOB_PRESENT &&
        open_cfw_retained_iar_memcmp(
            scratch->peer_cb, message->aes.ciphertext, 16U) != 0) {
        open_cfw_cordio_smp_sc_fail_with_reattempt(ccb);
        return;
    }
    ccb->next_command = OPEN_CFW_SMPI_SC_CMD_RANDOM;
    open_cfw_retained_cordio_sec_rand(scratch->initiator_random, 16U);
    open_cfw_cordio_smp_sc_send_random(ccb, &message->header,
        scratch->initiator_random);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_OOB_PROCESS_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_oob_process_random(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    open_cfw_retained_cordio_wstr_reverse_copy(
        ccb->secure_connections->scratch->responder_random,
        message->data.packet + OPEN_CFW_SMPI_SC_PDU_OFFSET + 1U, 16U);
    open_cfw_cordio_smp_sc_act_calculate_shared_secret(ccb, message);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_DH_SEND_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_dh_key_check_send(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    struct open_cfw_smpi_sc_scratch *scratch = ccb->secure_connections->scratch;
    open_cfw_retained_cordio_wstr_reverse_copy(
        scratch->responder_random, message->aes.ciphertext, 16U);
    ccb->next_command = OPEN_CFW_SMPI_SC_CMD_DH_CHECK;
    open_cfw_cordio_smp_sc_send_dh_key_check(ccb, &message->header,
        scratch->initiator_random);
}
#endif

#if OPEN_CFW_SMPI_SC_ALL || defined(OPEN_CFW_SMPI_SC_DH_VERIFY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpi_sc_dh_key_check_verify(
    struct open_cfw_smpi_sc_ccb *ccb, union open_cfw_smpi_sc_message *message)
{
    uint8_t *peer = message->data.packet + OPEN_CFW_SMPI_SC_PDU_OFFSET + 1U;
    if (open_cfw_retained_iar_memcmp(peer,
            ccb->secure_connections->scratch->responder_random, 16U) == 0) {
        uint8_t key[16];
        uint8_t length = ccb->pair_request[OPEN_CFW_SMPI_SC_PAIR_MAX_KEY] <
                ccb->pair_response[OPEN_CFW_SMPI_SC_PAIR_MAX_KEY] ?
            ccb->pair_request[OPEN_CFW_SMPI_SC_PAIR_MAX_KEY] :
            ccb->pair_response[OPEN_CFW_SMPI_SC_PAIR_MAX_KEY];
        open_cfw_iar_memcpy_void(key,
            ccb->secure_connections->ltk->temporary_ltk, length);
        open_cfw_runtime_memory_zero(key + length, 16U - length);
        /* r20/R4 behavior present in G2 and absent from the r19 oracle. */
        ccb->key_ready = 1U;
        open_cfw_cordio_dm_sec_master_smp_encrypt_request(ccb->connection_id,
            open_cfw_cordio_smp_main_get_sc_security_level(ccb), key);
    } else {
        struct open_cfw_smpi_sc_header header;
        header.param = ccb->connection_id;
        header.status = OPEN_CFW_SMPI_SC_ERROR_DH_CHECK;
        ccb->attempts++;
        open_cfw_cordio_smp_db_pairing_failed(ccb->connection_id);
        header.event = ccb->attempts == OPEN_CFW_SMPI_SC_CONFIG.maximum_attempts ?
            OPEN_CFW_SMPI_SC_EVENT_MAX_ATTEMPTS : OPEN_CFW_SMPI_SC_EVENT_DH_FAILURE;
        open_cfw_retained_cordio_smp_state_machine_execute(ccb, &header);
    }
}
#endif
