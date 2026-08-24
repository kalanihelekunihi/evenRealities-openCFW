/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the twenty Packetcraft Cordio shared Secure
 * Connections actions linked by G2 2.2.6.10.  This keeps the recovered
 * 32-bit SRAM/message ABI explicit and preserves G2's R4/r19 association
 * model rule for peers with no input and no output.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMP_SC_ACT_CAT_INITIATOR_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_CAT_RESPONDER_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_PROCESS_PAIRING_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_AUTH_REQUEST_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_CLEANUP_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_PAIRING_FAILED_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_PAIRING_CANCEL_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_AUTH_SELECT_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_PASSKEY_SETUP_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_JWNC_F4_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_JWNC_G2_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_JWNC_DISPLAY_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_PASSKEY_RECEIVE_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_PASSKEY_SEND_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_SHARED_SECRET_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_F5_T_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_F5_MAC_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_F5_LTK_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_F6_EA_ONLY) && \
    !defined(OPEN_CFW_SMP_SC_ACT_F6_EB_ONLY)
#define OPEN_CFW_SMP_SC_ACT_ALL 1
#else
#define OPEN_CFW_SMP_SC_ACT_ALL 0
#endif

#define OPEN_CFW_SMP_SC_ACT_ADDRESS_BYTES 6U
#define OPEN_CFW_SMP_SC_ACT_PUBLIC_KEY_BYTES 32U
#define OPEN_CFW_SMP_SC_ACT_PRIVATE_KEY_BYTES 32U
#define OPEN_CFW_SMP_SC_ACT_DH_KEY_BYTES 32U
#define OPEN_CFW_SMP_SC_ACT_RANDOM_BYTES 16U
#define OPEN_CFW_SMP_SC_ACT_PDU_OFFSET 8U
#define OPEN_CFW_SMP_SC_ACT_PUBLIC_X_POSITION 1U
#define OPEN_CFW_SMP_SC_ACT_PUBLIC_Y_POSITION 33U
#define OPEN_CFW_SMP_SC_ACT_PAIR_IO 1U
#define OPEN_CFW_SMP_SC_ACT_PAIR_OOB 2U
#define OPEN_CFW_SMP_SC_ACT_PAIR_AUTH 3U
#define OPEN_CFW_SMP_SC_ACT_PAIR_MAX_KEY 4U
#define OPEN_CFW_SMP_SC_ACT_AUTH_MITM 0x04U
#define OPEN_CFW_SMP_SC_ACT_AUTH_SC 0x08U
#define OPEN_CFW_SMP_SC_ACT_AUTH_KEYPRESS 0x10U
#define OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_ONLY 0U
#define OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO 1U
#define OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_ONLY 2U
#define OPEN_CFW_SMP_SC_ACT_IO_NONE 3U
#define OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_DISPLAY 4U
#define OPEN_CFW_SMP_SC_ACT_OOB_PRESENT 1U
#define OPEN_CFW_SMP_SC_ACT_AUTH_JUST_WORKS 1U
#define OPEN_CFW_SMP_SC_ACT_AUTH_OOB 2U
#define OPEN_CFW_SMP_SC_ACT_AUTH_PASSKEY 3U
#define OPEN_CFW_SMP_SC_ACT_AUTH_NUMERIC 4U
#define OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL 3U
#define OPEN_CFW_SMP_SC_ACT_EVENT_AUTH_RESPONSE 4U
#define OPEN_CFW_SMP_SC_ACT_EVENT_JW_NC 19U
#define OPEN_CFW_SMP_SC_ACT_EVENT_PASSKEY 20U
#define OPEN_CFW_SMP_SC_ACT_EVENT_OOB 21U
#define OPEN_CFW_SMP_SC_ACT_EVENT_USER_CONFIRM 22U
#define OPEN_CFW_SMP_SC_ACT_EVENT_EARLY_CONFIRM 30U
#define OPEN_CFW_SMP_SC_ACT_DM_AUTH_REQUEST 46U
#define OPEN_CFW_SMP_SC_ACT_DM_COMPARE 53U
#define OPEN_CFW_SMP_SC_ACT_DM_KEYPRESS 54U
#define OPEN_CFW_SMP_SC_ACT_CMD_CONFIRM 3U
#define OPEN_CFW_SMP_SC_ACT_CMD_KEYPRESS 14U
#define OPEN_CFW_SMP_SC_ACT_KEYPRESS_MESSAGE_BYTES 2U
#define OPEN_CFW_SMP_SC_ACT_F5_T_BYTES 32U
#define OPEN_CFW_SMP_SC_ACT_F5_TEXT_BYTES 53U
#define OPEN_CFW_SMP_SC_ACT_G2_TEXT_BYTES 80U
#define OPEN_CFW_SMP_SC_ACT_F6_TEXT_BYTES 65U
#define OPEN_CFW_SMP_SC_ACT_ERROR_AUTH 3U
#define OPEN_CFW_SMP_SC_ACT_ERROR_KEY_SIZE 6U
#define OPEN_CFW_SMP_SC_ACT_ERROR_MEMORY 7U
#define OPEN_CFW_SMP_SC_ACT_ERROR_UNSPECIFIED 8U
#define OPEN_CFW_SMP_SC_ACT_ERROR_DH_KEY 11U
#define OPEN_CFW_SMP_SC_ACT_SUCCESS 0U

struct open_cfw_smp_sc_act_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_smp_sc_act_timer {
    uint32_t next;
    struct open_cfw_smp_sc_act_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t is_started;
    uint8_t reserved[2];
};

union open_cfw_smp_sc_act_legacy_scratch {
    uint8_t bytes[64];
    uint32_t alignment;
};

struct open_cfw_smp_sc_act_public_key {
    uint8_t x[32];
    uint8_t y[32];
};

struct open_cfw_smp_sc_act_scratch {
    uint8_t initiator_random[16];
    uint8_t responder_random[16];
    uint8_t ra[16];
    uint8_t rb[16];
    uint8_t peer_cb[16];
    uint8_t peer_ca_or_ea[16];
};

struct open_cfw_smp_sc_act_ltk {
    uint8_t mac[16];
    uint8_t temporary_ltk[16];
};

struct open_cfw_smp_sc_act_sc_ccb {
    uint8_t lesc_enabled;
    uint8_t authentication_type;
    uint8_t keypress_notify;
    uint8_t passkey_position;
    uint8_t display;
    uint8_t reserved[3];
    struct open_cfw_smp_sc_act_public_key *peer_public_key;
    struct open_cfw_smp_sc_act_public_key *local_public_key;
    uint8_t *private_key;
    struct open_cfw_smp_sc_act_scratch *scratch;
    struct open_cfw_smp_sc_act_ltk *ltk;
};

struct open_cfw_smp_sc_act_ccb {
    struct open_cfw_smp_sc_act_timer response_timer;
    struct open_cfw_smp_sc_act_timer wait_timer;
    uint8_t pair_request[7];
    uint8_t pair_response[7];
    uint8_t reserved46[2];
    union open_cfw_smp_sc_act_legacy_scratch *legacy_scratch;
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
    struct open_cfw_smp_sc_act_sc_ccb *secure_connections;
};

struct open_cfw_smp_sc_act_control_block {
    struct open_cfw_smp_sc_act_ccb connections[3];
    const void *slave_interface;
    const void *master_interface;
    uint8_t handler_id;
    uint8_t reserved237[3];
    void *process_pairing;
    void *process_authentication;
    uint8_t lesc_supported;
    uint8_t reserved249[3];
};

struct open_cfw_smp_sc_act_config {
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

struct open_cfw_smp_sc_act_ecc_key {
    uint8_t public_x[32];
    uint8_t public_y[32];
    uint8_t private_key[32];
};

struct open_cfw_smp_sc_act_auth_response {
    struct open_cfw_smp_sc_act_header header;
    uint8_t data[16];
    uint8_t length;
};

struct open_cfw_smp_sc_act_data_message {
    struct open_cfw_smp_sc_act_header header;
    uint8_t *packet;
};

struct open_cfw_smp_sc_act_aes_message {
    struct open_cfw_smp_sc_act_header header;
    uint8_t *ciphertext;
    uint8_t *plaintext;
};

struct open_cfw_smp_sc_act_ecc_message {
    struct open_cfw_smp_sc_act_header header;
    uint8_t secret[32];
};

struct open_cfw_smp_sc_act_cmac_message {
    struct open_cfw_smp_sc_act_header header;
    uint8_t *ciphertext;
    uint8_t *plaintext;
};

struct open_cfw_smp_sc_act_keypress_message {
    struct open_cfw_smp_sc_act_header header;
    uint8_t keypress;
};

union open_cfw_smp_sc_act_message {
    struct open_cfw_smp_sc_act_header header;
    struct open_cfw_smp_sc_act_auth_response authentication;
    struct open_cfw_smp_sc_act_data_message data;
    struct open_cfw_smp_sc_act_aes_message aes;
    struct open_cfw_smp_sc_act_ecc_message ecc;
    struct open_cfw_smp_sc_act_cmac_message cmac;
    struct open_cfw_smp_sc_act_keypress_message keypress;
};

#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_smp_sc_act_sc_ccb) == 0x1CU,
    "G2 SMP SC CCB ABI changed");
_Static_assert(sizeof(struct open_cfw_smp_sc_act_ccb) == 0x4CU,
    "G2 SMP CCB ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_act_ccb, connection_id) == 0x3DU,
    "G2 SMP connection-ID offset changed");
_Static_assert(offsetof(struct open_cfw_smp_sc_act_ccb, authentication) == 0x40U,
    "G2 SMP authentication offset changed");
_Static_assert(sizeof(struct open_cfw_smp_sc_act_control_block) == 0xFCU,
    "G2 SMP control-block ABI changed");
#endif

#ifndef OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK
#define OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK \
    (*(struct open_cfw_smp_sc_act_control_block *)(uintptr_t)0x20070AECU)
#endif
#ifndef OPEN_CFW_SMP_SC_ACT_CONFIG
#define OPEN_CFW_SMP_SC_ACT_CONFIG \
    (**(struct open_cfw_smp_sc_act_config **)(uintptr_t)0x200004B8U)
#endif

extern uint8_t *open_cfw_retained_cordio_dm_conn_local_address(uint8_t id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_local_rpa(uint8_t id);
extern uint8_t open_cfw_retained_cordio_dm_conn_local_address_type(uint8_t id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_peer_address(uint8_t id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_peer_rpa(uint8_t id);
extern uint8_t open_cfw_retained_cordio_dm_conn_peer_address_type(uint8_t id);
extern void open_cfw_retained_cordio_wstr_reverse_copy(
    uint8_t *destination, const uint8_t *source, uint16_t length);
extern void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size);
extern void *open_cfw_runtime_memory_zero(void *destination, uint32_t size);
extern void *open_cfw_cordio_dm_sec_get_ecc_key(void);
extern void open_cfw_cordio_dm_sec_smp_callback_execute(void *message);
extern void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smp_sc_act_ccb *ccb, void *message);
extern uint8_t open_cfw_cordio_smp_sc_allocate_scratch_buffers(
    struct open_cfw_smp_sc_act_ccb *ccb);
extern void open_cfw_cordio_smp_sc_free_scratch_buffers(
    struct open_cfw_smp_sc_act_ccb *ccb);
extern uint8_t *open_cfw_cordio_smp_sc_allocate(
    uint8_t size, struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message);
extern uint8_t *open_cfw_cordio_smp_sc_cat(
    uint8_t *destination, const uint8_t *source, uint8_t length);
extern uint8_t *open_cfw_cordio_smp_sc_cat128(
    uint8_t *destination, uint8_t *source);
extern void open_cfw_cordio_smp_sc_cmac(
    const uint8_t *key, uint8_t *text, uint8_t text_length,
    struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message);
extern void open_cfw_cordio_smp_sc_calculate_f4(
    struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message, uint8_t *u, uint8_t *v,
    uint8_t z, uint8_t *x);
extern void open_cfw_cordio_smp_sc_cancel_with_reattempt(
    uint8_t connection_id, struct open_cfw_smp_sc_act_header *header,
    uint8_t status);
extern void open_cfw_cordio_smp_act_cleanup(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg);
extern void open_cfw_cordio_smp_act_pairing_failed(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg);
extern void open_cfw_cordio_smp_act_send_pairing_failed(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t reason);
extern void open_cfw_cordio_smp_act_start_response_timer(
    struct open_cfw_smp_sc_act_ccb *ccb);
extern uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length);
extern void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *packet);
extern void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16]);
extern uint8_t open_cfw_retained_cordio_sec_ecc_gen_shared_secret(
    const struct open_cfw_smp_sc_act_ecc_key *key, uint8_t handler_id,
    uint16_t parameter, uint8_t event);

uint8_t *open_cfw_cordio_smp_sc_act_cat_initiator_address(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *buffer);
uint8_t *open_cfw_cordio_smp_sc_act_cat_responder_address(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *buffer);
void open_cfw_cordio_smp_sc_act_cleanup(
    struct open_cfw_smp_sc_act_ccb *ccb,
    union open_cfw_smp_sc_act_message *message);
void open_cfw_cordio_smp_sc_act_pairing_failed(
    struct open_cfw_smp_sc_act_ccb *ccb,
    union open_cfw_smp_sc_act_message *message);

static __attribute__((always_inline, unused)) inline uint8_t
open_cfw_smp_sc_act_address_is_zero(
    const uint8_t *address)
{
    uint8_t value = 0U;
    uint8_t index;
    for (index = 0U; index < OPEN_CFW_SMP_SC_ACT_ADDRESS_BYTES; index++) {
        value |= address[index];
    }
    return value == 0U ? 1U : 0U;
}

static __attribute__((always_inline, unused)) inline uint8_t *
open_cfw_smp_sc_act_cat_address(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *buffer, uint8_t local)
{
    uint8_t *rpa;
    uint8_t *address;
    uint8_t type;
    if (local != 0U) {
        rpa = open_cfw_retained_cordio_dm_conn_local_rpa(ccb->connection_id);
        address = open_cfw_retained_cordio_dm_conn_local_address(
            ccb->connection_id);
        type = open_cfw_retained_cordio_dm_conn_local_address_type(
            ccb->connection_id);
    } else {
        rpa = open_cfw_retained_cordio_dm_conn_peer_rpa(ccb->connection_id);
        address = open_cfw_retained_cordio_dm_conn_peer_address(
            ccb->connection_id);
        type = open_cfw_retained_cordio_dm_conn_peer_address_type(
            ccb->connection_id);
    }
    if (rpa != NULL && open_cfw_smp_sc_act_address_is_zero(rpa) == 0U) {
        *buffer++ = 1U;
        address = rpa;
    } else {
        *buffer++ = type;
    }
    if (address != NULL) {
        open_cfw_retained_cordio_wstr_reverse_copy(
            buffer, address, OPEN_CFW_SMP_SC_ACT_ADDRESS_BYTES);
        buffer += OPEN_CFW_SMP_SC_ACT_ADDRESS_BYTES;
    }
    return buffer;
}

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_CAT_INITIATOR_ONLY)
__attribute__((noinline)) uint8_t *open_cfw_cordio_smp_sc_act_cat_initiator_address(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *buffer)
{
    return open_cfw_smp_sc_act_cat_address(ccb, buffer, ccb->initiator);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_CAT_RESPONDER_ONLY)
__attribute__((noinline)) uint8_t *open_cfw_cordio_smp_sc_act_cat_responder_address(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *buffer)
{
    return open_cfw_smp_sc_act_cat_address(ccb, buffer,
        ccb->initiator == 0U ? 1U : 0U);
}
#endif

static __attribute__((unused)) void open_cfw_smp_sc_act_execute(
    struct open_cfw_smp_sc_act_ccb *ccb,
    struct open_cfw_smp_sc_act_header *message, uint8_t event, uint8_t status)
{
    message->param = ccb->connection_id;
    message->event = event;
    message->status = status;
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, message);
}

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_PROCESS_PAIRING_ONLY)
__attribute__((noinline)) uint8_t open_cfw_cordio_smp_sc_act_process_pairing(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *oob, uint8_t *display)
{
    uint8_t just_works = 1U;
    uint8_t local_auth;
    uint8_t secure = (uint8_t)(
        (ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] &
         ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] &
         OPEN_CFW_SMP_SC_ACT_AUTH_SC) != 0U);
    struct open_cfw_smp_sc_act_header message = {0U, 0U, 0U};
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    *display = 0U;
    *oob = 0U;

    if ((secure != 0U &&
         (ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_OOB] ==
              OPEN_CFW_SMP_SC_ACT_OOB_PRESENT ||
          ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_OOB] ==
              OPEN_CFW_SMP_SC_ACT_OOB_PRESENT)) ||
        (secure == 0U &&
         ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_OOB] ==
             OPEN_CFW_SMP_SC_ACT_OOB_PRESENT &&
         ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_OOB] ==
             OPEN_CFW_SMP_SC_ACT_OOB_PRESENT)) {
        *oob = OPEN_CFW_SMP_SC_ACT_OOB_PRESENT;
        just_works = 0U;
    }

    if (*oob == 0U &&
        ((ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] |
          ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH]) &
         OPEN_CFW_SMP_SC_ACT_AUTH_MITM) != 0U &&
        ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] !=
            OPEN_CFW_SMP_SC_ACT_IO_NONE &&
        ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] !=
            OPEN_CFW_SMP_SC_ACT_IO_NONE &&
        !(((ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                 OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_ONLY) ||
            (ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                 OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO)) &&
           ((ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                 OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_ONLY) ||
            (ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                 OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO)))) {
        just_works = 0U;
        *display = (uint8_t)(
            ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_ONLY ||
            ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO ||
            (ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                 OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_DISPLAY &&
             (ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                  OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_ONLY ||
              ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                  OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_DISPLAY)));
        if (!(ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                  OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_ONLY &&
              ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                  OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_ONLY)) {
            *display ^= (uint8_t)(ccb->initiator == 0U);
        }
    }

    if (secure != 0U) {
        const struct open_cfw_smp_sc_act_ecc_key *key;
        if (OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK.lesc_supported == 0U) {
            open_cfw_smp_sc_act_execute(ccb, &message,
                OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
                OPEN_CFW_SMP_SC_ACT_ERROR_AUTH);
            return 0U;
        }
        sc->lesc_enabled = 1U;
        sc->authentication_type = OPEN_CFW_SMP_SC_ACT_AUTH_JUST_WORKS;
        sc->display = *display;
        if (*oob != 0U) {
            sc->authentication_type = OPEN_CFW_SMP_SC_ACT_AUTH_OOB;
        } else if (just_works == 0U) {
            sc->authentication_type = OPEN_CFW_SMP_SC_ACT_AUTH_PASSKEY;
            if ((ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                    OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_DISPLAY &&
                 (ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                      OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO ||
                  ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                      OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_DISPLAY)) ||
                (ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                     OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO &&
                 ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                     OPEN_CFW_SMP_SC_ACT_IO_KEYBOARD_DISPLAY)) {
                sc->authentication_type = OPEN_CFW_SMP_SC_ACT_AUTH_NUMERIC;
            } else if ((ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] &
                        ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] &
                        OPEN_CFW_SMP_SC_ACT_AUTH_KEYPRESS) != 0U) {
                sc->keypress_notify = 1U;
            }
        } else if (ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                       OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO &&
                   ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                       OPEN_CFW_SMP_SC_ACT_IO_DISPLAY_YES_NO) {
            sc->authentication_type = OPEN_CFW_SMP_SC_ACT_AUTH_NUMERIC;
            just_works = 0U;
        } else if (ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                       OPEN_CFW_SMP_SC_ACT_IO_NONE ||
                   ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO] ==
                       OPEN_CFW_SMP_SC_ACT_IO_NONE) {
            /* G2/R4 behavior: retain MITM for no-input/no-output JW. */
            just_works = 0U;
        }

        if (open_cfw_cordio_smp_sc_allocate_scratch_buffers(ccb) != 0U) {
            key = (const struct open_cfw_smp_sc_act_ecc_key *)
                open_cfw_cordio_dm_sec_get_ecc_key();
            if (key == NULL) {
                open_cfw_smp_sc_act_execute(ccb, &message,
                    OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
                    OPEN_CFW_SMP_SC_ACT_ERROR_UNSPECIFIED);
                return 0U;
            }
            open_cfw_iar_memcpy_void(sc->local_public_key->x,
                key->public_x, OPEN_CFW_SMP_SC_ACT_PUBLIC_KEY_BYTES);
            open_cfw_iar_memcpy_void(sc->local_public_key->y,
                key->public_y, OPEN_CFW_SMP_SC_ACT_PUBLIC_KEY_BYTES);
            open_cfw_iar_memcpy_void(sc->private_key, key->private_key,
                OPEN_CFW_SMP_SC_ACT_PRIVATE_KEY_BYTES);
            open_cfw_smp_sc_act_execute(ccb, &message, 17U, 0U);
        } else {
            open_cfw_smp_sc_act_execute(ccb, &message,
                OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
                OPEN_CFW_SMP_SC_ACT_ERROR_UNSPECIFIED);
        }
    } else if ((OPEN_CFW_SMP_SC_ACT_CONFIG.authentication &
                OPEN_CFW_SMP_SC_ACT_AUTH_SC) != 0U) {
        open_cfw_smp_sc_act_execute(ccb, &message,
            OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
            OPEN_CFW_SMP_SC_ACT_ERROR_AUTH);
        return 0U;
    } else {
        sc->lesc_enabled = 0U;
        open_cfw_smp_sc_act_execute(ccb, &message, 18U, 0U);
    }

    ccb->authentication = (uint8_t)(
        ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] &
        ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH]);
    if (just_works == 0U) {
        ccb->authentication |= OPEN_CFW_SMP_SC_ACT_AUTH_MITM;
    } else {
        ccb->authentication &= (uint8_t)~OPEN_CFW_SMP_SC_ACT_AUTH_MITM;
    }
    local_auth = ccb->initiator != 0U ?
        ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH] :
        ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH];
    if (just_works != 0U &&
        (OPEN_CFW_SMP_SC_ACT_CONFIG.authentication & local_auth &
         OPEN_CFW_SMP_SC_ACT_AUTH_MITM) != 0U) {
        open_cfw_smp_sc_act_execute(ccb, &message,
            OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
            OPEN_CFW_SMP_SC_ACT_ERROR_AUTH);
        return 0U;
    }
    if (ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_MAX_KEY] <
            OPEN_CFW_SMP_SC_ACT_CONFIG.minimum_key_length ||
        ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_MAX_KEY] <
            OPEN_CFW_SMP_SC_ACT_CONFIG.minimum_key_length) {
        open_cfw_smp_sc_act_execute(ccb, &message,
            OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
            OPEN_CFW_SMP_SC_ACT_ERROR_KEY_SIZE);
        return 0U;
    }
    return 1U;
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_AUTH_REQUEST_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_authentication_request(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t oob, uint8_t display)
{
    union {
        struct open_cfw_smp_sc_act_auth_response response;
        struct {
            struct open_cfw_smp_sc_act_header header;
            uint8_t oob;
            uint8_t display;
        } request;
    } message;
    if ((ccb->secure_connections->lesc_enabled == 0U &&
         (ccb->authentication & OPEN_CFW_SMP_SC_ACT_AUTH_MITM) != 0U) ||
        (ccb->secure_connections->lesc_enabled != 0U &&
         ccb->secure_connections->authentication_type ==
             OPEN_CFW_SMP_SC_ACT_AUTH_OOB)) {
        message.request.header.param = ccb->connection_id;
        message.request.header.event = OPEN_CFW_SMP_SC_ACT_DM_AUTH_REQUEST;
        message.request.header.status = 0U;
        message.request.oob = oob;
        message.request.display = display;
        open_cfw_cordio_dm_sec_smp_callback_execute(&message.request);
    } else {
        message.response.header.param = ccb->connection_id;
        message.response.header.event = OPEN_CFW_SMP_SC_ACT_EVENT_AUTH_RESPONSE;
        message.response.header.status = 0U;
        message.response.data[0] = 0U;
        message.response.data[1] = 0U;
        message.response.data[2] = 0U;
        message.response.length = 4U;
        open_cfw_retained_cordio_smp_state_machine_execute(
            ccb, &message.response);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_CLEANUP_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_cleanup(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    open_cfw_cordio_smp_act_cleanup(ccb, msg);
    open_cfw_cordio_smp_sc_free_scratch_buffers(ccb);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_PAIRING_FAILED_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_pairing_failed(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    open_cfw_cordio_smp_sc_act_cleanup(ccb, msg);
    open_cfw_cordio_smp_act_pairing_failed(ccb, msg);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_PAIRING_CANCEL_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_pairing_cancel(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    open_cfw_cordio_smp_act_send_pairing_failed(ccb, msg->header.status);
    open_cfw_cordio_smp_sc_act_pairing_failed(ccb, msg);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_AUTH_SELECT_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_authentication_select(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *packet = msg->data.packet + OPEN_CFW_SMP_SC_ACT_PDU_OFFSET;
    struct open_cfw_smp_sc_act_header header = {ccb->connection_id, 0U, 0U};
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    open_cfw_retained_cordio_wstr_reverse_copy(sc->peer_public_key->x,
        &packet[OPEN_CFW_SMP_SC_ACT_PUBLIC_X_POSITION], 32U);
    open_cfw_retained_cordio_wstr_reverse_copy(sc->peer_public_key->y,
        &packet[OPEN_CFW_SMP_SC_ACT_PUBLIC_Y_POSITION], 32U);
    if (sc->authentication_type == OPEN_CFW_SMP_SC_ACT_AUTH_NUMERIC ||
        sc->authentication_type == OPEN_CFW_SMP_SC_ACT_AUTH_JUST_WORKS) {
        header.event = OPEN_CFW_SMP_SC_ACT_EVENT_JW_NC;
    } else if (sc->authentication_type == OPEN_CFW_SMP_SC_ACT_AUTH_OOB) {
        header.event = OPEN_CFW_SMP_SC_ACT_EVENT_OOB;
    } else if (sc->authentication_type == OPEN_CFW_SMP_SC_ACT_AUTH_PASSKEY) {
        header.event = OPEN_CFW_SMP_SC_ACT_EVENT_PASSKEY;
    } else {
        header.event = OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL;
        header.status = OPEN_CFW_SMP_SC_ACT_ERROR_UNSPECIFIED;
    }
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, &header);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_PASSKEY_SETUP_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_passkey_setup(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    struct {
        struct open_cfw_smp_sc_act_header header;
        uint8_t oob;
        uint8_t display;
    } request;
    (void)msg;
    ccb->secure_connections->passkey_position = 0U;
    ccb->next_command = OPEN_CFW_SMP_SC_ACT_CMD_CONFIRM;
    request.header.param = ccb->connection_id;
    request.header.event = OPEN_CFW_SMP_SC_ACT_DM_AUTH_REQUEST;
    request.header.status = 0U;
    request.oob = 0U;
    request.display = ccb->secure_connections->display;
    open_cfw_cordio_dm_sec_smp_callback_execute(&request);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_JWNC_F4_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    open_cfw_cordio_smp_sc_calculate_f4(ccb, &msg->header,
        ccb->initiator != 0U ? sc->peer_public_key->x : sc->local_public_key->x,
        ccb->initiator != 0U ? sc->local_public_key->x : sc->peer_public_key->x,
        0U, sc->scratch->responder_random);
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_JWNC_G2_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    uint8_t *text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_ACT_G2_TEXT_BYTES, ccb, &msg->header);
    uint8_t *cursor = text;
    if (text != NULL) {
        cursor = open_cfw_cordio_smp_sc_cat(cursor,
            ccb->initiator != 0U ? sc->local_public_key->x : sc->peer_public_key->x,
            32U);
        cursor = open_cfw_cordio_smp_sc_cat(cursor,
            ccb->initiator != 0U ? sc->peer_public_key->x : sc->local_public_key->x,
            32U);
        (void)open_cfw_cordio_smp_sc_cat128(cursor,
            sc->scratch->responder_random);
        open_cfw_cordio_smp_sc_cmac(sc->scratch->initiator_random, text,
            OPEN_CFW_SMP_SC_ACT_G2_TEXT_BYTES, ccb, &msg->header);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_JWNC_DISPLAY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_jwnc_display(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    if (ccb->secure_connections->authentication_type ==
            OPEN_CFW_SMP_SC_ACT_AUTH_NUMERIC) {
        struct {
            struct open_cfw_smp_sc_act_header header;
            uint8_t confirm[16];
        } indication;
        indication.header.param = ccb->connection_id;
        indication.header.event = OPEN_CFW_SMP_SC_ACT_DM_COMPARE;
        indication.header.status = OPEN_CFW_SMP_SC_ACT_SUCCESS;
        open_cfw_retained_cordio_calc128_copy(
            indication.confirm, msg->aes.ciphertext);
        open_cfw_cordio_dm_sec_smp_callback_execute(&indication);
    } else {
        open_cfw_smp_sc_act_execute(ccb, &msg->header,
            OPEN_CFW_SMP_SC_ACT_EVENT_USER_CONFIRM,
            OPEN_CFW_SMP_SC_ACT_SUCCESS);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_PASSKEY_RECEIVE_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_passkey_receive(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *command = msg->data.packet + OPEN_CFW_SMP_SC_ACT_PDU_OFFSET;
    if (command[0] == OPEN_CFW_SMP_SC_ACT_CMD_KEYPRESS) {
        struct {
            struct open_cfw_smp_sc_act_header header;
            uint8_t notification;
        } indication;
        indication.header.param = ccb->connection_id;
        indication.header.event = OPEN_CFW_SMP_SC_ACT_DM_KEYPRESS;
        indication.header.status = OPEN_CFW_SMP_SC_ACT_SUCCESS;
        indication.notification = command[1];
        open_cfw_cordio_dm_sec_smp_callback_execute(&indication);
    } else if (command[0] == OPEN_CFW_SMP_SC_ACT_CMD_CONFIRM) {
        msg->header.event = OPEN_CFW_SMP_SC_ACT_EVENT_EARLY_CONFIRM;
        msg->header.status = OPEN_CFW_SMP_SC_ACT_SUCCESS;
        open_cfw_retained_cordio_smp_state_machine_execute(ccb, msg);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_PASSKEY_SEND_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_passkey_send(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *packet;
    if (ccb->secure_connections->keypress_notify == 0U) {
        return;
    }
    open_cfw_cordio_smp_act_start_response_timer(ccb);
    packet = open_cfw_cordio_smp_main_message_allocate(
        OPEN_CFW_SMP_SC_ACT_PDU_OFFSET +
        OPEN_CFW_SMP_SC_ACT_KEYPRESS_MESSAGE_BYTES);
    if (packet != NULL) {
        packet[OPEN_CFW_SMP_SC_ACT_PDU_OFFSET] =
            OPEN_CFW_SMP_SC_ACT_CMD_KEYPRESS;
        packet[OPEN_CFW_SMP_SC_ACT_PDU_OFFSET + 1U] = msg->keypress.keypress;
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    } else {
        open_cfw_smp_sc_act_execute(ccb, &msg->header,
            OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
            OPEN_CFW_SMP_SC_ACT_ERROR_UNSPECIFIED);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_SHARED_SECRET_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_calculate_shared_secret(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    struct open_cfw_smp_sc_act_ecc_key key;
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    open_cfw_iar_memcpy_void(key.private_key, sc->private_key, 32U);
    open_cfw_iar_memcpy_void(key.public_x, sc->peer_public_key->x, 32U);
    open_cfw_iar_memcpy_void(key.public_y, sc->peer_public_key->y, 32U);
    if (open_cfw_retained_cordio_sec_ecc_gen_shared_secret(&key,
            OPEN_CFW_SMP_SC_ACT_CONTROL_BLOCK.handler_id,
            ccb->connection_id, 25U) == 0U) {
        open_cfw_smp_sc_act_execute(ccb, &msg->header,
            OPEN_CFW_SMP_SC_ACT_EVENT_CANCEL,
            OPEN_CFW_SMP_SC_ACT_ERROR_MEMORY);
    }
}
#endif

static __attribute__((unused)) uint8_t *open_cfw_smp_sc_act_f5_prefix(
    struct open_cfw_smp_sc_act_ccb *ccb, uint8_t *cursor, uint8_t counter)
{
    *cursor++ = counter;
    *cursor++ = 0x62U;
    *cursor++ = 0x74U;
    *cursor++ = 0x6cU;
    *cursor++ = 0x65U;
    cursor = open_cfw_cordio_smp_sc_cat128(cursor,
        ccb->secure_connections->scratch->initiator_random);
    cursor = open_cfw_cordio_smp_sc_cat128(cursor,
        ccb->secure_connections->scratch->responder_random);
    cursor = open_cfw_cordio_smp_sc_act_cat_initiator_address(ccb, cursor);
    cursor = open_cfw_cordio_smp_sc_act_cat_responder_address(ccb, cursor);
    *cursor++ = 1U;
    *cursor++ = 0U;
    return cursor;
}

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_F5_T_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_calculate_f5_t(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t salt[16];
    uint8_t *text;
    if (msg->header.status != OPEN_CFW_SMP_SC_ACT_SUCCESS) {
        open_cfw_cordio_smp_sc_cancel_with_reattempt(ccb->connection_id,
            &msg->header, OPEN_CFW_SMP_SC_ACT_ERROR_DH_KEY);
        open_cfw_retained_cordio_smp_state_machine_execute(ccb, msg);
        return;
    }
    text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_ACT_F5_T_BYTES, ccb, &msg->header);
    if (text != NULL) {
        salt[0] = 0x6cU; salt[1] = 0x88U; salt[2] = 0x83U;
        salt[3] = 0x91U; salt[4] = 0xaaU; salt[5] = 0xf5U;
        salt[6] = 0xa5U; salt[7] = 0x38U; salt[8] = 0x60U;
        salt[9] = 0x37U; salt[10] = 0x0bU; salt[11] = 0xdbU;
        salt[12] = 0x5aU; salt[13] = 0x60U; salt[14] = 0x83U;
        salt[15] = 0xbeU;
        open_cfw_iar_memcpy_void(text, msg->ecc.secret,
            OPEN_CFW_SMP_SC_ACT_DH_KEY_BYTES);
        open_cfw_cordio_smp_sc_cmac(salt, text,
            OPEN_CFW_SMP_SC_ACT_F5_T_BYTES, ccb, &msg->header);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_F5_MAC_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_calculate_f5_mac(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *text;
    open_cfw_retained_cordio_calc128_copy(
        ccb->secure_connections->ltk->temporary_ltk, msg->cmac.ciphertext);
    text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_ACT_F5_TEXT_BYTES, ccb, &msg->header);
    if (text != NULL) {
        (void)open_cfw_smp_sc_act_f5_prefix(ccb, text, 0U);
        open_cfw_cordio_smp_sc_cmac(
            ccb->secure_connections->ltk->temporary_ltk, text,
            OPEN_CFW_SMP_SC_ACT_F5_TEXT_BYTES, ccb, &msg->header);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_F5_LTK_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_calculate_f5_ltk(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *text;
    open_cfw_retained_cordio_calc128_copy(
        ccb->secure_connections->ltk->mac, msg->cmac.ciphertext);
    text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_ACT_F5_TEXT_BYTES, ccb, &msg->header);
    if (text != NULL) {
        (void)open_cfw_smp_sc_act_f5_prefix(ccb, text, 1U);
        open_cfw_cordio_smp_sc_cmac(
            ccb->secure_connections->ltk->temporary_ltk, text,
            OPEN_CFW_SMP_SC_ACT_F5_TEXT_BYTES, ccb, &msg->header);
    }
}
#endif

static __attribute__((unused)) uint8_t *open_cfw_smp_sc_act_f6_randoms(
    uint8_t *cursor, struct open_cfw_smp_sc_act_sc_ccb *sc,
    uint8_t responder)
{
    cursor = open_cfw_cordio_smp_sc_cat128(cursor,
        responder != 0U ? sc->scratch->responder_random :
                          sc->scratch->initiator_random);
    cursor = open_cfw_cordio_smp_sc_cat128(cursor,
        responder != 0U ? sc->scratch->initiator_random :
                          sc->scratch->responder_random);
    return open_cfw_cordio_smp_sc_cat128(cursor,
        responder != 0U ? sc->scratch->ra : sc->scratch->rb);
}

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_F6_EA_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_calculate_f6_ea(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *text;
    uint8_t *cursor;
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    open_cfw_retained_cordio_wstr_reverse_copy(
        sc->ltk->temporary_ltk, msg->aes.ciphertext, 16U);
    text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_ACT_F6_TEXT_BYTES, ccb, &msg->header);
    if (text != NULL) {
        cursor = open_cfw_smp_sc_act_f6_randoms(text, sc, 0U);
        *cursor++ = ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH];
        *cursor++ = ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_OOB];
        *cursor++ = ccb->pair_request[OPEN_CFW_SMP_SC_ACT_PAIR_IO];
        cursor = open_cfw_cordio_smp_sc_act_cat_initiator_address(ccb, cursor);
        (void)open_cfw_cordio_smp_sc_act_cat_responder_address(ccb, cursor);
        open_cfw_cordio_smp_sc_cmac(sc->ltk->mac, text,
            OPEN_CFW_SMP_SC_ACT_F6_TEXT_BYTES, ccb, &msg->header);
    }
}
#endif

#if OPEN_CFW_SMP_SC_ACT_ALL || defined(OPEN_CFW_SMP_SC_ACT_F6_EB_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smp_sc_act_calculate_f6_eb(
    struct open_cfw_smp_sc_act_ccb *ccb, union open_cfw_smp_sc_act_message *msg)
{
    uint8_t *text;
    uint8_t *cursor;
    struct open_cfw_smp_sc_act_sc_ccb *sc = ccb->secure_connections;
    text = open_cfw_cordio_smp_sc_allocate(
        OPEN_CFW_SMP_SC_ACT_F6_TEXT_BYTES, ccb, &msg->header);
    if (text != NULL) {
        cursor = open_cfw_smp_sc_act_f6_randoms(text, sc, 1U);
        *cursor++ = ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_AUTH];
        *cursor++ = ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_OOB];
        *cursor++ = ccb->pair_response[OPEN_CFW_SMP_SC_ACT_PAIR_IO];
        cursor = open_cfw_cordio_smp_sc_act_cat_responder_address(ccb, cursor);
        (void)open_cfw_cordio_smp_sc_act_cat_initiator_address(ccb, cursor);
        open_cfw_cordio_smp_sc_cmac(sc->ltk->mac, text,
            OPEN_CFW_SMP_SC_ACT_F6_TEXT_BYTES, ccb, &msg->header);
    }
    open_cfw_retained_cordio_calc128_copy(
        sc->scratch->initiator_random, msg->aes.ciphertext);
}
#endif
