#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "cordio_smp_main_host.h"

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
    struct { uint8_t b1[16], b2[16], b3[16], b4[16]; } buffers;
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
    uint8_t lesc_enabled, authentication_type, keypress_notify;
    uint8_t passkey_position, display, reserved[3];
    void *peer_public_key, *local_public_key;
    uint8_t *private_key;
    void *scratch;
    struct open_cfw_smp_main_sc_ltk *ltk;
};

struct open_cfw_smp_main_ccb {
    struct open_cfw_smp_main_timer response_timer, wait_timer;
    uint8_t pair_request[7], pair_response[7], reserved46[2];
    union open_cfw_smp_main_scratch *scratch;
    uint8_t *queued_packet;
    uint16_t handle;
    uint8_t initiator, security_request, flow_disabled, connection_id;
    uint8_t state, next_command, authentication, token, attempts;
    uint8_t last_sent_key, key_ready, reserved69[3];
    struct open_cfw_smp_main_sc_ccb *secure_connections;
};

struct open_cfw_smp_main_control_block {
    struct open_cfw_smp_main_ccb connections[3];
    const void *slave_interface, *master_interface;
    uint8_t handler_id, reserved237[3];
    void *process_pairing, *process_authentication;
    uint8_t lesc_supported, reserved249[3];
};

struct open_cfw_smp_main_cmac_message {
    struct open_cfw_smp_main_header header;
    uint8_t *ciphertext;
    uint8_t *plain_text;
};

struct open_cfw_smp_main_control_block open_cfw_test_smp_main_control;
uint8_t open_cfw_test_smp_main_security_queue;

static uint8_t handle_connection;
static uint8_t roles[4];
static uint8_t local_address[4][6], local_rpa[4][6];
static uint8_t peer_address[4][6], peer_rpa[4][6];
static uint8_t local_type[4], peer_type[4];
static uint8_t failure_count[4];
static uint32_t disabled_time[4];
static uint32_t db_init_calls, db_service_calls, db_set_calls;
static uint32_t timer_calls, register_l2c_calls, register_dm_calls;
static uint32_t state_calls, free_calls, buffer_free_calls;
static uint32_t data_calls, send_calls, alloc_calls, dm_callback_calls;
static uint16_t last_data_cid, last_data_handle, last_data_length;
static uint8_t *last_data_packet;
static uint8_t last_state_event, last_state_status;
static struct open_cfw_smp_main_ccb *last_state_ccb;
static uint8_t aes_return, aes_input[16], aes_key[16];
static uint8_t aes_handler, aes_event;
static uint16_t aes_param;
static uint8_t random_seed;
static void *dequeue_items[4];
static uint8_t dequeue_count, dequeue_index;
static void (*registered_data)(uint16_t, uint16_t, uint8_t *);
static void (*registered_control)(struct open_cfw_smp_main_header *);
static void (*registered_dm)(void *);
static uint8_t allocation[64];

extern struct open_cfw_smp_main_ccb *
open_cfw_cordio_smp_main_ccb_by_handle(uint16_t);
extern struct open_cfw_smp_main_ccb *
open_cfw_cordio_smp_main_ccb_by_connection_id(uint8_t);
extern void open_cfw_cordio_smp_main_handler_init(uint8_t);
extern void open_cfw_cordio_smp_main_dm_connection_callback(void *);
extern void open_cfw_cordio_smp_main_l2c_data_callback(
    uint16_t, uint16_t, uint8_t *);
extern void open_cfw_cordio_smp_main_l2c_control_callback(
    struct open_cfw_smp_main_header *);
extern void open_cfw_cordio_smp_main_send_packet(
    struct open_cfw_smp_main_ccb *, uint8_t *);
extern void open_cfw_cordio_smp_main_calculate_c1_part1(
    struct open_cfw_smp_main_ccb *, const uint8_t *, const uint8_t *);
extern void open_cfw_cordio_smp_main_calculate_c1_part2(
    struct open_cfw_smp_main_ccb *, const uint8_t *, const uint8_t *);
extern void open_cfw_cordio_smp_main_calculate_s1(
    struct open_cfw_smp_main_ccb *, const uint8_t *, const uint8_t *,
    const uint8_t *);
extern void open_cfw_cordio_smp_main_generate_ltk(
    struct open_cfw_smp_main_ccb *);
extern uint8_t open_cfw_cordio_smp_main_get_sc_security_level(
    struct open_cfw_smp_main_ccb *);
extern uint8_t open_cfw_cordio_smp_main_dm_lesc_enabled(uint8_t);
extern uint8_t *open_cfw_cordio_smp_main_dm_get_stk(uint8_t, uint8_t *);
extern void *open_cfw_cordio_smp_main_message_allocate(uint16_t);
extern void open_cfw_cordio_smp_main_dm_message_send(void *);
extern void open_cfw_cordio_smp_main_dm_encrypt_indication(
    struct open_cfw_smp_main_header *);
extern void open_cfw_cordio_smp_main_handler(
    uint32_t, struct open_cfw_smp_main_header *);

static void reset_fixture(void)
{
    memset(&open_cfw_test_smp_main_control, 0,
        sizeof(open_cfw_test_smp_main_control));
    memset(roles, 0, sizeof(roles));
    memset(local_address, 0, sizeof(local_address));
    memset(local_rpa, 0, sizeof(local_rpa));
    memset(peer_address, 0, sizeof(peer_address));
    memset(peer_rpa, 0, sizeof(peer_rpa));
    memset(local_type, 0, sizeof(local_type));
    memset(peer_type, 0, sizeof(peer_type));
    memset(failure_count, 0, sizeof(failure_count));
    memset(disabled_time, 0, sizeof(disabled_time));
    db_init_calls = db_service_calls = db_set_calls = timer_calls = 0U;
    register_l2c_calls = register_dm_calls = state_calls = free_calls = 0U;
    buffer_free_calls = data_calls = send_calls = alloc_calls = 0U;
    dm_callback_calls = 0U;
    last_data_cid = last_data_handle = last_data_length = 0U;
    last_data_packet = NULL;
    last_state_event = last_state_status = 0U;
    last_state_ccb = NULL;
    aes_return = 7U;
    memset(aes_input, 0, sizeof(aes_input));
    memset(aes_key, 0, sizeof(aes_key));
    aes_handler = aes_event = 0U;
    aes_param = 0U;
    random_seed = 0x40U;
    memset(dequeue_items, 0, sizeof(dequeue_items));
    dequeue_count = dequeue_index = 0U;
    registered_data = NULL;
    registered_control = NULL;
    registered_dm = NULL;
    handle_connection = 0U;
}

uint8_t open_cfw_retained_cordio_dm_conn_id_by_handle(uint16_t handle)
{
    (void)handle;
    return handle_connection;
}
uint8_t open_cfw_retained_cordio_dm_conn_role(uint8_t id) { return roles[id]; }
uint8_t *open_cfw_retained_cordio_dm_conn_local_address(uint8_t id)
{ return local_address[id]; }
uint8_t *open_cfw_retained_cordio_dm_conn_local_rpa(uint8_t id)
{ return local_rpa[id]; }
uint8_t open_cfw_retained_cordio_dm_conn_local_address_type(uint8_t id)
{ return local_type[id]; }
uint8_t *open_cfw_retained_cordio_dm_conn_peer_address(uint8_t id)
{ return peer_address[id]; }
uint8_t *open_cfw_retained_cordio_dm_conn_peer_rpa(uint8_t id)
{ return peer_rpa[id]; }
uint8_t open_cfw_retained_cordio_dm_conn_peer_address_type(uint8_t id)
{ return peer_type[id]; }

void open_cfw_retained_cordio_dm_conn_register(
    uint8_t client, void (*callback)(void *))
{ register_dm_calls++; if (client == 1U) registered_dm = callback; }
void open_cfw_retained_cordio_l2c_register(
    uint16_t cid, void (*data_cb)(uint16_t, uint16_t, uint8_t *),
    void (*control_cb)(struct open_cfw_smp_main_header *))
{
    register_l2c_calls++;
    if (cid == 6U) { registered_data = data_cb; registered_control = control_cb; }
}
void open_cfw_retained_cordio_l2c_data_request(
    uint16_t cid, uint16_t handle, uint16_t length, uint8_t *packet)
{
    data_calls++; last_data_cid = cid; last_data_handle = handle;
    last_data_length = length; last_data_packet = packet;
}
void open_cfw_retained_cordio_wsf_timer_start_ms(
    struct open_cfw_smp_main_timer *timer, uint32_t milliseconds)
{ timer_calls++; timer->ticks = milliseconds; timer->is_started = 1U; }
void *open_cfw_retained_cordio_wsf_msg_data_alloc(
    uint16_t length, uint16_t tailroom)
{ alloc_calls++; return length <= sizeof(allocation) && tailroom == 0U ? allocation : NULL; }
void open_cfw_retained_cordio_wsf_msg_send(uint8_t handler, void *message)
{ send_calls++; aes_handler = handler; last_data_packet = message; }
void *open_cfw_retained_cordio_wsf_msg_dequeue(void *queue, uint8_t *handler)
{
    if (queue != &open_cfw_test_smp_main_security_queue ||
        dequeue_index >= dequeue_count) return NULL;
    *handler = dequeue_index;
    return dequeue_items[dequeue_index++];
}
void open_cfw_retained_cordio_wsf_msg_free(void *message)
{ (void)message; free_calls++; }
void open_cfw_retained_cordio_wsf_buffer_free(void *buffer)
{ (void)buffer; buffer_free_calls++; }
uint8_t open_cfw_retained_cordio_sec_aes(
    const uint8_t key[16], const uint8_t data[16], uint8_t handler,
    uint16_t param, uint8_t event)
{
    memcpy(aes_key, key, 16U); memcpy(aes_input, data, 16U);
    aes_handler = handler; aes_param = param; aes_event = event;
    return aes_return;
}
void open_cfw_retained_cordio_sec_rand(uint8_t *buffer, uint16_t length)
{ uint16_t i; for (i = 0; i < length; i++) buffer[i] = (uint8_t)(random_seed + i); }
void open_cfw_cordio_dm_sec_smp_callback_execute(void *message)
{ dm_callback_calls++; last_data_packet = message; }
void open_cfw_retained_cordio_smp_state_machine_execute(
    struct open_cfw_smp_main_ccb *ccb, void *message)
{
    struct open_cfw_smp_main_header *header = message;
    state_calls++; last_state_ccb = ccb;
    last_state_event = header->event; last_state_status = header->status;
}
uint32_t open_cfw_cordio_smp_db_get_pairing_disabled_time(uint8_t id)
{ return disabled_time[id]; }
uint8_t open_cfw_cordio_smp_db_get_failure_count(uint8_t id)
{ return failure_count[id]; }
void open_cfw_cordio_smp_db_set_failure_count(uint8_t id, uint8_t count)
{ db_set_calls++; failure_count[id] = count; }
void open_cfw_cordio_smp_db_init(void) { db_init_calls++; }
void open_cfw_cordio_smp_db_service(void) { db_service_calls++; }
void open_cfw_iar_memcpy_void(void *dst, const void *src, uint32_t size)
{ memcpy(dst, src, size); }
void *open_cfw_runtime_memory_zero(void *dst, uint32_t size)
{ return memset(dst, 0, size); }

int open_cfw_test_smp_main_lookup_and_init(void)
{
    uint8_t i;
    reset_fixture();
    handle_connection = 2U;
    open_cfw_cordio_smp_main_handler_init(0x5AU);
    if (db_init_calls != 1U || register_l2c_calls != 1U ||
        register_dm_calls != 1U || registered_data == NULL ||
        registered_control == NULL || registered_dm == NULL ||
        open_cfw_test_smp_main_control.handler_id != 0x5AU) return 1;
    for (i = 0U; i < 3U; i++) {
        struct open_cfw_smp_main_ccb *ccb =
            &open_cfw_test_smp_main_control.connections[i];
        if (ccb->response_timer.handler_id != 0x5AU ||
            ccb->response_timer.message.param != i + 1U ||
            ccb->wait_timer.message.param != i + 1U) return 2;
    }
    if (open_cfw_cordio_smp_main_ccb_by_handle(9U) !=
        &open_cfw_test_smp_main_control.connections[1] ||
        open_cfw_cordio_smp_main_ccb_by_connection_id(0U) != NULL ||
        open_cfw_cordio_smp_main_ccb_by_connection_id(4U) != NULL) return 3;
    return 0;
}

int open_cfw_test_smp_main_connection_lifecycle(void)
{
    uint8_t event[16] = {0};
    struct open_cfw_smp_main_header *header = (void *)event;
    struct open_cfw_smp_main_ccb *ccb;
    reset_fixture();
    open_cfw_test_smp_main_control.lesc_supported = 1U;
    roles[1] = 0U; failure_count[1] = 3U; disabled_time[1] = 2500U;
    header->param = 1U; header->event = 39U;
    *(uint16_t *)(void *)(event + 6U) = 0x1234U;
    open_cfw_cordio_smp_main_dm_connection_callback(event);
    ccb = &open_cfw_test_smp_main_control.connections[0];
    if (ccb->handle != 0x1234U || ccb->connection_id != 1U ||
        ccb->initiator != 1U || ccb->next_command != 11U ||
        ccb->attempts != 3U || ccb->state != 36U || timer_calls != 1U ||
        ccb->wait_timer.message.event != 16U) return 1;
    ccb->queued_packet = event + 12U; ccb->attempts = 5U;
    header->event = 40U; event[8] = 0x13U;
    open_cfw_cordio_smp_main_dm_connection_callback(event);
    if (db_set_calls != 1U || failure_count[1] != 5U || state_calls != 1U ||
        last_state_event != 10U || last_state_status != 0x33U ||
        ccb->connection_id != 0U || ccb->queued_packet != NULL ||
        free_calls != 1U) return 2;
    return 0;
}

int open_cfw_test_smp_main_l2cap_and_queueing(void)
{
    uint8_t first[32] = {0}, second[32] = {0};
    struct open_cfw_smp_main_header control = {1U, 0U, 0U};
    struct open_cfw_smp_main_ccb *ccb;
    reset_fixture(); handle_connection = 1U;
    ccb = &open_cfw_test_smp_main_control.connections[0];
    ccb->connection_id = 1U; ccb->handle = 0x2222U; ccb->next_command = 1U;
    first[8] = 1U;
    open_cfw_cordio_smp_main_l2c_data_callback(0x2222U, 7U, first);
    if (state_calls != 1U || last_state_event != 6U || last_state_ccb != ccb)
        return 1;
    open_cfw_cordio_smp_main_l2c_data_callback(0x2222U, 6U, first);
    if (state_calls != 1U) return 2;
    ccb->flow_disabled = 1U; ccb->queued_packet = first;
    second[8] = 5U;
    open_cfw_cordio_smp_main_send_packet(ccb, second);
    if (free_calls != 1U || ccb->queued_packet != second) return 3;
    ccb->state = 2U;
    open_cfw_cordio_smp_main_l2c_control_callback(&control);
    if (ccb->queued_packet != NULL || data_calls != 1U ||
        last_data_cid != 6U || last_data_handle != 0x2222U ||
        last_data_length != 2U || last_data_packet != second ||
        state_calls != 2U || last_state_event != 12U) return 4;
    return 0;
}

int open_cfw_test_smp_main_legacy_crypto(void)
{
    uint8_t key[16], random[16], expected[16], i;
    struct open_cfw_smp_main_ccb *ccb;
    reset_fixture();
    ccb = &open_cfw_test_smp_main_control.connections[0];
    ccb->connection_id = 1U; ccb->initiator = 1U;
    open_cfw_test_smp_main_control.handler_id = 9U;
    local_type[1] = 0U; peer_type[1] = 1U;
    memcpy(local_address[1], "LOCAL!", 6U);
    memcpy(peer_address[1], "PEER!!", 6U);
    for (i = 0U; i < 16U; i++) { key[i] = (uint8_t)(0xA0U + i); random[i] = i; }
    for (i = 0U; i < 7U; i++) { ccb->pair_request[i] = i + 1U; ccb->pair_response[i] = i + 8U; }
    expected[0] = random[0]; expected[1] = (uint8_t)(1U ^ random[1]);
    for (i = 0U; i < 7U; i++) { expected[2U+i] = ccb->pair_request[i] ^ random[2U+i]; expected[9U+i] = ccb->pair_response[i] ^ random[9U+i]; }
    open_cfw_cordio_smp_main_calculate_c1_part1(ccb, key, random);
    if (memcmp(aes_input, expected, 16U) != 0 || memcmp(aes_key, key, 16U) != 0 ||
        aes_handler != 9U || aes_param != 1U || aes_event != 11U || ccb->token != 7U) return 1;
    open_cfw_cordio_smp_main_calculate_c1_part2(ccb, key, random);
    for (i = 0U; i < 6U; i++) {
        if (aes_input[i] != (uint8_t)(peer_address[1][i] ^ random[i]) ||
            aes_input[6U+i] != (uint8_t)(local_address[1][i] ^ random[6U+i])) return 2;
    }
    open_cfw_cordio_smp_main_calculate_s1(ccb, key, random + 0U, random + 0U);
    if (memcmp(aes_input, random, 8U) != 0 || memcmp(aes_input + 8U, random, 8U) != 0) return 3;
    aes_return = 0xFFU; state_calls = 0U;
    open_cfw_cordio_smp_main_calculate_s1(ccb, key, random, random);
    if (state_calls != 1U || last_state_event != 3U || last_state_status != 8U) return 4;
    return 0;
}

int open_cfw_test_smp_main_keys(void)
{
    union open_cfw_smp_main_scratch scratch;
    struct open_cfw_smp_main_sc_ltk ltk;
    struct open_cfw_smp_main_sc_ccb sc;
    struct open_cfw_smp_main_ccb *ccb;
    uint8_t level = 0U, i, *key;
    reset_fixture(); memset(&scratch, 0, sizeof(scratch));
    memset(&ltk, 0, sizeof(ltk)); memset(&sc, 0, sizeof(sc));
    ccb = &open_cfw_test_smp_main_control.connections[0];
    ccb->connection_id = 1U; ccb->scratch = &scratch;
    ccb->authentication = 4U; scratch.key_indication.encryption_key_length = 12U;
    for (i = 0U; i < 16U; i++) scratch.buffers.b4[i] = (uint8_t)(0x20U + i);
    open_cfw_cordio_smp_main_generate_ltk(ccb);
    if (dm_callback_calls != 1U || scratch.key_indication.type != 1U ||
        scratch.key_indication.security_level != 2U ||
        scratch.key_indication.header.event != 47U ||
        scratch.key_indication.diversifier != 0x2120U ||
        memcmp(scratch.key_indication.random, scratch.buffers.b4 + 2U, 8U) != 0)
        return 1;
    for (i = 0U; i < 12U; i++) if (scratch.key_indication.key[i] != 0x40U + i) return 2;
    for (i = 12U; i < 16U; i++) if (scratch.key_indication.key[i] != 0U) return 3;
    ccb->key_ready = 1U; ccb->pair_request[4] = ccb->pair_response[4] = 16U;
    sc.lesc_enabled = 1U; sc.ltk = &ltk; ccb->secure_connections = &sc;
    open_cfw_test_smp_main_control.lesc_supported = 1U;
    key = open_cfw_cordio_smp_main_dm_get_stk(1U, &level);
    if (key != ltk.temporary_ltk || level != 3U ||
        open_cfw_cordio_smp_main_dm_lesc_enabled(1U) != 1U ||
        open_cfw_cordio_smp_main_get_sc_security_level(ccb) != 3U) return 4;
    ccb->key_ready = 0U;
    return open_cfw_cordio_smp_main_dm_get_stk(1U, &level) == NULL ? 0 : 5;
}

int open_cfw_test_smp_main_handler(void)
{
    struct open_cfw_smp_main_header header = {1U, 32U, 0U};
    struct open_cfw_smp_main_cmac_message cmac;
    struct open_cfw_smp_main_ccb *ccb;
    uint8_t dummy[2];
    reset_fixture(); ccb = &open_cfw_test_smp_main_control.connections[0];
    ccb->connection_id = 1U; ccb->token = 9U;
    if (open_cfw_cordio_smp_main_message_allocate(16U) != allocation || alloc_calls != 1U) return 1;
    open_cfw_test_smp_main_control.handler_id = 0x44U;
    open_cfw_cordio_smp_main_dm_message_send(dummy);
    if (send_calls != 1U || aes_handler != 0x44U || last_data_packet != dummy) return 2;
    open_cfw_cordio_smp_main_handler(0U, &header);
    if (db_service_calls != 1U) return 3;
    memset(&cmac, 0, sizeof(cmac)); cmac.header.param = 1U;
    cmac.header.event = 28U; cmac.plain_text = dummy;
    open_cfw_cordio_smp_main_handler(0U, &cmac.header);
    if (buffer_free_calls != 1U || state_calls != 1U) return 4;
    dequeue_items[0] = dummy; dequeue_items[1] = dummy + 1U; dequeue_count = 2U;
    header.event = 11U; header.status = 8U;
    open_cfw_cordio_smp_main_handler(0U, &header);
    if (free_calls != 2U || dequeue_index != 2U || state_calls != 1U) return 5;
    header.status = 9U;
    open_cfw_cordio_smp_main_dm_encrypt_indication(&header);
    if (header.event != 9U || state_calls != 2U || last_state_event != 9U) return 6;
    return 0;
}
