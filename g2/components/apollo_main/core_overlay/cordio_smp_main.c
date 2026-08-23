/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production adapter for the twenty linked Packetcraft Cordio r20.05c
 * smp_main.c functions retained by G2 2.2.6.10.  It preserves the r20
 * keyReady/LESC behavior and Ambiq stale-AES-result queue cleanup observed
 * in the authenticated stock image while making the G2 SRAM ABI explicit.
 */

#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMP_MAIN_PACKET_LENGTH_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_L2C_DATA_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_L2C_CTRL_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_RESUME_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_DM_CONN_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_CCB_HANDLE_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_CCB_CONN_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_C1_PART1_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_C1_PART2_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_S1_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_GENERATE_LTK_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_SEND_PKT_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_STATE_IDLE_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_MSG_ALLOC_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_DM_MSG_SEND_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_DM_ENCRYPT_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_SC_LEVEL_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_LESC_ENABLED_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_GET_STK_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_INIT_ONLY) && \
    !defined(OPEN_CFW_SMP_MAIN_HANDLER_ONLY)
#define OPEN_CFW_SMP_MAIN_ALL 1
#else
#define OPEN_CFW_SMP_MAIN_ALL 0
#endif

#define OPEN_CFW_SMP_CONNECTION_COUNT 3U
#define OPEN_CFW_SMP_PACKET_OFFSET 8U
#define OPEN_CFW_SMP_CID 6U
#define OPEN_CFW_SMP_PAIR_REQUEST_LENGTH 7U
#define OPEN_CFW_SMP_PAIR_RESPONSE_LENGTH 7U
#define OPEN_CFW_SMP_KEY_LENGTH 16U
#define OPEN_CFW_SMP_RANDOM8_LENGTH 8U
#define OPEN_CFW_SMP_COMMAND_PAIR_REQUEST 1U
#define OPEN_CFW_SMP_COMMAND_PAIR_FAILED 5U
#define OPEN_CFW_SMP_COMMAND_SECURITY_REQUEST 11U
#define OPEN_CFW_SMP_COMMAND_MAX 15U
#define OPEN_CFW_SMP_MESSAGE_CANCEL 3U
#define OPEN_CFW_SMP_MESSAGE_COMMAND 6U
#define OPEN_CFW_SMP_MESSAGE_PAIR_FAILED 7U
#define OPEN_CFW_SMP_MESSAGE_ENCRYPT_COMPLETE 8U
#define OPEN_CFW_SMP_MESSAGE_ENCRYPT_FAILED 9U
#define OPEN_CFW_SMP_MESSAGE_CONNECTION_CLOSE 10U
#define OPEN_CFW_SMP_MESSAGE_AES_COMPLETE 11U
#define OPEN_CFW_SMP_MESSAGE_SEND_NEXT_KEY 12U
#define OPEN_CFW_SMP_MESSAGE_WAIT_TIMEOUT 16U
#define OPEN_CFW_SMP_MESSAGE_CMAC_COMPLETE 28U
#define OPEN_CFW_SMP_DATABASE_SERVICE_EVENT 32U
#define OPEN_CFW_DM_CONNECTION_OPEN_EVENT 39U
#define OPEN_CFW_DM_CONNECTION_CLOSE_EVENT 40U
#define OPEN_CFW_DM_SECURITY_KEY_EVENT 47U
#define OPEN_CFW_DM_SECURITY_ERROR_BASE 32U
#define OPEN_CFW_DM_SECURITY_LEVEL_ENCRYPTED 1U
#define OPEN_CFW_DM_SECURITY_LEVEL_AUTHENTICATED 2U
#define OPEN_CFW_DM_SECURITY_LEVEL_LESC 3U
#define OPEN_CFW_DM_KEY_LOCAL_LTK 1U
#define OPEN_CFW_SMP_AUTH_MITM 4U
#define OPEN_CFW_SMP_AES_TOKEN_INVALID 0xFFU
#define OPEN_CFW_SMP_L2C_FLOW_DISABLE 1U
#define OPEN_CFW_SMP_ROLE_MASTER 0U
#define OPEN_CFW_SMP_LEGACY_INITIATOR_ATTEMPTS 12U
#define OPEN_CFW_SMP_LEGACY_RESPONDER_ATTEMPTS 13U
#define OPEN_CFW_SMP_SC_INITIATOR_ATTEMPTS 36U
#define OPEN_CFW_SMP_SC_RESPONDER_ATTEMPTS 38U

struct open_cfw_smp_main_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};

struct open_cfw_smp_main_timer {
    uint32_t next;
    struct open_cfw_smp_main_header message;
    uint32_t ticks;
    uint8_t handler_id;
    uint8_t is_started;
    uint8_t reserved[2];
};

union open_cfw_smp_main_scratch {
    struct {
        uint8_t b1[16];
        uint8_t b2[16];
        uint8_t b3[16];
        uint8_t b4[16];
    } buffers;
    struct {
        struct open_cfw_smp_main_header header;
        uint8_t key[16];
        uint8_t random[8];
        uint16_t diversifier;
        uint8_t type;
        uint8_t security_level;
        uint8_t encryption_key_length;
    } key_indication;
};

struct open_cfw_smp_main_sc_ltk {
    uint8_t mac[16];
    uint8_t temporary_ltk[16];
};

struct open_cfw_smp_main_sc_ccb {
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
    struct open_cfw_smp_main_sc_ltk *ltk;
};

struct open_cfw_smp_main_ccb {
    struct open_cfw_smp_main_timer response_timer;
    struct open_cfw_smp_main_timer wait_timer;
    uint8_t pair_request[7];
    uint8_t pair_response[7];
    uint8_t reserved46[2];
    union open_cfw_smp_main_scratch *scratch;
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
    struct open_cfw_smp_main_sc_ccb *secure_connections;
};

struct open_cfw_smp_main_control_block {
    struct open_cfw_smp_main_ccb connections[OPEN_CFW_SMP_CONNECTION_COUNT];
    const void *slave_interface;
    const void *master_interface;
    uint8_t handler_id;
    uint8_t reserved237[3];
    void *process_pairing;
    void *process_authentication;
    uint8_t lesc_supported;
    uint8_t reserved249[3];
};

struct open_cfw_smp_main_data_message {
    struct open_cfw_smp_main_header header;
    uint8_t *packet;
};

struct open_cfw_smp_main_cmac_message {
    struct open_cfw_smp_main_header header;
    uint8_t *ciphertext;
    uint8_t *plain_text;
};

#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_smp_main_ccb) == 0x4CU,
    "G2 SMP CCB ABI changed");
_Static_assert(sizeof(struct open_cfw_smp_main_control_block) == 0xFCU,
    "G2 SMP control-block ABI changed");
_Static_assert(offsetof(struct open_cfw_smp_main_ccb, scratch) == 0x30U,
    "G2 SMP scratch offset changed");
_Static_assert(offsetof(struct open_cfw_smp_main_ccb, connection_id) == 0x3DU,
    "G2 SMP connection-ID offset changed");
_Static_assert(offsetof(struct open_cfw_smp_main_ccb, key_ready) == 0x44U,
    "G2 SMP keyReady offset changed");
_Static_assert(offsetof(struct open_cfw_smp_main_ccb, secure_connections) == 0x48U,
    "G2 SMP SC pointer offset changed");
#endif

#ifndef OPEN_CFW_SMP_MAIN_CONTROL_BLOCK
#define OPEN_CFW_SMP_MAIN_CONTROL_BLOCK \
    (*(struct open_cfw_smp_main_control_block *)(uintptr_t)0x20070AECU)
#endif

#ifndef OPEN_CFW_SMP_MAIN_SECURITY_QUEUE
#define OPEN_CFW_SMP_MAIN_SECURITY_QUEUE ((void *)(uintptr_t)0x20072CD8U)
#endif

extern uint8_t open_cfw_retained_cordio_dm_conn_id_by_handle(uint16_t handle);
extern uint8_t open_cfw_retained_cordio_dm_conn_role(uint8_t connection_id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_local_address(uint8_t connection_id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_local_rpa(uint8_t connection_id);
extern uint8_t open_cfw_retained_cordio_dm_conn_local_address_type(uint8_t connection_id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_peer_address(uint8_t connection_id);
extern uint8_t *open_cfw_retained_cordio_dm_conn_peer_rpa(uint8_t connection_id);
extern uint8_t open_cfw_retained_cordio_dm_conn_peer_address_type(uint8_t connection_id);
extern void open_cfw_retained_cordio_dm_conn_register(
    uint8_t client_id, void (*callback)(void *));
extern void open_cfw_retained_cordio_l2c_register(
    uint16_t cid, void (*data_callback)(uint16_t, uint16_t, uint8_t *),
    void (*control_callback)(struct open_cfw_smp_main_header *));
extern void open_cfw_retained_cordio_l2c_data_request(
    uint16_t cid, uint16_t handle, uint16_t length, uint8_t *packet);
extern void open_cfw_retained_cordio_wsf_timer_start_ms(
    struct open_cfw_smp_main_timer *timer, uint32_t milliseconds);
extern void *open_cfw_retained_cordio_wsf_msg_data_alloc(
    uint16_t length, uint16_t tailroom);
extern void open_cfw_retained_cordio_wsf_msg_send(uint8_t handler_id, void *message);
extern void *open_cfw_retained_cordio_wsf_msg_dequeue(void *queue, uint8_t *handler_id);
extern void open_cfw_retained_cordio_wsf_msg_free(void *message);
extern void open_cfw_retained_cordio_wsf_buffer_free(void *buffer);
extern uint8_t open_cfw_retained_cordio_sec_aes(
    const uint8_t key[16], const uint8_t data[16], uint8_t handler_id,
    uint16_t param, uint8_t event);
extern void open_cfw_retained_cordio_sec_rand(uint8_t *buffer, uint16_t length);
extern void open_cfw_cordio_dm_sec_smp_callback_execute(void *message);
extern void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smp_main_ccb *ccb, void *message);
extern uint32_t open_cfw_cordio_smp_db_get_pairing_disabled_time(
    uint8_t connection_id);
extern uint8_t open_cfw_cordio_smp_db_get_failure_count(
    uint8_t connection_id);
extern void open_cfw_cordio_smp_db_set_failure_count(
    uint8_t connection_id, uint8_t count);
extern void open_cfw_cordio_smp_db_init(void);
extern void open_cfw_cordio_smp_db_service(void);
extern void open_cfw_iar_memcpy_void(void *destination, const void *source,
    uint32_t size);
extern void *open_cfw_runtime_memory_zero(void *destination, uint32_t size);

struct open_cfw_smp_main_ccb *open_cfw_cordio_smp_main_ccb_by_handle(
    uint16_t handle);
struct open_cfw_smp_main_ccb *open_cfw_cordio_smp_main_ccb_by_connection_id(
    uint8_t connection_id);
void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_main_ccb *ccb, uint8_t *packet);
uint8_t open_cfw_cordio_smp_main_state_idle(
    struct open_cfw_smp_main_ccb *ccb);
uint8_t open_cfw_cordio_smp_main_get_sc_security_level(
    struct open_cfw_smp_main_ccb *ccb);
void open_cfw_cordio_smp_main_handler(
    uint32_t event, struct open_cfw_smp_main_header *message);
uint8_t open_cfw_cordio_smp_main_packet_length(uint8_t command);
void open_cfw_cordio_smp_main_l2c_data_callback(
    uint16_t handle, uint16_t length, uint8_t *packet);
void open_cfw_cordio_smp_main_l2c_control_callback(
    struct open_cfw_smp_main_header *message);
void open_cfw_cordio_smp_main_resume_attempts(uint8_t connection_id);
void open_cfw_cordio_smp_main_dm_connection_callback(void *event);

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_PACKET_LENGTH_ONLY)
__attribute__((noinline)) uint8_t open_cfw_cordio_smp_main_packet_length(
    uint8_t command)
{
    if (command == 1U || command == 2U) {
        return 7U;
    }
    if (command == 3U || command == 4U || command == 6U ||
        command == 8U || command == 10U || command == 13U) {
        return 17U;
    }
    if (command == 5U || command == 11U || command == 14U) {
        return 2U;
    }
    if (command == 7U) {
        return 11U;
    }
    if (command == 9U) {
        return 8U;
    }
    return command == 12U ? 65U : 0U;
}
#endif

static __attribute__((unused)) uint8_t open_cfw_smp_main_address_is_zero(
    const uint8_t address[6])
{
    uint8_t index;
    for (index = 0U; index < 6U; index++) {
        if (address[index] != 0U) {
            return 0U;
        }
    }
    return 1U;
}

static __attribute__((unused)) void open_cfw_smp_main_copy(
    void *destination, const void *source, uint32_t size)
{
    open_cfw_iar_memcpy_void(destination, source, size);
}

static __attribute__((unused)) void open_cfw_smp_main_cancel(
    struct open_cfw_smp_main_ccb *ccb)
{
    struct open_cfw_smp_main_header message = {
        0U, OPEN_CFW_SMP_MESSAGE_CANCEL, 8U
    };
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, &message);
}

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_CCB_HANDLE_ONLY)
struct open_cfw_smp_main_ccb *open_cfw_cordio_smp_main_ccb_by_handle(
    uint16_t handle)
{
    uint8_t connection_id =
        open_cfw_retained_cordio_dm_conn_id_by_handle(handle);
    return connection_id == 0U ? NULL :
        open_cfw_cordio_smp_main_ccb_by_connection_id(connection_id);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_CCB_CONN_ONLY)
struct open_cfw_smp_main_ccb *open_cfw_cordio_smp_main_ccb_by_connection_id(
    uint8_t connection_id)
{
    if (connection_id == 0U || connection_id > OPEN_CFW_SMP_CONNECTION_COUNT) {
        return NULL;
    }
    return &OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.connections[connection_id - 1U];
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_L2C_DATA_ONLY)
void open_cfw_cordio_smp_main_l2c_data_callback(
    uint16_t handle, uint16_t length, uint8_t *packet)
{
    struct open_cfw_smp_main_ccb *ccb =
        open_cfw_cordio_smp_main_ccb_by_handle(handle);
    uint8_t command;
    struct open_cfw_smp_main_data_message message;
    if (ccb == NULL || packet == NULL) {
        return;
    }
    command = packet[OPEN_CFW_SMP_PACKET_OFFSET];
    if (command < OPEN_CFW_SMP_COMMAND_PAIR_REQUEST ||
        command >= OPEN_CFW_SMP_COMMAND_MAX ||
        length != open_cfw_cordio_smp_main_packet_length(command) ||
        (command != ccb->next_command &&
         command != OPEN_CFW_SMP_COMMAND_PAIR_FAILED)) {
        return;
    }
    message.header.param = ccb->connection_id;
    message.header.event = command == OPEN_CFW_SMP_COMMAND_PAIR_FAILED ?
        OPEN_CFW_SMP_MESSAGE_PAIR_FAILED : OPEN_CFW_SMP_MESSAGE_COMMAND;
    message.header.status = command == OPEN_CFW_SMP_COMMAND_PAIR_FAILED ?
        packet[OPEN_CFW_SMP_PACKET_OFFSET + 1U] : 0U;
    message.packet = packet;
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, &message);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_L2C_CTRL_ONLY)
void open_cfw_cordio_smp_main_l2c_control_callback(
    struct open_cfw_smp_main_header *message)
{
    struct open_cfw_smp_main_ccb *ccb;
    uint8_t *packet;
    if (message == NULL) {
        return;
    }
    ccb = open_cfw_cordio_smp_main_ccb_by_connection_id(
        (uint8_t)message->param);
    if (ccb == NULL || ccb->connection_id == 0U) {
        return;
    }
    ccb->flow_disabled = message->event == OPEN_CFW_SMP_L2C_FLOW_DISABLE;
    if (ccb->flow_disabled != 0U) {
        return;
    }
    if (ccb->queued_packet != NULL) {
        packet = ccb->queued_packet;
        ccb->queued_packet = NULL;
        open_cfw_cordio_smp_main_send_packet(ccb, packet);
    }
    if (open_cfw_cordio_smp_main_state_idle(ccb) == 0U) {
        message->event = OPEN_CFW_SMP_MESSAGE_SEND_NEXT_KEY;
        open_cfw_retained_cordio_smp_state_machine_execute(ccb, message);
    }
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_RESUME_ONLY)
void open_cfw_cordio_smp_main_resume_attempts(uint8_t connection_id)
{
    struct open_cfw_smp_main_ccb *ccb =
        open_cfw_cordio_smp_main_ccb_by_connection_id(connection_id);
    uint32_t milliseconds =
        open_cfw_cordio_smp_db_get_pairing_disabled_time(
            connection_id);
    uint8_t master;
    if (ccb == NULL || milliseconds == 0U) {
        return;
    }
    master = open_cfw_retained_cordio_dm_conn_role(connection_id) ==
        OPEN_CFW_SMP_ROLE_MASTER;
    if (OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.lesc_supported != 0U) {
        ccb->state = master ? OPEN_CFW_SMP_SC_INITIATOR_ATTEMPTS :
            OPEN_CFW_SMP_SC_RESPONDER_ATTEMPTS;
    } else {
        ccb->state = master ? OPEN_CFW_SMP_LEGACY_INITIATOR_ATTEMPTS :
            OPEN_CFW_SMP_LEGACY_RESPONDER_ATTEMPTS;
    }
    ccb->wait_timer.message.event = OPEN_CFW_SMP_MESSAGE_WAIT_TIMEOUT;
    open_cfw_retained_cordio_wsf_timer_start_ms(
        &ccb->wait_timer, milliseconds);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_DM_CONN_ONLY)
void open_cfw_cordio_smp_main_dm_connection_callback(void *event)
{
    uint8_t *bytes = (uint8_t *)event;
    struct open_cfw_smp_main_header *header =
        (struct open_cfw_smp_main_header *)event;
    struct open_cfw_smp_main_ccb *ccb;
    struct open_cfw_smp_main_header close_message;
    if (event == NULL) {
        return;
    }
    ccb = open_cfw_cordio_smp_main_ccb_by_connection_id(
        (uint8_t)header->param);
    if (ccb == NULL) {
        return;
    }
    if (header->event == OPEN_CFW_DM_CONNECTION_OPEN_EVENT) {
        ccb->initiator =
            open_cfw_retained_cordio_dm_conn_role((uint8_t)header->param) ==
            OPEN_CFW_SMP_ROLE_MASTER;
        ccb->next_command = ccb->initiator != 0U ?
            OPEN_CFW_SMP_COMMAND_SECURITY_REQUEST :
            OPEN_CFW_SMP_COMMAND_PAIR_REQUEST;
        ccb->handle = *(uint16_t *)(void *)(bytes + 6U);
        ccb->connection_id = (uint8_t)header->param;
        ccb->security_request = 0U;
        ccb->flow_disabled = 0U;
        ccb->attempts =
            open_cfw_cordio_smp_db_get_failure_count(
                (uint8_t)header->param);
        ccb->last_sent_key = 0U;
        ccb->state = 0U;
        ccb->key_ready = 0U;
        open_cfw_cordio_smp_main_resume_attempts((uint8_t)header->param);
    } else if (ccb->connection_id != 0U &&
               header->event == OPEN_CFW_DM_CONNECTION_CLOSE_EVENT) {
        open_cfw_cordio_smp_db_set_failure_count(
            (uint8_t)header->param, ccb->attempts);
        close_message.param = header->param;
        close_message.event = OPEN_CFW_SMP_MESSAGE_CONNECTION_CLOSE;
        close_message.status =
            (uint8_t)(bytes[8] + OPEN_CFW_DM_SECURITY_ERROR_BASE);
        open_cfw_retained_cordio_smp_state_machine_execute(
            ccb, &close_message);
        ccb->connection_id = 0U;
        if (ccb->queued_packet != NULL) {
            open_cfw_retained_cordio_wsf_msg_free(ccb->queued_packet);
            ccb->queued_packet = NULL;
        }
    }
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_C1_PART1_ONLY)
void open_cfw_cordio_smp_main_calculate_c1_part1(
    struct open_cfw_smp_main_ccb *ccb, const uint8_t key[16],
    const uint8_t random[16])
{
    uint8_t buffer[16];
    uint8_t initiator_type;
    uint8_t responder_type;
    uint8_t index;
    if (ccb->initiator != 0U) {
        initiator_type = open_cfw_smp_main_address_is_zero(
            open_cfw_retained_cordio_dm_conn_local_rpa(ccb->connection_id)) ?
            open_cfw_retained_cordio_dm_conn_local_address_type(
                ccb->connection_id) : 1U;
        responder_type = open_cfw_smp_main_address_is_zero(
            open_cfw_retained_cordio_dm_conn_peer_rpa(ccb->connection_id)) ?
            open_cfw_retained_cordio_dm_conn_peer_address_type(
                ccb->connection_id) : 1U;
    } else {
        initiator_type = open_cfw_smp_main_address_is_zero(
            open_cfw_retained_cordio_dm_conn_peer_rpa(ccb->connection_id)) ?
            open_cfw_retained_cordio_dm_conn_peer_address_type(
                ccb->connection_id) : 1U;
        responder_type = open_cfw_smp_main_address_is_zero(
            open_cfw_retained_cordio_dm_conn_local_rpa(ccb->connection_id)) ?
            open_cfw_retained_cordio_dm_conn_local_address_type(
                ccb->connection_id) : 1U;
    }
    buffer[0] = (uint8_t)(initiator_type ^ random[0]);
    buffer[1] = (uint8_t)(responder_type ^ random[1]);
    for (index = 0U; index < 7U; index++) {
        buffer[2U + index] = (uint8_t)(ccb->pair_request[index] ^
            random[2U + index]);
        buffer[9U + index] = (uint8_t)(ccb->pair_response[index] ^
            random[9U + index]);
    }
    ccb->token = open_cfw_retained_cordio_sec_aes(
        key, buffer, OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.handler_id,
        ccb->connection_id, OPEN_CFW_SMP_MESSAGE_AES_COMPLETE);
    if (ccb->token == OPEN_CFW_SMP_AES_TOKEN_INVALID) {
        open_cfw_smp_main_cancel(ccb);
    }
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_C1_PART2_ONLY)
void open_cfw_cordio_smp_main_calculate_c1_part2(
    struct open_cfw_smp_main_ccb *ccb, const uint8_t key[16],
    const uint8_t part1[16])
{
    uint8_t buffer[16];
    uint8_t *initiator;
    uint8_t *responder;
    uint8_t index;
    if (ccb->initiator != 0U) {
        initiator = open_cfw_retained_cordio_dm_conn_local_rpa(
            ccb->connection_id);
        if (open_cfw_smp_main_address_is_zero(initiator) != 0U) {
            initiator = open_cfw_retained_cordio_dm_conn_local_address(
                ccb->connection_id);
        }
        responder = open_cfw_retained_cordio_dm_conn_peer_rpa(
            ccb->connection_id);
        if (open_cfw_smp_main_address_is_zero(responder) != 0U) {
            responder = open_cfw_retained_cordio_dm_conn_peer_address(
                ccb->connection_id);
        }
    } else {
        initiator = open_cfw_retained_cordio_dm_conn_peer_rpa(
            ccb->connection_id);
        if (open_cfw_smp_main_address_is_zero(initiator) != 0U) {
            initiator = open_cfw_retained_cordio_dm_conn_peer_address(
                ccb->connection_id);
        }
        responder = open_cfw_retained_cordio_dm_conn_local_rpa(
            ccb->connection_id);
        if (open_cfw_smp_main_address_is_zero(responder) != 0U) {
            responder = open_cfw_retained_cordio_dm_conn_local_address(
                ccb->connection_id);
        }
    }
    for (index = 0U; index < 6U; index++) {
        buffer[index] = (uint8_t)(responder[index] ^ part1[index]);
        buffer[6U + index] = (uint8_t)(initiator[index] ^ part1[6U + index]);
    }
    for (index = 12U; index < 16U; index++) {
        buffer[index] = part1[index];
    }
    ccb->token = open_cfw_retained_cordio_sec_aes(
        key, buffer, OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.handler_id,
        ccb->connection_id, OPEN_CFW_SMP_MESSAGE_AES_COMPLETE);
    if (ccb->token == OPEN_CFW_SMP_AES_TOKEN_INVALID) {
        open_cfw_smp_main_cancel(ccb);
    }
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_S1_ONLY)
void open_cfw_cordio_smp_main_calculate_s1(
    struct open_cfw_smp_main_ccb *ccb, const uint8_t key[16],
    const uint8_t random1[16], const uint8_t random2[16])
{
    uint8_t buffer[16];
    open_cfw_smp_main_copy(buffer, random2, 8U);
    open_cfw_smp_main_copy(buffer + 8U, random1, 8U);
    ccb->token = open_cfw_retained_cordio_sec_aes(
        key, buffer, OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.handler_id,
        ccb->connection_id, OPEN_CFW_SMP_MESSAGE_AES_COMPLETE);
    if (ccb->token == OPEN_CFW_SMP_AES_TOKEN_INVALID) {
        open_cfw_smp_main_cancel(ccb);
    }
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_GENERATE_LTK_ONLY)
void open_cfw_cordio_smp_main_generate_ltk(
    struct open_cfw_smp_main_ccb *ccb)
{
    union open_cfw_smp_main_scratch *scratch = ccb->scratch;
    uint8_t length = scratch->key_indication.encryption_key_length;
    uint8_t level = (ccb->authentication & OPEN_CFW_SMP_AUTH_MITM) != 0U ?
        OPEN_CFW_DM_SECURITY_LEVEL_AUTHENTICATED :
        OPEN_CFW_DM_SECURITY_LEVEL_ENCRYPTED;
    open_cfw_retained_cordio_sec_rand(
        scratch->key_indication.key, length);
    (void)open_cfw_runtime_memory_zero(
        scratch->key_indication.key + length,
        (uint32_t)(OPEN_CFW_SMP_KEY_LENGTH - length));
    scratch->key_indication.diversifier =
        (uint16_t)scratch->buffers.b4[0] |
        (uint16_t)((uint16_t)scratch->buffers.b4[1] << 8);
    open_cfw_smp_main_copy(scratch->key_indication.random,
        scratch->buffers.b4 + 2U, OPEN_CFW_SMP_RANDOM8_LENGTH);
    scratch->key_indication.type = OPEN_CFW_DM_KEY_LOCAL_LTK;
    scratch->key_indication.security_level = level;
    scratch->key_indication.header.event = OPEN_CFW_DM_SECURITY_KEY_EVENT;
    open_cfw_cordio_dm_sec_smp_callback_execute(
        &scratch->key_indication);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_SEND_PKT_ONLY)
void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_main_ccb *ccb, uint8_t *packet)
{
    if (ccb->flow_disabled != 0U) {
        if (ccb->queued_packet != NULL) {
            open_cfw_retained_cordio_wsf_msg_free(ccb->queued_packet);
        }
        ccb->queued_packet = packet;
    } else {
        open_cfw_retained_cordio_l2c_data_request(
            OPEN_CFW_SMP_CID, ccb->handle,
            open_cfw_cordio_smp_main_packet_length(
                packet[OPEN_CFW_SMP_PACKET_OFFSET]), packet);
    }
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_STATE_IDLE_ONLY)
uint8_t open_cfw_cordio_smp_main_state_idle(
    struct open_cfw_smp_main_ccb *ccb)
{
    return ccb->state == 0U ? 1U : 0U;
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_MSG_ALLOC_ONLY)
void *open_cfw_cordio_smp_main_message_allocate(uint16_t length)
{
    return open_cfw_retained_cordio_wsf_msg_data_alloc(length, 0U);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_DM_MSG_SEND_ONLY)
void open_cfw_cordio_smp_main_dm_message_send(void *message)
{
    open_cfw_retained_cordio_wsf_msg_send(
        OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.handler_id, message);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_DM_ENCRYPT_ONLY)
void open_cfw_cordio_smp_main_dm_encrypt_indication(
    struct open_cfw_smp_main_header *message)
{
    message->event = message->status == 0U ?
        OPEN_CFW_SMP_MESSAGE_ENCRYPT_COMPLETE :
        OPEN_CFW_SMP_MESSAGE_ENCRYPT_FAILED;
    open_cfw_cordio_smp_main_handler(0U, message);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_SC_LEVEL_ONLY)
uint8_t open_cfw_cordio_smp_main_get_sc_security_level(
    struct open_cfw_smp_main_ccb *ccb)
{
    if ((ccb->authentication & OPEN_CFW_SMP_AUTH_MITM) == 0U) {
        return OPEN_CFW_DM_SECURITY_LEVEL_ENCRYPTED;
    }
    return (ccb->pair_request[4] < ccb->pair_response[4] ?
        ccb->pair_request[4] : ccb->pair_response[4]) == 16U ?
        OPEN_CFW_DM_SECURITY_LEVEL_LESC :
        OPEN_CFW_DM_SECURITY_LEVEL_AUTHENTICATED;
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_LESC_ENABLED_ONLY)
uint8_t open_cfw_cordio_smp_main_dm_lesc_enabled(uint8_t connection_id)
{
    struct open_cfw_smp_main_ccb *ccb =
        open_cfw_cordio_smp_main_ccb_by_connection_id(connection_id);
    return ccb == NULL || ccb->secure_connections == NULL ? 0U :
        ccb->secure_connections->lesc_enabled;
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_GET_STK_ONLY)
uint8_t *open_cfw_cordio_smp_main_dm_get_stk(
    uint8_t connection_id, uint8_t *security_level)
{
    struct open_cfw_smp_main_ccb *ccb =
        open_cfw_cordio_smp_main_ccb_by_connection_id(connection_id);
    if (ccb == NULL || ccb->key_ready == 0U) {
        return NULL;
    }
    if (OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.lesc_supported != 0U &&
        ccb->secure_connections != NULL &&
        ccb->secure_connections->lesc_enabled != 0U &&
        ccb->secure_connections->ltk != NULL) {
        *security_level =
            open_cfw_cordio_smp_main_get_sc_security_level(ccb);
        return ccb->secure_connections->ltk->temporary_ltk;
    }
    if (ccb->scratch != NULL) {
        *security_level =
            (ccb->authentication & OPEN_CFW_SMP_AUTH_MITM) != 0U ?
            OPEN_CFW_DM_SECURITY_LEVEL_AUTHENTICATED :
            OPEN_CFW_DM_SECURITY_LEVEL_ENCRYPTED;
        return ccb->scratch->buffers.b3;
    }
    return NULL;
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_INIT_ONLY)
void open_cfw_cordio_smp_main_handler_init(uint8_t handler_id)
{
    uint8_t index;
    OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.handler_id = handler_id;
    open_cfw_cordio_smp_db_init();
    for (index = 0U; index < OPEN_CFW_SMP_CONNECTION_COUNT; index++) {
        struct open_cfw_smp_main_ccb *ccb =
            &OPEN_CFW_SMP_MAIN_CONTROL_BLOCK.connections[index];
        ccb->response_timer.handler_id = handler_id;
        ccb->response_timer.message.param = (uint16_t)(index + 1U);
        ccb->wait_timer.handler_id = handler_id;
        ccb->wait_timer.message.param = (uint16_t)(index + 1U);
    }
    open_cfw_retained_cordio_l2c_register(
        OPEN_CFW_SMP_CID, open_cfw_cordio_smp_main_l2c_data_callback,
        open_cfw_cordio_smp_main_l2c_control_callback);
    open_cfw_retained_cordio_dm_conn_register(
        1U, open_cfw_cordio_smp_main_dm_connection_callback);
}
#endif

#if OPEN_CFW_SMP_MAIN_ALL || defined(OPEN_CFW_SMP_MAIN_HANDLER_ONLY)
void open_cfw_cordio_smp_main_handler(
    uint32_t event, struct open_cfw_smp_main_header *message)
{
    struct open_cfw_smp_main_ccb *ccb;
    (void)event;
    if (message == NULL) {
        return;
    }
    if (message->event == OPEN_CFW_SMP_DATABASE_SERVICE_EVENT) {
        open_cfw_cordio_smp_db_service();
        return;
    }
    if (message->event == OPEN_CFW_SMP_MESSAGE_CMAC_COMPLETE) {
        struct open_cfw_smp_main_cmac_message *cmac =
            (struct open_cfw_smp_main_cmac_message *)message;
        if (cmac->plain_text != NULL) {
            open_cfw_retained_cordio_wsf_buffer_free(cmac->plain_text);
        }
    }
    ccb = open_cfw_cordio_smp_main_ccb_by_connection_id(
        (uint8_t)message->param);
    if (ccb == NULL || ccb->connection_id == 0U) {
        return;
    }
    if (message->event == OPEN_CFW_SMP_MESSAGE_AES_COMPLETE &&
        ccb->token != message->status) {
        uint8_t handler_id;
        void *queued;
        while ((queued = open_cfw_retained_cordio_wsf_msg_dequeue(
                    OPEN_CFW_SMP_MAIN_SECURITY_QUEUE, &handler_id)) != NULL) {
            open_cfw_retained_cordio_wsf_msg_free(queued);
        }
        return;
    }
    open_cfw_retained_cordio_smp_state_machine_execute(ccb, message);
}
#endif
