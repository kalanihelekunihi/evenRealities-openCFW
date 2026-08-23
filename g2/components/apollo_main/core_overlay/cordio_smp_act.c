/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the 25 Packetcraft Cordio r20.05c smp_act.c
 * functions linked by G2 2.2.6.10.  The implementation keeps the recovered
 * 32-bit SRAM ABI explicit and is compiled one routed leaf at a time.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMP_ACT_START_TIMER_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_NONE_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_CLEANUP_CORE_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_CLEANUP_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_SEND_FAIL_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_PAIR_FAIL_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_SEC_TIMEOUT_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_PAIR_CANCEL_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_STORE_PIN_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_PROCESS_PAIRING_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_AUTH_REQUEST_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_CONFIRM_CALC1_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_CONFIRM_CALC2_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_SEND_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_VERIFY_CALC1_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_VERIFY_CALC2_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_SEND_KEY_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_RECEIVE_KEY_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_MAX_ATTEMPTS_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_ATTEMPT_RECEIVED_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_NOTIFY_ATTEMPTS_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_NOTIFY_TIMEOUT_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_CHECK_ATTEMPTS_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_PAIR_COMPLETE_ONLY) && \
    !defined(OPEN_CFW_SMP_ACT_EXECUTE_ONLY)
#define OPEN_CFW_SMP_ACT_ALL 1
#else
#define OPEN_CFW_SMP_ACT_ALL 0
#endif

#define OPEN_CFW_SMP_ACT_PACKET_OFFSET 8U
#define OPEN_CFW_SMP_ACT_PIN_BYTES 4U
#define OPEN_CFW_SMP_ACT_OOB_BYTES 16U
#define OPEN_CFW_SMP_ACT_RANDOM_BYTES 16U
#define OPEN_CFW_SMP_ACT_RANDOM8_BYTES 8U
#define OPEN_CFW_SMP_ACT_CONFIRM_BYTES 16U
#define OPEN_CFW_SMP_ACT_PAIR_FAIL_PACKET_BYTES 2U
#define OPEN_CFW_SMP_ACT_CONFIRM_PACKET_BYTES 17U
#define OPEN_CFW_SMP_ACT_ENCRYPT_PACKET_BYTES 17U
#define OPEN_CFW_SMP_ACT_TIMEOUT_SECONDS 30U

#define OPEN_CFW_SMP_ACT_PAIR_IO 1U
#define OPEN_CFW_SMP_ACT_PAIR_OOB 2U
#define OPEN_CFW_SMP_ACT_PAIR_AUTH 3U
#define OPEN_CFW_SMP_ACT_PAIR_MAX_KEY 4U

#define OPEN_CFW_SMP_ACT_IO_DISPLAY_ONLY 0U
#define OPEN_CFW_SMP_ACT_IO_DISPLAY_YES_NO 1U
#define OPEN_CFW_SMP_ACT_IO_KEYBOARD_ONLY 2U
#define OPEN_CFW_SMP_ACT_IO_NONE 3U
#define OPEN_CFW_SMP_ACT_IO_KEYBOARD_DISPLAY 4U
#define OPEN_CFW_SMP_ACT_OOB_PRESENT 1U
#define OPEN_CFW_SMP_ACT_AUTH_MITM 4U

#define OPEN_CFW_SMP_ACT_KEY_ENCRYPTION 1U
#define OPEN_CFW_SMP_ACT_KEY_IDENTITY 2U
#define OPEN_CFW_SMP_ACT_KEY_SIGNING 4U
#define OPEN_CFW_SMP_ACT_KEY_LOCAL_LTK 1U
#define OPEN_CFW_SMP_ACT_KEY_PEER_LTK 2U
#define OPEN_CFW_SMP_ACT_KEY_IRK 4U
#define OPEN_CFW_SMP_ACT_KEY_CSRK 8U

#define OPEN_CFW_SMP_ACT_CMD_PAIR_REQUEST 1U
#define OPEN_CFW_SMP_ACT_CMD_CONFIRM 3U
#define OPEN_CFW_SMP_ACT_CMD_RANDOM 4U
#define OPEN_CFW_SMP_ACT_CMD_FAILED 5U
#define OPEN_CFW_SMP_ACT_CMD_ENCRYPTION_INFO 6U
#define OPEN_CFW_SMP_ACT_CMD_MASTER_ID 7U
#define OPEN_CFW_SMP_ACT_CMD_IDENTITY_INFO 8U
#define OPEN_CFW_SMP_ACT_CMD_IDENTITY_ADDRESS 9U
#define OPEN_CFW_SMP_ACT_CMD_SIGNING_INFO 10U
#define OPEN_CFW_SMP_ACT_CMD_SECURITY_REQUEST 11U

#define OPEN_CFW_SMP_ACT_EVENT_CANCEL 3U
#define OPEN_CFW_SMP_ACT_EVENT_AUTH_RESPONSE 4U
#define OPEN_CFW_SMP_ACT_EVENT_SEND_NEXT_KEY 12U
#define OPEN_CFW_SMP_ACT_EVENT_WAIT_TIMEOUT 16U
#define OPEN_CFW_SMP_ACT_EVENT_CLEANUP 31U
#define OPEN_CFW_SMP_ACT_DM_PAIR_COMPLETE 42U
#define OPEN_CFW_SMP_ACT_DM_PAIR_FAILED 43U
#define OPEN_CFW_SMP_ACT_DM_AUTH_REQUEST 46U
#define OPEN_CFW_SMP_ACT_DM_KEY 47U

#define OPEN_CFW_SMP_ACT_ERROR_AUTHENTICATION 3U
#define OPEN_CFW_SMP_ACT_ERROR_KEY_SIZE 6U
#define OPEN_CFW_SMP_ACT_ERROR_ATTEMPTS 9U
#define OPEN_CFW_SMP_ACT_ERROR_TIMEOUT 0xE1U
#define OPEN_CFW_SMP_ACT_SECURITY_NONE 0U
#define OPEN_CFW_SMP_ACT_SECURITY_ENCRYPTED 1U
#define OPEN_CFW_SMP_ACT_SECURITY_AUTHENTICATED 2U
#define OPEN_CFW_SMP_ACT_ROLE_MASTER 0U
#define OPEN_CFW_SMP_ACT_IDLE_PAIRING 1U
#define OPEN_CFW_SMP_ACT_CONNECTION_IDLE 0U
#define OPEN_CFW_SMP_ACT_PUBLIC_ADDRESS 0U
#define OPEN_CFW_SMP_ACT_COMMON_TABLE_ENTRIES 5U

struct open_cfw_smp_act_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_smp_act_timer {
    uint32_t next;
    struct open_cfw_smp_act_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t is_started;
    uint8_t reserved[2];
};

struct open_cfw_smp_act_ltk {
    uint8_t key[16];
    uint8_t random[8];
    uint16_t diversifier;
};

struct open_cfw_smp_act_irk {
    uint8_t key[16];
    uint8_t address[6];
    uint8_t address_type;
};

union open_cfw_smp_act_key_data {
    struct open_cfw_smp_act_ltk ltk;
    struct open_cfw_smp_act_irk irk;
    uint8_t csrk[16];
};

struct open_cfw_smp_act_key_indication {
    struct open_cfw_smp_act_header header;
    union open_cfw_smp_act_key_data key_data;
    uint8_t type;
    uint8_t security_level;
    uint8_t encryption_key_length;
};

union open_cfw_smp_act_scratch {
    struct {
        uint8_t b1[16];
        uint8_t b2[16];
        uint8_t b3[16];
        uint8_t b4[16];
    } buffers;
    struct open_cfw_smp_act_key_indication key_indication;
};

struct open_cfw_smp_act_sc_ltk {
    uint8_t mac[16];
    uint8_t temporary_ltk[16];
};

struct open_cfw_smp_act_sc_ccb {
    uint8_t lesc_enabled;
    uint8_t authentication_type;
    uint8_t keypress_notify;
    uint8_t passkey_position;
    uint8_t display;
    uint8_t reserved[3];
    void *peer_public_key;
    void *local_public_key;
    uint8_t *private_key;
    void *scratch;
    struct open_cfw_smp_act_sc_ltk *ltk;
};

struct open_cfw_smp_act_ccb {
    struct open_cfw_smp_act_timer response_timer;
    struct open_cfw_smp_act_timer wait_timer;
    uint8_t pair_request[7];
    uint8_t pair_response[7];
    uint8_t reserved46[2];
    union open_cfw_smp_act_scratch *scratch;
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
    struct open_cfw_smp_act_sc_ccb *secure_connections;
};

typedef void (*open_cfw_smp_act_function)(
    struct open_cfw_smp_act_ccb *, void *);

typedef uint8_t open_cfw_smp_act_table_entry[3];

struct open_cfw_smp_act_interface {
    const open_cfw_smp_act_table_entry *const *state_table;
    const open_cfw_smp_act_function *action_table;
    const open_cfw_smp_act_table_entry *common_table;
};

struct open_cfw_smp_act_control_block {
    struct open_cfw_smp_act_ccb connections[3];
    const struct open_cfw_smp_act_interface *slave_interface;
    const struct open_cfw_smp_act_interface *master_interface;
    uint8_t handler_id;
    uint8_t reserved237[3];
    void *process_pairing;
    void *process_authentication;
    uint8_t lesc_supported;
    uint8_t reserved249[3];
};

struct open_cfw_smp_act_config {
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

struct open_cfw_smp_act_auth_response {
    struct open_cfw_smp_act_header header;
    uint8_t authentication_data[16];
    uint8_t authentication_data_length;
};

struct open_cfw_smp_act_aes_message {
    struct open_cfw_smp_act_header header;
    uint8_t *ciphertext;
    uint8_t *plaintext;
};

struct open_cfw_smp_act_data_message {
    struct open_cfw_smp_act_header header;
    uint8_t *packet;
};

union open_cfw_smp_act_message {
    struct open_cfw_smp_act_header header;
    struct open_cfw_smp_act_auth_response authentication;
    struct open_cfw_smp_act_aes_message aes;
    struct open_cfw_smp_act_data_message data;
};

#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_smp_act_ccb) == 0x4CU,
    "G2 SMP CCB ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_act_ccb, scratch) == 0x30U,
    "G2 SMP scratch offset changed");
_Static_assert(offsetof(struct open_cfw_smp_act_ccb, connection_id) == 0x3DU,
    "G2 SMP connection-ID offset changed");
_Static_assert(offsetof(struct open_cfw_smp_act_ccb, attempts) == 0x42U,
    "G2 SMP attempts offset changed");
_Static_assert(sizeof(struct open_cfw_smp_act_control_block) == 0xFCU,
    "G2 SMP control-block ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_act_config, minimum_key_length) == 5U,
    "G2 SMP minimum-key offset changed");
#endif

#ifndef OPEN_CFW_SMP_ACT_CONTROL_BLOCK
#define OPEN_CFW_SMP_ACT_CONTROL_BLOCK \
    (*(struct open_cfw_smp_act_control_block *)(uintptr_t)0x20070AECU)
#endif

#ifndef OPEN_CFW_SMP_ACT_CONFIG
#define OPEN_CFW_SMP_ACT_CONFIG \
    (**(struct open_cfw_smp_act_config **)(uintptr_t)0x200004B8U)
#endif

extern void open_cfw_retained_cordio_wsf_timer_start_sec(
    struct open_cfw_smp_act_timer *timer, uint32_t seconds);
extern void open_cfw_retained_cordio_wsf_timer_start_ms(
    struct open_cfw_smp_act_timer *timer, uint32_t milliseconds);
extern void open_cfw_retained_cordio_wsf_timer_stop(
    struct open_cfw_smp_act_timer *timer);
extern void open_cfw_retained_cordio_wsf_buffer_free(void *buffer);
extern void open_cfw_retained_cordio_wsf_msg_free(void *message);
extern void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t length);
extern void open_cfw_retained_cordio_wsf_msg_send(
    uint8_t handler_id, void *message);
extern void open_cfw_retained_cordio_dm_conn_set_idle(
    uint8_t connection_id, uint16_t idle_mask, uint8_t idle);
extern uint8_t open_cfw_retained_cordio_dm_conn_security_level(
    uint8_t connection_id);
extern uint8_t open_cfw_retained_cordio_dm_conn_role(uint8_t connection_id);
extern void open_cfw_cordio_dm_sec_smp_callback_execute(void *message);
extern void open_cfw_retained_cordio_sec_rand(
    uint8_t *buffer, uint16_t length);
extern void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16]);
extern const uint8_t *open_cfw_cordio_dm_sec_get_local_irk(void);
extern const uint8_t *open_cfw_cordio_dm_sec_get_local_csrk(void);
extern const uint8_t *open_cfw_retained_cordio_hci_get_bd_address(void);
extern uint32_t open_cfw_cordio_smp_db_max_attempt_reached(
    uint8_t connection_id);
extern uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length);
extern void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_act_ccb *ccb, uint8_t *packet);
extern void open_cfw_cordio_smp_main_calculate_c1_part1(
    struct open_cfw_smp_act_ccb *ccb, const uint8_t *key,
    const uint8_t *random);
extern void open_cfw_cordio_smp_main_calculate_c1_part2(
    struct open_cfw_smp_act_ccb *ccb, const uint8_t *key,
    const uint8_t *part1);
extern void open_cfw_cordio_smp_main_generate_ltk(
    struct open_cfw_smp_act_ccb *ccb);
extern uint8_t open_cfw_cordio_smp_main_get_sc_security_level(
    struct open_cfw_smp_act_ccb *ccb);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);
extern void *open_cfw_runtime_memory_zero(void *destination, uint32_t size);

void open_cfw_cordio_smp_act_start_response_timer(
    struct open_cfw_smp_act_ccb *ccb);
void open_cfw_cordio_smp_act_cleanup_core(
    struct open_cfw_smp_act_ccb *ccb);
void open_cfw_cordio_smp_act_send_pairing_failed(
    struct open_cfw_smp_act_ccb *ccb, uint8_t reason);
void open_cfw_cordio_smp_act_pairing_failed(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message);
void open_cfw_cordio_smp_act_pairing_cancel(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message);
void open_cfw_cordio_smp_act_store_pin(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message);
void open_cfw_cordio_smp_act_notify_attempts_failure(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message);
void open_cfw_cordio_smp_act_execute(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message);

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_START_TIMER_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_start_response_timer(
    struct open_cfw_smp_act_ccb *ccb)
{
    ccb->response_timer.message.event = 15U;
    ccb->response_timer.message.status = OPEN_CFW_SMP_ACT_ERROR_TIMEOUT;
    open_cfw_retained_cordio_wsf_timer_start_sec(
        &ccb->response_timer, OPEN_CFW_SMP_ACT_TIMEOUT_SECONDS);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_NONE_ONLY)
__attribute__((noinline, aligned(2))) void open_cfw_cordio_smp_act_none(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    (void)ccb;
    (void)message;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_CLEANUP_CORE_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_cleanup_core(
    struct open_cfw_smp_act_ccb *ccb)
{
    if (ccb->scratch != NULL) {
        open_cfw_retained_cordio_wsf_buffer_free(ccb->scratch);
        ccb->scratch = NULL;
    }
    open_cfw_retained_cordio_wsf_timer_stop(&ccb->response_timer);
    open_cfw_retained_cordio_wsf_timer_stop(&ccb->wait_timer);
    ccb->security_request = 0U;
    ccb->next_command = ccb->initiator != 0U ?
        OPEN_CFW_SMP_ACT_CMD_SECURITY_REQUEST :
        OPEN_CFW_SMP_ACT_CMD_PAIR_REQUEST;
    ccb->last_sent_key = 0U;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_CLEANUP_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_cleanup(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    (void)message;
    open_cfw_cordio_smp_act_cleanup_core(ccb);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_SEND_FAIL_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_send_pairing_failed(
    struct open_cfw_smp_act_ccb *ccb, uint8_t reason)
{
    uint8_t *packet = open_cfw_cordio_smp_main_message_allocate(
        OPEN_CFW_SMP_ACT_PACKET_OFFSET +
        OPEN_CFW_SMP_ACT_PAIR_FAIL_PACKET_BYTES);
    if (packet != NULL) {
        packet[OPEN_CFW_SMP_ACT_PACKET_OFFSET] = OPEN_CFW_SMP_ACT_CMD_FAILED;
        packet[OPEN_CFW_SMP_ACT_PACKET_OFFSET + 1U] = reason;
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_PAIR_FAIL_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_pairing_failed(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    open_cfw_cordio_smp_act_cleanup_core(ccb);
    open_cfw_retained_cordio_dm_conn_set_idle(
        ccb->connection_id, OPEN_CFW_SMP_ACT_IDLE_PAIRING,
        OPEN_CFW_SMP_ACT_CONNECTION_IDLE);
    message->header.event = OPEN_CFW_SMP_ACT_DM_PAIR_FAILED;
    open_cfw_cordio_dm_sec_smp_callback_execute(message);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_SEC_TIMEOUT_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_security_request_timeout(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    if (open_cfw_retained_cordio_dm_conn_security_level(
            ccb->connection_id) == OPEN_CFW_SMP_ACT_SECURITY_NONE) {
        open_cfw_cordio_smp_act_pairing_failed(ccb, message);
    } else {
        message->header.event = OPEN_CFW_SMP_ACT_EVENT_CLEANUP;
        open_cfw_cordio_smp_act_execute(ccb, message);
    }
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_PAIR_CANCEL_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_pairing_cancel(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    open_cfw_cordio_smp_act_send_pairing_failed(ccb, message->header.status);
    open_cfw_cordio_smp_act_pairing_failed(ccb, message);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_STORE_PIN_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_store_pin(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    open_cfw_iar_memcpy_void(
        ccb->scratch->buffers.b1,
        message->authentication.authentication_data,
        message->authentication.authentication_data_length);
    if (message->authentication.authentication_data_length ==
            OPEN_CFW_SMP_ACT_PIN_BYTES) {
        open_cfw_runtime_memory_zero(
            &ccb->scratch->buffers.b1[OPEN_CFW_SMP_ACT_PIN_BYTES],
            OPEN_CFW_SMP_ACT_OOB_BYTES - OPEN_CFW_SMP_ACT_PIN_BYTES);
    }
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_PROCESS_PAIRING_ONLY)
__attribute__((noinline)) uint8_t open_cfw_cordio_smp_act_process_pairing(
    struct open_cfw_smp_act_ccb *ccb, uint8_t *oob, uint8_t *display)
{
    uint8_t just_works = 1U;
    uint8_t local_auth;
    union open_cfw_smp_act_message message;

    *display = 0U;
    *oob = 0U;
    if (ccb->pair_request[OPEN_CFW_SMP_ACT_PAIR_OOB] ==
            OPEN_CFW_SMP_ACT_OOB_PRESENT &&
        ccb->pair_response[OPEN_CFW_SMP_ACT_PAIR_OOB] ==
            OPEN_CFW_SMP_ACT_OOB_PRESENT) {
        *oob = OPEN_CFW_SMP_ACT_OOB_PRESENT;
        just_works = 0U;
    } else if (((ccb->pair_request[OPEN_CFW_SMP_ACT_PAIR_AUTH] |
                 ccb->pair_response[OPEN_CFW_SMP_ACT_PAIR_AUTH]) &
                OPEN_CFW_SMP_ACT_AUTH_MITM) != 0U) {
        uint8_t request_io = ccb->pair_request[OPEN_CFW_SMP_ACT_PAIR_IO];
        uint8_t response_io = ccb->pair_response[OPEN_CFW_SMP_ACT_PAIR_IO];
        uint8_t both_display =
            (uint8_t)(((request_io == OPEN_CFW_SMP_ACT_IO_DISPLAY_ONLY) ||
                       (request_io == OPEN_CFW_SMP_ACT_IO_DISPLAY_YES_NO)) &&
                      ((response_io == OPEN_CFW_SMP_ACT_IO_DISPLAY_ONLY) ||
                       (response_io == OPEN_CFW_SMP_ACT_IO_DISPLAY_YES_NO)));
        if (request_io != OPEN_CFW_SMP_ACT_IO_NONE &&
            response_io != OPEN_CFW_SMP_ACT_IO_NONE && both_display == 0U) {
            just_works = 0U;
            *display = (uint8_t)(
                request_io == OPEN_CFW_SMP_ACT_IO_DISPLAY_ONLY ||
                request_io == OPEN_CFW_SMP_ACT_IO_DISPLAY_YES_NO ||
                (request_io == OPEN_CFW_SMP_ACT_IO_KEYBOARD_DISPLAY &&
                 (response_io == OPEN_CFW_SMP_ACT_IO_KEYBOARD_ONLY ||
                  response_io == OPEN_CFW_SMP_ACT_IO_KEYBOARD_DISPLAY)));
            if (!(response_io == OPEN_CFW_SMP_ACT_IO_KEYBOARD_ONLY &&
                  request_io == OPEN_CFW_SMP_ACT_IO_KEYBOARD_ONLY)) {
                *display ^= (uint8_t)(ccb->initiator == 0U);
            }
        }
    }

    ccb->authentication = (uint8_t)(
        ccb->pair_request[OPEN_CFW_SMP_ACT_PAIR_AUTH] &
        ccb->pair_response[OPEN_CFW_SMP_ACT_PAIR_AUTH]);
    if (just_works == 0U) {
        ccb->authentication |= OPEN_CFW_SMP_ACT_AUTH_MITM;
    } else {
        ccb->authentication &= (uint8_t)~OPEN_CFW_SMP_ACT_AUTH_MITM;
    }

    local_auth = ccb->initiator != 0U ?
        ccb->pair_request[OPEN_CFW_SMP_ACT_PAIR_AUTH] :
        ccb->pair_response[OPEN_CFW_SMP_ACT_PAIR_AUTH];
    if (just_works != 0U &&
        (OPEN_CFW_SMP_ACT_CONFIG.authentication & local_auth &
         OPEN_CFW_SMP_ACT_AUTH_MITM) != 0U) {
        message.header.param = ccb->connection_id;
        message.header.status = OPEN_CFW_SMP_ACT_ERROR_AUTHENTICATION;
        message.header.event = OPEN_CFW_SMP_ACT_EVENT_CANCEL;
        open_cfw_cordio_smp_act_execute(ccb, &message);
        return 0U;
    }
    if (ccb->pair_request[OPEN_CFW_SMP_ACT_PAIR_MAX_KEY] <
            OPEN_CFW_SMP_ACT_CONFIG.minimum_key_length ||
        ccb->pair_response[OPEN_CFW_SMP_ACT_PAIR_MAX_KEY] <
            OPEN_CFW_SMP_ACT_CONFIG.minimum_key_length) {
        message.header.param = ccb->connection_id;
        message.header.status = OPEN_CFW_SMP_ACT_ERROR_KEY_SIZE;
        message.header.event = OPEN_CFW_SMP_ACT_EVENT_CANCEL;
        open_cfw_cordio_smp_act_execute(ccb, &message);
        return 0U;
    }
    return 1U;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_AUTH_REQUEST_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_authentication_request(
    struct open_cfw_smp_act_ccb *ccb, uint8_t oob, uint8_t display)
{
    union {
        struct open_cfw_smp_act_auth_response response;
        struct {
            struct open_cfw_smp_act_header header;
            uint8_t oob;
            uint8_t display;
        } request;
    } message;
    if ((ccb->authentication & OPEN_CFW_SMP_ACT_AUTH_MITM) != 0U) {
        message.request.header.param = ccb->connection_id;
        message.request.header.event = OPEN_CFW_SMP_ACT_DM_AUTH_REQUEST;
        message.request.oob = oob;
        message.request.display = display;
        open_cfw_cordio_dm_sec_smp_callback_execute(&message.request);
    } else {
        message.response.header.param = ccb->connection_id;
        message.response.header.event = OPEN_CFW_SMP_ACT_EVENT_AUTH_RESPONSE;
        message.response.authentication_data[0] = 0U;
        message.response.authentication_data[1] = 0U;
        message.response.authentication_data[2] = 0U;
        message.response.authentication_data_length = OPEN_CFW_SMP_ACT_PIN_BYTES;
        open_cfw_cordio_smp_act_execute(
            ccb, (union open_cfw_smp_act_message *)&message.response);
    }
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_CONFIRM_CALC1_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_confirm_calculate_one(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    open_cfw_cordio_smp_act_store_pin(ccb, message);
    open_cfw_retained_cordio_sec_rand(
        ccb->scratch->buffers.b4, OPEN_CFW_SMP_ACT_RANDOM_BYTES);
    open_cfw_cordio_smp_main_calculate_c1_part1(
        ccb, ccb->scratch->buffers.b1, ccb->scratch->buffers.b4);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_CONFIRM_CALC2_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_confirm_calculate_two(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    open_cfw_cordio_smp_main_calculate_c1_part2(
        ccb, ccb->scratch->buffers.b1, message->aes.ciphertext);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_SEND_CONFIRM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_send_confirm(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    uint8_t *packet;
    ccb->next_command = ccb->initiator != 0U ?
        OPEN_CFW_SMP_ACT_CMD_CONFIRM : OPEN_CFW_SMP_ACT_CMD_RANDOM;
    open_cfw_cordio_smp_act_start_response_timer(ccb);
    packet = open_cfw_cordio_smp_main_message_allocate(
        OPEN_CFW_SMP_ACT_PACKET_OFFSET +
        OPEN_CFW_SMP_ACT_CONFIRM_PACKET_BYTES);
    if (packet != NULL) {
        packet[OPEN_CFW_SMP_ACT_PACKET_OFFSET] = OPEN_CFW_SMP_ACT_CMD_CONFIRM;
        open_cfw_iar_memcpy_void(
            &packet[OPEN_CFW_SMP_ACT_PACKET_OFFSET + 1U],
            message->aes.ciphertext, OPEN_CFW_SMP_ACT_CONFIRM_BYTES);
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_VERIFY_CALC1_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_verify_calculate_one(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    uint8_t *random = message->data.packet +
        OPEN_CFW_SMP_ACT_PACKET_OFFSET + 1U;
    open_cfw_iar_memcpy_void(
        ccb->scratch->buffers.b2, random, OPEN_CFW_SMP_ACT_RANDOM_BYTES);
    open_cfw_cordio_smp_main_calculate_c1_part1(
        ccb, ccb->scratch->buffers.b1, random);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_VERIFY_CALC2_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_verify_calculate_two(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    open_cfw_cordio_smp_main_calculate_c1_part2(
        ccb, ccb->scratch->buffers.b1, message->aes.ciphertext);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_SEND_KEY_ONLY)
__attribute__((noinline)) uint8_t open_cfw_cordio_smp_act_send_key(
    struct open_cfw_smp_act_ccb *ccb, uint8_t distribution)
{
    uint8_t *packet;
    uint8_t *payload;
    struct open_cfw_smp_act_header *header;

    if (OPEN_CFW_SMP_ACT_CONTROL_BLOCK.lesc_supported != 0U &&
        ccb->secure_connections != NULL &&
        ccb->secure_connections->lesc_enabled != 0U &&
        ccb->last_sent_key == 0U) {
        struct open_cfw_smp_act_key_indication indication;
        indication.type =
            open_cfw_retained_cordio_dm_conn_role(ccb->connection_id) ==
                OPEN_CFW_SMP_ACT_ROLE_MASTER ?
            OPEN_CFW_SMP_ACT_KEY_PEER_LTK : OPEN_CFW_SMP_ACT_KEY_LOCAL_LTK;
        indication.header.event = OPEN_CFW_SMP_ACT_DM_KEY;
        indication.header.param = ccb->connection_id;
        indication.security_level =
            open_cfw_cordio_smp_main_get_sc_security_level(ccb);
        indication.key_data.ltk.diversifier = 0U;
        open_cfw_runtime_memory_zero(
            indication.key_data.ltk.random, OPEN_CFW_SMP_ACT_RANDOM8_BYTES);
        open_cfw_retained_cordio_calc128_copy(
            indication.key_data.ltk.key,
            ccb->secure_connections->ltk->temporary_ltk);
        open_cfw_cordio_dm_sec_smp_callback_execute(&indication);
        ccb->last_sent_key = OPEN_CFW_SMP_ACT_CMD_MASTER_ID;
    }

    if (distribution == 0U ||
        (distribution == OPEN_CFW_SMP_ACT_KEY_ENCRYPTION &&
         ccb->last_sent_key == OPEN_CFW_SMP_ACT_CMD_MASTER_ID) ||
        (distribution <= (OPEN_CFW_SMP_ACT_KEY_ENCRYPTION |
                          OPEN_CFW_SMP_ACT_KEY_IDENTITY) &&
         ccb->last_sent_key == OPEN_CFW_SMP_ACT_CMD_IDENTITY_ADDRESS) ||
        ccb->last_sent_key == OPEN_CFW_SMP_ACT_CMD_SIGNING_INFO) {
        return 1U;
    }
    if (ccb->flow_disabled != 0U) {
        return 0U;
    }

    packet = open_cfw_cordio_smp_main_message_allocate(
        OPEN_CFW_SMP_ACT_PACKET_OFFSET +
        OPEN_CFW_SMP_ACT_ENCRYPT_PACKET_BYTES);
    if (packet == NULL) {
        return 0U;
    }
    payload = &packet[OPEN_CFW_SMP_ACT_PACKET_OFFSET];
    if (ccb->last_sent_key == 0U &&
        (distribution & OPEN_CFW_SMP_ACT_KEY_ENCRYPTION) != 0U) {
        open_cfw_cordio_smp_main_generate_ltk(ccb);
        *payload++ = OPEN_CFW_SMP_ACT_CMD_ENCRYPTION_INFO;
        open_cfw_retained_cordio_calc128_copy(
            payload, ccb->scratch->key_indication.key_data.ltk.key);
    } else if (ccb->last_sent_key ==
               OPEN_CFW_SMP_ACT_CMD_ENCRYPTION_INFO) {
        uint16_t diversifier =
            ccb->scratch->key_indication.key_data.ltk.diversifier;
        *payload++ = OPEN_CFW_SMP_ACT_CMD_MASTER_ID;
        *payload++ = (uint8_t)diversifier;
        *payload++ = (uint8_t)(diversifier >> 8U);
        open_cfw_iar_memcpy_void(
            payload, ccb->scratch->key_indication.key_data.ltk.random,
            OPEN_CFW_SMP_ACT_RANDOM8_BYTES);
    } else if ((distribution & OPEN_CFW_SMP_ACT_KEY_IDENTITY) != 0U &&
               (ccb->last_sent_key == 0U ||
                ccb->last_sent_key == OPEN_CFW_SMP_ACT_CMD_MASTER_ID)) {
        *payload++ = OPEN_CFW_SMP_ACT_CMD_IDENTITY_INFO;
        open_cfw_retained_cordio_calc128_copy(
            payload, open_cfw_cordio_dm_sec_get_local_irk());
    } else if (ccb->last_sent_key ==
               OPEN_CFW_SMP_ACT_CMD_IDENTITY_INFO) {
        *payload++ = OPEN_CFW_SMP_ACT_CMD_IDENTITY_ADDRESS;
        *payload++ = OPEN_CFW_SMP_ACT_PUBLIC_ADDRESS;
        open_cfw_iar_memcpy_void(
            payload, open_cfw_retained_cordio_hci_get_bd_address(), 6U);
    } else if ((distribution & OPEN_CFW_SMP_ACT_KEY_SIGNING) != 0U &&
               (ccb->last_sent_key == 0U ||
                ccb->last_sent_key == OPEN_CFW_SMP_ACT_CMD_IDENTITY_ADDRESS ||
                ccb->last_sent_key == OPEN_CFW_SMP_ACT_CMD_MASTER_ID)) {
        *payload++ = OPEN_CFW_SMP_ACT_CMD_SIGNING_INFO;
        open_cfw_retained_cordio_calc128_copy(
            payload, open_cfw_cordio_dm_sec_get_local_csrk());
    } else {
        open_cfw_retained_cordio_wsf_msg_free(packet);
        return 1U;
    }

    ccb->last_sent_key = packet[OPEN_CFW_SMP_ACT_PACKET_OFFSET];
    open_cfw_cordio_smp_main_send_packet(ccb, packet);
    if (ccb->flow_disabled == 0U) {
        header = open_cfw_retained_cordio_wsf_msg_alloc(
            (uint16_t)sizeof(*header));
        if (header != NULL) {
            header->event = OPEN_CFW_SMP_ACT_EVENT_SEND_NEXT_KEY;
            header->param = ccb->connection_id;
            open_cfw_retained_cordio_wsf_msg_send(
                OPEN_CFW_SMP_ACT_CONTROL_BLOCK.handler_id, header);
        }
    }
    return 0U;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_RECEIVE_KEY_ONLY)
__attribute__((noinline)) uint8_t open_cfw_cordio_smp_act_receive_key(
    struct open_cfw_smp_act_ccb *ccb,
    struct open_cfw_smp_act_key_indication *indication,
    uint8_t *packet, uint8_t distribution)
{
    uint8_t ready = 0U;
    uint8_t done = 0U;
    uint8_t *payload = packet + OPEN_CFW_SMP_ACT_PACKET_OFFSET;
    uint8_t command = *payload++;

    if (command == OPEN_CFW_SMP_ACT_CMD_ENCRYPTION_INFO) {
        open_cfw_retained_cordio_calc128_copy(
            indication->key_data.ltk.key, payload);
    } else if (command == OPEN_CFW_SMP_ACT_CMD_MASTER_ID) {
        indication->key_data.ltk.diversifier =
            (uint16_t)payload[0] | ((uint16_t)payload[1] << 8U);
        open_cfw_iar_memcpy_void(
            indication->key_data.ltk.random, &payload[2],
            OPEN_CFW_SMP_ACT_RANDOM8_BYTES);
        indication->security_level =
            (ccb->authentication & OPEN_CFW_SMP_ACT_AUTH_MITM) != 0U ?
            OPEN_CFW_SMP_ACT_SECURITY_AUTHENTICATED :
            OPEN_CFW_SMP_ACT_SECURITY_ENCRYPTED;
        indication->type = OPEN_CFW_SMP_ACT_KEY_PEER_LTK;
        ready = 1U;
    } else if (command == OPEN_CFW_SMP_ACT_CMD_IDENTITY_INFO) {
        open_cfw_retained_cordio_calc128_copy(
            indication->key_data.irk.key, payload);
    } else if (command == OPEN_CFW_SMP_ACT_CMD_IDENTITY_ADDRESS) {
        indication->key_data.irk.address_type = payload[0];
        open_cfw_iar_memcpy_void(
            indication->key_data.irk.address, &payload[1], 6U);
        indication->type = OPEN_CFW_SMP_ACT_KEY_IRK;
        ready = 1U;
    } else if (command == OPEN_CFW_SMP_ACT_CMD_SIGNING_INFO) {
        open_cfw_retained_cordio_calc128_copy(
            indication->key_data.csrk, payload);
        indication->type = OPEN_CFW_SMP_ACT_KEY_CSRK;
        ready = 1U;
    }

    if (ccb->next_command == OPEN_CFW_SMP_ACT_CMD_ENCRYPTION_INFO ||
        ccb->next_command == OPEN_CFW_SMP_ACT_CMD_IDENTITY_INFO) {
        ccb->next_command++;
    } else if ((distribution & OPEN_CFW_SMP_ACT_KEY_IDENTITY) != 0U &&
               ccb->next_command == OPEN_CFW_SMP_ACT_CMD_MASTER_ID) {
        ccb->next_command = OPEN_CFW_SMP_ACT_CMD_IDENTITY_INFO;
    } else if ((distribution & OPEN_CFW_SMP_ACT_KEY_SIGNING) != 0U &&
               (ccb->next_command == OPEN_CFW_SMP_ACT_CMD_MASTER_ID ||
                ccb->next_command ==
                    OPEN_CFW_SMP_ACT_CMD_IDENTITY_ADDRESS)) {
        ccb->next_command = OPEN_CFW_SMP_ACT_CMD_SIGNING_INFO;
    } else {
        done = 1U;
    }
    if (ready != 0U) {
        indication->header.event = OPEN_CFW_SMP_ACT_DM_KEY;
        open_cfw_cordio_dm_sec_smp_callback_execute(indication);
    }
    return done;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_MAX_ATTEMPTS_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_max_attempts(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    uint32_t timeout;
    open_cfw_cordio_smp_act_pairing_cancel(ccb, message);
    timeout = open_cfw_cordio_smp_db_max_attempt_reached(ccb->connection_id);
    ccb->wait_timer.message.event = OPEN_CFW_SMP_ACT_EVENT_WAIT_TIMEOUT;
    open_cfw_retained_cordio_wsf_timer_start_ms(&ccb->wait_timer, timeout);
    ccb->attempts = 0U;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_ATTEMPT_RECEIVED_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_attempt_received(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    (void)message;
    ccb->attempts = 1U;
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_NOTIFY_ATTEMPTS_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_notify_attempts_failure(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    (void)ccb;
    message->header.status = OPEN_CFW_SMP_ACT_ERROR_ATTEMPTS;
    message->header.event = OPEN_CFW_SMP_ACT_DM_PAIR_FAILED;
    open_cfw_cordio_dm_sec_smp_callback_execute(message);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_NOTIFY_TIMEOUT_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_notify_timeout_failure(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    (void)ccb;
    message->header.status = OPEN_CFW_SMP_ACT_ERROR_TIMEOUT;
    message->header.event = OPEN_CFW_SMP_ACT_DM_PAIR_FAILED;
    open_cfw_cordio_dm_sec_smp_callback_execute(message);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_CHECK_ATTEMPTS_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_check_attempts(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    if (ccb->attempts != 0U) {
        ccb->attempts = 0U;
        open_cfw_cordio_smp_act_send_pairing_failed(
            ccb, OPEN_CFW_SMP_ACT_ERROR_ATTEMPTS);
        open_cfw_cordio_smp_act_notify_attempts_failure(ccb, message);
        open_cfw_cordio_smp_act_cleanup_core(ccb);
    }
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_PAIR_COMPLETE_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_pairing_complete(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    struct {
        struct open_cfw_smp_act_header header;
        uint8_t authentication;
    } complete;
    (void)message;
    open_cfw_cordio_smp_act_cleanup_core(ccb);
    open_cfw_retained_cordio_dm_conn_set_idle(
        ccb->connection_id, OPEN_CFW_SMP_ACT_IDLE_PAIRING,
        OPEN_CFW_SMP_ACT_CONNECTION_IDLE);
    complete.authentication = ccb->authentication;
    complete.header.param = ccb->connection_id;
    complete.header.event = OPEN_CFW_SMP_ACT_DM_PAIR_COMPLETE;
    open_cfw_cordio_dm_sec_smp_callback_execute(&complete);
}
#endif

#if OPEN_CFW_SMP_ACT_ALL || defined(OPEN_CFW_SMP_ACT_EXECUTE_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_act_execute(
    struct open_cfw_smp_act_ccb *ccb, union open_cfw_smp_act_message *message)
{
    const struct open_cfw_smp_act_interface *interface =
        open_cfw_retained_cordio_dm_conn_role(ccb->connection_id) == 1U ?
        OPEN_CFW_SMP_ACT_CONTROL_BLOCK.slave_interface :
        OPEN_CFW_SMP_ACT_CONTROL_BLOCK.master_interface;
    const open_cfw_smp_act_table_entry *entry =
        interface->state_table[ccb->state];

    for (;;) {
        do {
            if ((*entry)[0] == message->header.event) {
                ccb->state = (*entry)[1];
                interface->action_table[(*entry)[2]](ccb, message);
                return;
            }
            entry++;
        } while ((*entry)[0] != 0U);

        if (entry == interface->common_table +
                     OPEN_CFW_SMP_ACT_COMMON_TABLE_ENTRIES - 1U) {
            return;
        }
        entry = interface->common_table;
    }
}
#endif
