/*
 * SPDX-License-Identifier: Apache-2.0
 * Production adapter for the ten Packetcraft Cordio r20.05c legacy SMP
 * responder actions linked by G2 2.2.6.10.
 */
#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMPR_SEND_SECURITY_REQUEST_ONLY) && \
 !defined(OPEN_CFW_SMPR_PROCESS_PAIR_REQUEST_ONLY) && \
 !defined(OPEN_CFW_SMPR_SEND_PAIR_RESPONSE_ONLY) && \
 !defined(OPEN_CFW_SMPR_PROCESS_PAIR_CONFIRM_ONLY) && \
 !defined(OPEN_CFW_SMPR_PROCESS_PAIR_CONFIRM_CALCULATE_ONLY) && \
 !defined(OPEN_CFW_SMPR_CONFIRM_VERIFY_ONLY) && \
 !defined(OPEN_CFW_SMPR_SEND_PAIR_RANDOM_ONLY) && \
 !defined(OPEN_CFW_SMPR_SETUP_KEY_DISTRIBUTION_ONLY) && \
 !defined(OPEN_CFW_SMPR_SEND_KEY_ONLY) && \
 !defined(OPEN_CFW_SMPR_RECEIVE_KEY_ONLY)
#define OPEN_CFW_SMPR_ALL 1
#else
#define OPEN_CFW_SMPR_ALL 0
#endif

#define OPEN_CFW_SMPR_PACKET_OFFSET 8U
#define OPEN_CFW_SMPR_PAIR_BYTES 7U
#define OPEN_CFW_SMPR_RANDOM_BYTES 16U
#define OPEN_CFW_SMPR_KEY_BYTES 16U
#define OPEN_CFW_SMPR_PAIR_AUTH 3U
#define OPEN_CFW_SMPR_PAIR_MAX_KEY 4U
#define OPEN_CFW_SMPR_PAIR_INITIATOR_KEYS 5U
#define OPEN_CFW_SMPR_PAIR_RESPONDER_KEYS 6U
#define OPEN_CFW_SMPR_CMD_PAIR_RESPONSE 2U
#define OPEN_CFW_SMPR_CMD_PAIR_CONFIRM 3U
#define OPEN_CFW_SMPR_CMD_PAIR_RANDOM 4U
#define OPEN_CFW_SMPR_CMD_ENCRYPTION_INFO 6U
#define OPEN_CFW_SMPR_CMD_IDENTITY_INFO 8U
#define OPEN_CFW_SMPR_CMD_SIGNING_INFO 10U
#define OPEN_CFW_SMPR_CMD_SECURITY_REQUEST 11U
#define OPEN_CFW_SMPR_CMD_PUBLIC_KEY 12U
#define OPEN_CFW_SMPR_AUTH_MITM 4U
#define OPEN_CFW_SMPR_AUTH_SC 8U
#define OPEN_CFW_SMPR_KEY_ENCRYPTION 1U
#define OPEN_CFW_SMPR_KEY_IDENTITY 2U
#define OPEN_CFW_SMPR_KEY_SIGNING 4U
#define OPEN_CFW_SMPR_EVENT_CANCEL 3U
#define OPEN_CFW_SMPR_EVENT_MAX_ATTEMPTS 13U
#define OPEN_CFW_SMPR_EVENT_PAIRING_COMPLETE 14U
#define OPEN_CFW_SMPR_DM_PAIR_INDICATION 49U
#define OPEN_CFW_SMPR_ERROR_CONFIRM 4U
#define OPEN_CFW_SMPR_ERROR_UNSPECIFIED 8U
#define OPEN_CFW_SMPR_SECURITY_ENCRYPTED 1U
#define OPEN_CFW_SMPR_SECURITY_AUTHENTICATED 2U
#define OPEN_CFW_SMPR_IDLE_PAIRING 1U
#define OPEN_CFW_SMPR_CONNECTION_BUSY 1U

struct open_cfw_smpr_header { uint16_t param; uint8_t event, status; };
struct open_cfw_smpr_timer {
    uint32_t next; struct open_cfw_smpr_header message; uint32_t ticks;
    uint8_t handler_id, is_started, reserved[2];
};
struct open_cfw_smpr_ltk { uint8_t key[16], random[8]; uint16_t diversifier; };
struct open_cfw_smpr_irk { uint8_t key[16], address[6], address_type; };
union open_cfw_smpr_key_data {
    struct open_cfw_smpr_ltk ltk; struct open_cfw_smpr_irk irk; uint8_t csrk[16];
};
struct open_cfw_smpr_key_indication {
    struct open_cfw_smpr_header header; union open_cfw_smpr_key_data key_data;
    uint8_t type, security_level, encryption_key_length;
};
union open_cfw_smpr_scratch {
    struct { uint8_t b1[16], b2[16], b3[16], b4[16]; } buffers;
    struct open_cfw_smpr_key_indication key_indication;
};
struct open_cfw_smpr_sc { uint8_t lesc_enabled, reserved[27]; };
struct open_cfw_smpr_ccb {
    struct open_cfw_smpr_timer response_timer, wait_timer;
    uint8_t pair_request[7], pair_response[7], reserved46[2];
    union open_cfw_smpr_scratch *scratch; uint8_t *queued_packet;
    uint16_t handle; uint8_t initiator, security_request, flow_disabled;
    uint8_t connection_id, state, next_command, authentication, token, attempts;
    uint8_t last_sent_key, key_ready, reserved69[3]; struct open_cfw_smpr_sc *secure_connections;
};
struct open_cfw_smpr_control_block {
    struct open_cfw_smpr_ccb connections[3]; const void *slave_interface;
    const void *master_interface; uint8_t handler_id, reserved237[3];
    uint8_t (*process_pairing)(struct open_cfw_smpr_ccb *, uint8_t *, uint8_t *);
    void (*process_authentication)(struct open_cfw_smpr_ccb *, uint8_t, uint8_t);
    uint8_t lesc_supported, reserved249[3];
};
struct open_cfw_smpr_config {
    uint32_t attempt_timeout; uint8_t io_capability, minimum_key_length;
    uint8_t maximum_key_length, maximum_attempts, authentication, reserved9[3];
    uint32_t maximum_attempt_timeout, attempt_decrement_timeout;
    uint16_t attempt_exponent;
};
struct open_cfw_smpr_pair_message {
    struct open_cfw_smpr_header header;
    uint8_t oob, authentication, initiator_keys, responder_keys;
};
struct open_cfw_smpr_security_message {
    struct open_cfw_smpr_header header; uint8_t authentication;
};
struct open_cfw_smpr_data_message { struct open_cfw_smpr_header header; uint8_t *packet; };
struct open_cfw_smpr_aes_message { struct open_cfw_smpr_header header; uint8_t *ciphertext, *plaintext; };
union open_cfw_smpr_message {
    struct open_cfw_smpr_header header; struct open_cfw_smpr_pair_message pair;
    struct open_cfw_smpr_security_message security;
    struct open_cfw_smpr_data_message data; struct open_cfw_smpr_aes_message aes;
};

#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(union open_cfw_smpr_scratch) == 64U, "SMP scratch ABI");
_Static_assert(sizeof(struct open_cfw_smpr_ccb) == 0x4CU, "SMP CCB ABI");
_Static_assert(offsetof(struct open_cfw_smpr_ccb, scratch) == 0x30U, "scratch ABI");
_Static_assert(offsetof(struct open_cfw_smpr_ccb, key_ready) == 0x44U, "keyReady ABI");
_Static_assert(sizeof(struct open_cfw_smpr_control_block) == 0xFCU, "SMP CB ABI");
#endif

#ifndef OPEN_CFW_SMPR_CONTROL_BLOCK
#define OPEN_CFW_SMPR_CONTROL_BLOCK (*(struct open_cfw_smpr_control_block *)(uintptr_t)0x20070AECU)
#endif
#ifndef OPEN_CFW_SMPR_CONFIG
#define OPEN_CFW_SMPR_CONFIG (**(struct open_cfw_smpr_config **)(uintptr_t)0x200004B8U)
#endif

extern void *open_cfw_retained_cordio_wsf_buffer_alloc(uint16_t size);
extern void open_cfw_retained_cordio_dm_conn_set_idle(uint8_t, uint16_t, uint8_t);
extern void open_cfw_cordio_dm_sec_smp_callback_execute(void *message);
extern void open_cfw_retained_cordio_sec_rand(uint8_t *, uint16_t);
extern uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length);
extern void open_cfw_cordio_smp_main_send_packet(struct open_cfw_smpr_ccb *, uint8_t *);
extern void open_cfw_cordio_smp_main_calculate_c1_part1(
    struct open_cfw_smpr_ccb *, const uint8_t *, const uint8_t *);
extern void open_cfw_cordio_smp_main_calculate_s1(
    struct open_cfw_smpr_ccb *, const uint8_t *, const uint8_t *, const uint8_t *);
extern void open_cfw_cordio_smp_act_start_response_timer(struct open_cfw_smpr_ccb *);
extern uint8_t open_cfw_cordio_smp_act_receive_key(
    struct open_cfw_smpr_ccb *, struct open_cfw_smpr_key_indication *, uint8_t *, uint8_t);
extern uint8_t open_cfw_cordio_smp_act_send_key(struct open_cfw_smpr_ccb *, uint8_t);
extern void open_cfw_cordio_smp_act_execute(struct open_cfw_smpr_ccb *, union open_cfw_smpr_message *);
extern void open_cfw_cordio_smp_db_pairing_failed(uint8_t);
extern void open_cfw_iar_memcpy_void(void *, const void *, uint32_t);
extern void *open_cfw_runtime_memory_zero(void *, uint32_t);
extern int open_cfw_retained_iar_memcmp(const void *, const void *, uint32_t);

void open_cfw_cordio_smpr_send_key(struct open_cfw_smpr_ccb *, union open_cfw_smpr_message *);
void open_cfw_cordio_smpr_process_pair_confirm(struct open_cfw_smpr_ccb *, union open_cfw_smpr_message *);

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_SEND_SECURITY_REQUEST_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_send_security_request(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    uint8_t *packet;
    open_cfw_cordio_smp_act_start_response_timer(ccb);
    packet = open_cfw_cordio_smp_main_message_allocate(OPEN_CFW_SMPR_PACKET_OFFSET + 2U);
    if (packet != NULL) {
        packet[OPEN_CFW_SMPR_PACKET_OFFSET] = OPEN_CFW_SMPR_CMD_SECURITY_REQUEST;
        packet[OPEN_CFW_SMPR_PACKET_OFFSET + 1U] = message->security.authentication;
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_PROCESS_PAIR_REQUEST_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_process_pair_request(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    struct {
        struct open_cfw_smpr_header header;
        uint8_t authentication, oob, initiator_keys, responder_keys;
    } indication;
    uint8_t *request;
    if (ccb->scratch == NULL)
        ccb->scratch = open_cfw_retained_cordio_wsf_buffer_alloc((uint16_t)sizeof(*ccb->scratch));
    if (ccb->scratch == NULL) {
        message->header.status = OPEN_CFW_SMPR_ERROR_UNSPECIFIED;
        message->header.event = OPEN_CFW_SMPR_EVENT_CANCEL;
        open_cfw_cordio_smp_act_execute(ccb, message);
        return;
    }
    open_cfw_retained_cordio_dm_conn_set_idle(ccb->connection_id,
        OPEN_CFW_SMPR_IDLE_PAIRING, OPEN_CFW_SMPR_CONNECTION_BUSY);
    request = message->data.packet + OPEN_CFW_SMPR_PACKET_OFFSET;
    open_cfw_iar_memcpy_void(ccb->pair_request, request, OPEN_CFW_SMPR_PAIR_BYTES);
    indication.authentication = request[OPEN_CFW_SMPR_PAIR_AUTH];
    indication.oob = request[2U];
    indication.initiator_keys = request[OPEN_CFW_SMPR_PAIR_INITIATOR_KEYS];
    indication.responder_keys = request[OPEN_CFW_SMPR_PAIR_RESPONDER_KEYS];
    indication.header.param = ccb->connection_id;
    indication.header.event = OPEN_CFW_SMPR_DM_PAIR_INDICATION;
    indication.header.status = 0U;
    open_cfw_cordio_dm_sec_smp_callback_execute(&indication);
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_SEND_PAIR_RESPONSE_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_send_pair_response(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    uint8_t *packet, *p = ccb->pair_response;
    uint8_t oob, display;
    *p++ = OPEN_CFW_SMPR_CMD_PAIR_RESPONSE;
    *p++ = OPEN_CFW_SMPR_CONFIG.io_capability;
    *p++ = message->pair.oob;
    *p++ = message->pair.authentication;
    *p++ = OPEN_CFW_SMPR_CONFIG.maximum_key_length;
    *p++ = message->pair.initiator_keys;
    *p = message->pair.responder_keys;
    if (!OPEN_CFW_SMPR_CONTROL_BLOCK.process_pairing(ccb, &oob, &display)) return;
    ccb->next_command =
        (ccb->pair_request[OPEN_CFW_SMPR_PAIR_AUTH] &
         message->pair.authentication & OPEN_CFW_SMPR_AUTH_SC) == OPEN_CFW_SMPR_AUTH_SC ?
        OPEN_CFW_SMPR_CMD_PUBLIC_KEY : OPEN_CFW_SMPR_CMD_PAIR_CONFIRM;
    open_cfw_cordio_smp_act_start_response_timer(ccb);
    packet = open_cfw_cordio_smp_main_message_allocate(
        OPEN_CFW_SMPR_PACKET_OFFSET + OPEN_CFW_SMPR_PAIR_BYTES);
    if (packet != NULL) {
        open_cfw_iar_memcpy_void(packet + OPEN_CFW_SMPR_PACKET_OFFSET,
            ccb->pair_response, OPEN_CFW_SMPR_PAIR_BYTES);
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
    OPEN_CFW_SMPR_CONTROL_BLOCK.process_authentication(ccb, oob, display);
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_PROCESS_PAIR_CONFIRM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_process_pair_confirm(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    open_cfw_iar_memcpy_void(ccb->scratch->buffers.b3,
        message->data.packet + OPEN_CFW_SMPR_PACKET_OFFSET + 1U, 16U);
    ccb->next_command = 0U;
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_PROCESS_PAIR_CONFIRM_CALCULATE_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_process_pair_confirm_calculate(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    open_cfw_cordio_smpr_process_pair_confirm(ccb, message);
    open_cfw_retained_cordio_sec_rand(ccb->scratch->buffers.b4, OPEN_CFW_SMPR_RANDOM_BYTES);
    open_cfw_cordio_smp_main_calculate_c1_part1(ccb,
        ccb->scratch->buffers.b1, ccb->scratch->buffers.b4);
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_CONFIRM_VERIFY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_confirm_verify(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    if (open_cfw_retained_iar_memcmp(message->aes.ciphertext,
            ccb->scratch->buffers.b3, 16U) != 0) {
        ccb->attempts++;
        open_cfw_cordio_smp_db_pairing_failed(ccb->connection_id);
        message->header.status = OPEN_CFW_SMPR_ERROR_CONFIRM;
        message->header.event = ccb->attempts == OPEN_CFW_SMPR_CONFIG.maximum_attempts ?
            OPEN_CFW_SMPR_EVENT_MAX_ATTEMPTS : OPEN_CFW_SMPR_EVENT_CANCEL;
        open_cfw_cordio_smp_act_execute(ccb, message);
        return;
    }
    open_cfw_cordio_smp_main_calculate_s1(ccb, ccb->scratch->buffers.b1,
        ccb->scratch->buffers.b4, ccb->scratch->buffers.b2);
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_SEND_PAIR_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_send_pair_random(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    uint8_t *packet;
    uint8_t length = ccb->pair_request[OPEN_CFW_SMPR_PAIR_MAX_KEY] <
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_MAX_KEY] ?
        ccb->pair_request[OPEN_CFW_SMPR_PAIR_MAX_KEY] :
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_MAX_KEY];
    open_cfw_iar_memcpy_void(ccb->scratch->buffers.b3, message->aes.ciphertext, length);
    open_cfw_runtime_memory_zero(ccb->scratch->buffers.b3 + length,
        OPEN_CFW_SMPR_KEY_BYTES - length);
    ccb->key_ready = 1U;
    open_cfw_cordio_smp_act_start_response_timer(ccb);
    packet = open_cfw_cordio_smp_main_message_allocate(OPEN_CFW_SMPR_PACKET_OFFSET + 17U);
    if (packet != NULL) {
        packet[OPEN_CFW_SMPR_PACKET_OFFSET] = OPEN_CFW_SMPR_CMD_PAIR_RANDOM;
        open_cfw_iar_memcpy_void(packet + OPEN_CFW_SMPR_PACKET_OFFSET + 1U,
            ccb->scratch->buffers.b4, OPEN_CFW_SMPR_RANDOM_BYTES);
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_SETUP_KEY_DISTRIBUTION_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_setup_key_distribution(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    ccb->next_command = 0U;
    open_cfw_cordio_smp_act_start_response_timer(ccb);
    ccb->scratch->key_indication.header.param = ccb->connection_id;
    ccb->scratch->key_indication.security_level =
        (ccb->authentication & OPEN_CFW_SMPR_AUTH_MITM) != 0U ?
        OPEN_CFW_SMPR_SECURITY_AUTHENTICATED : OPEN_CFW_SMPR_SECURITY_ENCRYPTED;
    ccb->scratch->key_indication.encryption_key_length =
        ccb->pair_request[OPEN_CFW_SMPR_PAIR_MAX_KEY] <
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_MAX_KEY] ?
        ccb->pair_request[OPEN_CFW_SMPR_PAIR_MAX_KEY] :
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_MAX_KEY];
    open_cfw_cordio_smpr_send_key(ccb, message);
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_SEND_KEY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_send_key(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    uint8_t distribution = ccb->pair_request[OPEN_CFW_SMPR_PAIR_RESPONDER_KEYS] &
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_RESPONDER_KEYS];
    if (ccb->next_command != 0U || !open_cfw_cordio_smp_act_send_key(ccb, distribution)) return;
    ccb->next_command = 0U;
    distribution = ccb->pair_request[OPEN_CFW_SMPR_PAIR_INITIATOR_KEYS] &
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_INITIATOR_KEYS];
    if ((distribution & OPEN_CFW_SMPR_KEY_ENCRYPTION) != 0U) {
        if (OPEN_CFW_SMPR_CONTROL_BLOCK.lesc_supported != 0U &&
            ccb->secure_connections != NULL && ccb->secure_connections->lesc_enabled != 0U) {
            if ((distribution & OPEN_CFW_SMPR_KEY_IDENTITY) != 0U)
                ccb->next_command = OPEN_CFW_SMPR_CMD_IDENTITY_INFO;
        } else ccb->next_command = OPEN_CFW_SMPR_CMD_ENCRYPTION_INFO;
    } else if ((distribution & OPEN_CFW_SMPR_KEY_IDENTITY) != 0U)
        ccb->next_command = OPEN_CFW_SMPR_CMD_IDENTITY_INFO;
    else if ((distribution & OPEN_CFW_SMPR_KEY_SIGNING) != 0U)
        ccb->next_command = OPEN_CFW_SMPR_CMD_SIGNING_INFO;
    if (ccb->next_command == 0U) {
        message->header.event = OPEN_CFW_SMPR_EVENT_PAIRING_COMPLETE;
        open_cfw_cordio_smp_act_execute(ccb, message);
    }
}
#endif

#if OPEN_CFW_SMPR_ALL || defined(OPEN_CFW_SMPR_RECEIVE_KEY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_receive_key(
    struct open_cfw_smpr_ccb *ccb, union open_cfw_smpr_message *message)
{
    uint8_t distribution = ccb->pair_request[OPEN_CFW_SMPR_PAIR_INITIATOR_KEYS] &
        ccb->pair_response[OPEN_CFW_SMPR_PAIR_INITIATOR_KEYS];
    if (open_cfw_cordio_smp_act_receive_key(ccb, &ccb->scratch->key_indication,
            message->data.packet, distribution)) {
        message->header.event = OPEN_CFW_SMPR_EVENT_PAIRING_COMPLETE;
        open_cfw_cordio_smp_act_execute(ccb, message);
    }
}
#endif
