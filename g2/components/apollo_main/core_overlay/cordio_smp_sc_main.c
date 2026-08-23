/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the eighteen Packetcraft Cordio r20.05c
 * smp_sc_main.c functions linked by G2 2.2.6.10.  The target SRAM layout is
 * explicit and the byte-array trace helper fixes the upstream short-final-line
 * count bug so diagnostic logging cannot stall pairing.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMP_SC_ALLOC_SCRATCH_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_FREE_SCRATCH_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_CMAC_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ALLOC_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_F4_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_INIT_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_CAT_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_CAT128_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_SEND_PUBLIC_KEY_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_SEND_DH_CHECK_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_SEND_RANDOM_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_SEND_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_PASSKEY_BIT_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_REATTEMPT_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_FAIL_REATTEMPT_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_EVENT_STRING_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_STATE_STRING_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_LOG_BYTES_ONLY)
#define OPEN_CFW_SMP_SC_ALL 1
#else
#define OPEN_CFW_SMP_SC_ALL 0
#endif

#define OPEN_CFW_SMP_SC_CONNECTION_COUNT 3U
#define OPEN_CFW_SMP_SC_SCRATCH_BYTES 96U
#define OPEN_CFW_SMP_SC_PUBLIC_KEY_BYTES 64U
#define OPEN_CFW_SMP_SC_LTK_BYTES 32U
#define OPEN_CFW_SMP_SC_PRIVATE_KEY_BYTES 32U
#define OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES 32U
#define OPEN_CFW_SMP_SC_RANDOM_BYTES 16U
#define OPEN_CFW_SMP_SC_F4_TEXT_BYTES 65U
#define OPEN_CFW_SMP_SC_PAYLOAD_OFFSET 8U
#define OPEN_CFW_SMP_SC_PUBLIC_KEY_PDU_BYTES 65U
#define OPEN_CFW_SMP_SC_VALUE_PDU_BYTES 17U
#define OPEN_CFW_SMP_SC_COMMAND_CONFIRM 3U
#define OPEN_CFW_SMP_SC_COMMAND_RANDOM 4U
#define OPEN_CFW_SMP_SC_COMMAND_PUBLIC_KEY 12U
#define OPEN_CFW_SMP_SC_COMMAND_DH_CHECK 13U
#define OPEN_CFW_SMP_SC_ERROR_CONFIRM_VALUE 4U
#define OPEN_CFW_SMP_SC_ERROR_UNSPECIFIED 8U
#define OPEN_CFW_SMP_SC_EVENT_CANCEL 3U
#define OPEN_CFW_SMP_SC_EVENT_MAX_ATTEMPTS 13U
#define OPEN_CFW_SMP_SC_EVENT_CMAC_COMPLETE 28U
#define OPEN_CFW_SMP_SC_IDLE_PAIRING 1U
#define OPEN_CFW_SMP_SC_CONNECTION_BUSY 1U

struct open_cfw_smp_sc_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_smp_sc_timer {
    uint32_t next;
    struct open_cfw_smp_sc_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t is_started;
    uint8_t reserved[2];
};

union open_cfw_smp_sc_legacy_scratch {
    uint8_t bytes[64];
    uint32_t alignment;
};

struct open_cfw_smp_sc_public_key {
    uint8_t x[OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES];
    uint8_t y[OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES];
};

struct open_cfw_smp_sc_scratch {
    uint8_t initiator_random[16];
    uint8_t responder_random[16];
    uint8_t ra[16];
    uint8_t rb[16];
    uint8_t peer_cb[16];
    uint8_t peer_ca_or_ea[16];
};

struct open_cfw_smp_sc_ltk {
    uint8_t mac[16];
    uint8_t temporary_ltk[16];
};

struct open_cfw_smp_sc_ccb {
    uint8_t lesc_enabled;
    uint8_t authentication_type;
    uint8_t keypress_notify;
    uint8_t passkey_position;
    uint8_t display;
    uint8_t reserved[3];
    struct open_cfw_smp_sc_public_key *peer_public_key;
    struct open_cfw_smp_sc_public_key *local_public_key;
    uint8_t *private_key;
    struct open_cfw_smp_sc_scratch *scratch;
    struct open_cfw_smp_sc_ltk *ltk;
};

struct open_cfw_smp_sc_main_ccb {
    struct open_cfw_smp_sc_timer response_timer;
    struct open_cfw_smp_sc_timer wait_timer;
    uint8_t pair_request[7];
    uint8_t pair_response[7];
    uint8_t reserved46[2];
    union open_cfw_smp_sc_legacy_scratch *legacy_scratch;
    uint8_t *queued_packet;
    uint16_t handle;
    uint8_t initiator;
    uint8_t security_request;
    uint8_t flow_disabled;
    uint8_t connection_id;
    uint8_t state;
    uint8_t next_command;
    uint8_t authentication;
    uint8_t token;
    uint8_t attempts;
    uint8_t last_sent_key;
    uint8_t key_ready;
    uint8_t reserved69[3];
    struct open_cfw_smp_sc_ccb *secure_connections;
};

struct open_cfw_smp_sc_control_block {
    struct open_cfw_smp_sc_main_ccb connections[OPEN_CFW_SMP_SC_CONNECTION_COUNT];
    const void *slave_interface;
    const void *master_interface;
    uint8_t handler_id;
    uint8_t reserved237[3];
    void *process_pairing;
    void *process_authentication;
    uint8_t lesc_supported;
    uint8_t reserved249[3];
};

struct open_cfw_smp_sc_config {
    uint32_t attempt_timeout;
    uint8_t io_capability;
    uint8_t minimum_key_length;
    uint8_t maximum_key_length;
    uint8_t maximum_attempts;
    uint8_t authentication;
    uint8_t reserved9[3];
    uint32_t maximum_attempt_timeout;
    uint32_t attempt_decrement_timeout;
    uint16_t attempt_exponent;
};

#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_smp_sc_ccb) == 0x1CU,
    "G2 SMP SC CCB ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_ccb, peer_public_key) == 0x08U,
    "G2 SMP SC peer-key offset changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_ccb, scratch) == 0x14U,
    "G2 SMP SC scratch offset changed");
_Static_assert(sizeof(struct open_cfw_smp_sc_main_ccb) == 0x4CU,
    "G2 SMP main CCB ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_main_ccb, connection_id) == 0x3DU,
    "G2 SMP connection-ID offset changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_main_ccb, attempts) == 0x42U,
    "G2 SMP attempts offset changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_main_ccb, secure_connections) == 0x48U,
    "G2 SMP SC pointer offset changed");
_Static_assert(sizeof(struct open_cfw_smp_sc_control_block) == 0xFCU,
    "G2 SMP control-block ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_config, maximum_attempts) == 7U,
    "G2 SMP max-attempts offset changed");
#endif

#ifndef OPEN_CFW_SMP_SC_CONTROL_BLOCK
#define OPEN_CFW_SMP_SC_CONTROL_BLOCK \
    (*(struct open_cfw_smp_sc_control_block *)(uintptr_t)0x20070AECU)
#endif

#ifndef OPEN_CFW_SMP_SC_RECORDS
#define OPEN_CFW_SMP_SC_RECORDS \
    ((struct open_cfw_smp_sc_ccb *)(uintptr_t)0x200728F4U)
#endif

#ifndef OPEN_CFW_SMP_SC_CONFIG
#define OPEN_CFW_SMP_SC_CONFIG \
    (**(struct open_cfw_smp_sc_config **)(uintptr_t)0x200004B8U)
#endif

extern void *open_cfw_retained_cordio_wsf_buffer_alloc(uint16_t size);
extern void open_cfw_retained_cordio_wsf_buffer_free(void *buffer);
extern uint8_t open_cfw_retained_cordio_sec_cmac(
    const uint8_t *key, uint8_t *text, uint16_t text_length,
    uint8_t handler_id, uint16_t parameter, uint8_t event);
extern void open_cfw_retained_cordio_dm_conn_set_idle(
    uint8_t connection_id, uint16_t idle_mask, uint8_t idle);
extern void open_cfw_retained_cordio_smp_start_response_timer(
    struct open_cfw_smp_sc_main_ccb *ccb);
extern uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length);
extern void open_cfw_retained_cordio_wstr_reverse_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length);
extern void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_sc_main_ccb *ccb, uint8_t *packet);
extern void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smp_sc_main_ccb *ccb, void *message);
extern void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16]);
extern struct open_cfw_smp_sc_main_ccb *
    open_cfw_cordio_smp_main_ccb_by_connection_id(uint8_t connection_id);
extern void open_cfw_cordio_smp_db_pairing_failed(uint8_t connection_id);
extern uint8_t *open_cfw_retained_cordio_smpi_state_string(uint8_t state);
extern uint8_t *open_cfw_retained_cordio_smpr_state_string(uint8_t state);
extern uint8_t open_cfw_retained_cordio_smp_sc_process_pairing(
    struct open_cfw_smp_sc_main_ccb *ccb, uint8_t *oob, uint8_t *display);
extern void open_cfw_retained_cordio_smp_sc_process_authentication(
    struct open_cfw_smp_sc_main_ccb *ccb, uint8_t oob, uint8_t display);
extern void open_cfw_retained_cordio_wsf_trace(const char *format, ...);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);

uint8_t *open_cfw_cordio_smp_sc_allocate(
    uint8_t size, struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message);
void open_cfw_cordio_smp_sc_cmac(
    const uint8_t *key, uint8_t *text, uint8_t text_length,
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message);
void open_cfw_cordio_smp_sc_cancel_with_reattempt(
    uint8_t connection_id, struct open_cfw_smp_sc_header *header,
    uint8_t status);

static __attribute__((unused)) void open_cfw_smp_sc_cancel(
    struct open_cfw_smp_sc_main_ccb *ccb, struct open_cfw_smp_sc_header *message)
{
    message->status = OPEN_CFW_SMP_SC_ERROR_UNSPECIFIED;
    message->event = OPEN_CFW_SMP_SC_EVENT_CANCEL;
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, message);
}

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_ALLOC_SCRATCH_ONLY)
uint8_t open_cfw_cordio_smp_sc_allocate_scratch_buffers(
    struct open_cfw_smp_sc_main_ccb *ccb)
{
    struct open_cfw_smp_sc_ccb *sc = ccb->secure_connections;
    if (sc->scratch == NULL) {
        sc->scratch = open_cfw_retained_cordio_wsf_buffer_alloc(
            OPEN_CFW_SMP_SC_SCRATCH_BYTES);
    }
    if (sc->peer_public_key == NULL) {
        sc->peer_public_key = open_cfw_retained_cordio_wsf_buffer_alloc(
            OPEN_CFW_SMP_SC_PUBLIC_KEY_BYTES);
    }
    if (sc->ltk == NULL) {
        sc->ltk = open_cfw_retained_cordio_wsf_buffer_alloc(
            OPEN_CFW_SMP_SC_LTK_BYTES);
    }
    if (sc->local_public_key == NULL) {
        sc->local_public_key = open_cfw_retained_cordio_wsf_buffer_alloc(
            OPEN_CFW_SMP_SC_PUBLIC_KEY_BYTES);
    }
    if (sc->private_key == NULL) {
        sc->private_key = open_cfw_retained_cordio_wsf_buffer_alloc(
            OPEN_CFW_SMP_SC_PRIVATE_KEY_BYTES);
    }
    return sc->scratch != NULL && sc->peer_public_key != NULL &&
        sc->ltk != NULL && sc->local_public_key != NULL &&
        sc->private_key != NULL ? 1U : 0U;
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_FREE_SCRATCH_ONLY)
void open_cfw_cordio_smp_sc_free_scratch_buffers(
    struct open_cfw_smp_sc_main_ccb *ccb)
{
    struct open_cfw_smp_sc_ccb *sc = ccb->secure_connections;
    if (sc->scratch != NULL) {
        open_cfw_retained_cordio_wsf_buffer_free(sc->scratch);
        sc->scratch = NULL;
    }
    if (sc->peer_public_key != NULL) {
        open_cfw_retained_cordio_wsf_buffer_free(sc->peer_public_key);
        sc->peer_public_key = NULL;
    }
    if (sc->ltk != NULL) {
        open_cfw_retained_cordio_wsf_buffer_free(sc->ltk);
        sc->ltk = NULL;
    }
    if (sc->local_public_key != NULL) {
        open_cfw_retained_cordio_wsf_buffer_free(sc->local_public_key);
        sc->local_public_key = NULL;
    }
    if (sc->private_key != NULL) {
        open_cfw_retained_cordio_wsf_buffer_free(sc->private_key);
        sc->private_key = NULL;
    }
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_CMAC_ONLY)
void open_cfw_cordio_smp_sc_cmac(
    const uint8_t *key, uint8_t *text, uint8_t text_length,
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message)
{
    if (open_cfw_retained_cordio_sec_cmac(
            key, text, text_length, OPEN_CFW_SMP_SC_CONTROL_BLOCK.handler_id,
            ccb->connection_id, OPEN_CFW_SMP_SC_EVENT_CMAC_COMPLETE) == 0U) {
        open_cfw_retained_cordio_wsf_buffer_free(text);
        open_cfw_smp_sc_cancel(ccb, message);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_ALLOC_ONLY)
uint8_t *open_cfw_cordio_smp_sc_allocate(
    uint8_t size, struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message)
{
    uint8_t *buffer = open_cfw_retained_cordio_wsf_buffer_alloc(size);
    if (buffer == NULL) {
        open_cfw_smp_sc_cancel(ccb, message);
    }
    return buffer;
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_F4_ONLY)
void open_cfw_cordio_smp_sc_calculate_f4(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message, uint8_t *u, uint8_t *v,
    uint8_t z, uint8_t *x)
{
    uint8_t *text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_F4_TEXT_BYTES, ccb, message);
    if (text != NULL) {
        open_cfw_iar_memcpy_void(text, u, OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES);
        open_cfw_iar_memcpy_void(
            text + OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES, v,
            OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES);
        text[OPEN_CFW_SMP_SC_F4_TEXT_BYTES - 1U] = z;
        open_cfw_cordio_smp_sc_cmac(
            x, text, OPEN_CFW_SMP_SC_F4_TEXT_BYTES, ccb, message);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_INIT_ONLY)
void open_cfw_cordio_smp_sc_init(void)
{
    uint8_t index;
    for (index = 0U; index < OPEN_CFW_SMP_SC_CONNECTION_COUNT; index++) {
        OPEN_CFW_SMP_SC_CONTROL_BLOCK.connections[index].secure_connections =
            &OPEN_CFW_SMP_SC_RECORDS[index];
    }
    OPEN_CFW_SMP_SC_CONTROL_BLOCK.process_pairing =
        (void *)open_cfw_retained_cordio_smp_sc_process_pairing;
    OPEN_CFW_SMP_SC_CONTROL_BLOCK.process_authentication =
        (void *)open_cfw_retained_cordio_smp_sc_process_authentication;
    OPEN_CFW_SMP_SC_CONTROL_BLOCK.lesc_supported = 1U;
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_CAT_ONLY)
uint8_t *open_cfw_cordio_smp_sc_cat(
    uint8_t *destination, const uint8_t *source, uint8_t length)
{
    open_cfw_iar_memcpy_void(destination, source, length);
    return destination + length;
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_CAT128_ONLY)
uint8_t *open_cfw_cordio_smp_sc_cat128(
    uint8_t *destination, uint8_t *source)
{
    open_cfw_retained_cordio_calc128_copy(destination, source);
    return destination + 16U;
}
#endif

static __attribute__((unused)) void open_cfw_smp_sc_begin_send(
    struct open_cfw_smp_sc_main_ccb *ccb)
{
    open_cfw_retained_cordio_dm_conn_set_idle(
        ccb->connection_id, OPEN_CFW_SMP_SC_IDLE_PAIRING,
        OPEN_CFW_SMP_SC_CONNECTION_BUSY);
    open_cfw_retained_cordio_smp_start_response_timer(ccb);
}

static __attribute__((unused)) uint8_t *open_cfw_smp_sc_pdu(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message, uint16_t length, uint8_t command)
{
    uint8_t *packet;
    open_cfw_smp_sc_begin_send(ccb);
    packet = open_cfw_cordio_smp_main_message_allocate(
        (uint16_t)(length + OPEN_CFW_SMP_SC_PAYLOAD_OFFSET));
    if (packet == NULL) {
        open_cfw_smp_sc_cancel(ccb, message);
        return NULL;
    }
    packet[OPEN_CFW_SMP_SC_PAYLOAD_OFFSET] = command;
    return packet;
}

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_SEND_PUBLIC_KEY_ONLY)
void open_cfw_cordio_smp_sc_send_public_key(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message)
{
    uint8_t *packet = open_cfw_smp_sc_pdu(
        ccb, message, OPEN_CFW_SMP_SC_PUBLIC_KEY_PDU_BYTES,
        OPEN_CFW_SMP_SC_COMMAND_PUBLIC_KEY);
    if (packet != NULL) {
        uint8_t *payload = packet + OPEN_CFW_SMP_SC_PAYLOAD_OFFSET + 1U;
        open_cfw_retained_cordio_wstr_reverse_copy(
            payload, ccb->secure_connections->local_public_key->x,
            OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES);
        open_cfw_retained_cordio_wstr_reverse_copy(
            payload + OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES,
            ccb->secure_connections->local_public_key->y,
            OPEN_CFW_SMP_SC_PUBLIC_KEY_COORD_BYTES);
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
}
#endif

static __attribute__((unused)) void open_cfw_smp_sc_send_value(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message, const uint8_t *value,
    uint8_t command)
{
    uint8_t *packet = open_cfw_smp_sc_pdu(
        ccb, message, OPEN_CFW_SMP_SC_VALUE_PDU_BYTES, command);
    if (packet != NULL) {
        open_cfw_retained_cordio_wstr_reverse_copy(
            packet + OPEN_CFW_SMP_SC_PAYLOAD_OFFSET + 1U, value,
            OPEN_CFW_SMP_SC_RANDOM_BYTES);
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
}

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_SEND_DH_CHECK_ONLY)
void open_cfw_cordio_smp_sc_send_dh_key_check(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message, uint8_t *check)
{
    open_cfw_smp_sc_send_value(
        ccb, message, check, OPEN_CFW_SMP_SC_COMMAND_DH_CHECK);
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_SEND_RANDOM_ONLY)
void open_cfw_cordio_smp_sc_send_random(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message, uint8_t *random)
{
    open_cfw_smp_sc_send_value(
        ccb, message, random, OPEN_CFW_SMP_SC_COMMAND_RANDOM);
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_SEND_CONFIRM_ONLY)
void open_cfw_cordio_smp_sc_send_pairing_confirm(
    struct open_cfw_smp_sc_main_ccb *ccb,
    struct open_cfw_smp_sc_header *message, uint8_t *confirm)
{
    open_cfw_smp_sc_send_value(
        ccb, message, confirm, OPEN_CFW_SMP_SC_COMMAND_CONFIRM);
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_PASSKEY_BIT_ONLY)
uint8_t open_cfw_cordio_smp_sc_get_passkey_bit(
    struct open_cfw_smp_sc_main_ccb *ccb)
{
    struct open_cfw_smp_sc_ccb *sc = ccb->secure_connections;
    uint8_t byte_index = (uint8_t)(15U - sc->passkey_position / 8U);
    uint8_t bit_index = (uint8_t)(sc->passkey_position % 8U);
    return (sc->scratch->ra[byte_index] & (uint8_t)(1U << bit_index)) != 0U ?
        0x81U : 0x80U;
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_REATTEMPT_ONLY)
void open_cfw_cordio_smp_sc_cancel_with_reattempt(
    uint8_t connection_id, struct open_cfw_smp_sc_header *header,
    uint8_t status)
{
    struct open_cfw_smp_sc_main_ccb *ccb =
        open_cfw_cordio_smp_main_ccb_by_connection_id(connection_id);
    ccb->attempts++;
    header->param = connection_id;
    header->status = status;
    open_cfw_cordio_smp_db_pairing_failed(connection_id);
    header->event = ccb->attempts == OPEN_CFW_SMP_SC_CONFIG.maximum_attempts ?
        OPEN_CFW_SMP_SC_EVENT_MAX_ATTEMPTS : OPEN_CFW_SMP_SC_EVENT_CANCEL;
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_FAIL_REATTEMPT_ONLY)
void open_cfw_cordio_smp_sc_fail_with_reattempt(
    struct open_cfw_smp_sc_main_ccb *ccb)
{
    struct open_cfw_smp_sc_header header;
    open_cfw_cordio_smp_sc_cancel_with_reattempt(
        ccb->connection_id, &header, OPEN_CFW_SMP_SC_ERROR_CONFIRM_VALUE);
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, &header);
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_EVENT_STRING_ONLY)
uint8_t *open_cfw_cordio_smp_sc_event_string(uint8_t event)
{
    switch (event) {
    case 1U: return (uint8_t *)(uintptr_t)(const void *)"API_PAIR_REQ";
    case 2U: return (uint8_t *)(uintptr_t)(const void *)"API_PAIR_RSP";
    case 3U: return (uint8_t *)(uintptr_t)(const void *)"API_CANCEL_REQ";
    case 4U: return (uint8_t *)(uintptr_t)(const void *)"API_AUTH_RSP";
    case 5U: return (uint8_t *)(uintptr_t)(const void *)"API_SECURITY_REQ";
    case 6U: return (uint8_t *)(uintptr_t)(const void *)"CMD_PKT";
    case 7U: return (uint8_t *)(uintptr_t)(const void *)"CMD_PAIRING_FAILED";
    case 8U: return (uint8_t *)(uintptr_t)(const void *)"DM_ENCRYPT_CMPL";
    case 9U: return (uint8_t *)(uintptr_t)(const void *)"DM_ENCRYPT_FAILED";
    case 10U: return (uint8_t *)(uintptr_t)(const void *)"DM_CONN_CLOSE";
    case 11U: return (uint8_t *)(uintptr_t)(const void *)"WSF_AES_CMPL";
    case 12U: return (uint8_t *)(uintptr_t)(const void *)"INT_SEND_NEXT_KEY";
    case 13U: return (uint8_t *)(uintptr_t)(const void *)"INT_MAX_ATTEMPTS";
    case 14U: return (uint8_t *)(uintptr_t)(const void *)"INT_PAIRING_CMPL";
    case 15U: return (uint8_t *)(uintptr_t)(const void *)"INT_RSP_TIMEOUT";
    case 16U: return (uint8_t *)(uintptr_t)(const void *)"INT_WI_TIMEOUT";
    case 17U: return (uint8_t *)(uintptr_t)(const void *)"INT_LESC";
    case 18U: return (uint8_t *)(uintptr_t)(const void *)"INT_LEGACY";
    case 19U: return (uint8_t *)(uintptr_t)(const void *)"INT_JW_NC";
    case 20U: return (uint8_t *)(uintptr_t)(const void *)"INT_PASSKEY";
    case 21U: return (uint8_t *)(uintptr_t)(const void *)"INT_OOB";
    case 22U: return (uint8_t *)(uintptr_t)(const void *)"API_USER_CONFIRM";
    case 23U: return (uint8_t *)(uintptr_t)(const void *)"API_USER_KEYPRESS";
    case 24U: return (uint8_t *)(uintptr_t)(const void *)"API_KEYPRESS_CMPL";
    case 25U: return (uint8_t *)(uintptr_t)(const void *)"WSF_ECC_CMPL";
    case 26U: return (uint8_t *)(uintptr_t)(const void *)"INT_PK_NEXT";
    case 27U: return (uint8_t *)(uintptr_t)(const void *)"INT_PK_CMPL";
    case 28U: return (uint8_t *)(uintptr_t)(const void *)"WSF_CMAC_CMPL";
    case 29U: return (uint8_t *)(uintptr_t)(const void *)"DH_CHECK_FAILURE";
    case 31U: return (uint8_t *)(uintptr_t)(const void *)"INT_CLEANUP";
    default: return (uint8_t *)(uintptr_t)(const void *)"Unknown";
    }
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_STATE_STRING_ONLY)
uint8_t *open_cfw_cordio_smp_sc_state_string(uint8_t state)
{
    return OPEN_CFW_SMP_SC_CONTROL_BLOCK.connections[0].initiator != 0U ?
        open_cfw_retained_cordio_smpi_state_string(state) :
        open_cfw_retained_cordio_smpr_state_string(state);
}
#endif

#if OPEN_CFW_SMP_SC_ALL || defined(OPEN_CFW_SMP_SC_LOG_BYTES_ONLY)
void open_cfw_cordio_smp_sc_log_byte_array(
    char *prefix, uint8_t *array, uint8_t length)
{
    char line[39];
    uint8_t consumed = 0U;
    open_cfw_retained_cordio_wsf_trace(prefix);
    while (consumed < length) {
        uint8_t count = (uint8_t)(length - consumed);
        uint8_t index;
        uint8_t position = 0U;
        if (count > 16U) {
            count = 16U;
        }
        line[position++] = '[';
        for (index = 0U; index < count; index++, consumed++) {
            uint8_t value;
            if (index != 0U && (index % 4U) == 0U) {
                line[position++] = ' ';
            }
            value = array[consumed];
            line[position++] = (char)((value >> 4U) < 10U ?
                '0' + (value >> 4U) : 'a' + (value >> 4U) - 10U);
            value &= 0x0FU;
            line[position++] = (char)(value < 10U ?
                '0' + value : 'a' + value - 10U);
        }
        line[position++] = ']';
        line[position] = '\0';
        open_cfw_retained_cordio_wsf_trace(line);
    }
}
#endif
