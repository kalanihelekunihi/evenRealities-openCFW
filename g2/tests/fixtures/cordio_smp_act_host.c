#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "cordio_smp_act_host.h"

struct open_cfw_smp_act_header {
    uint16_t param;
    uint8_t event;
    uint8_t status;
};
struct open_cfw_smp_act_timer {
    uint32_t next;
    struct open_cfw_smp_act_header message;
    uint32_t ticks;
    uint8_t handler_id, is_started, reserved[2];
};
struct open_cfw_smp_act_ltk {
    uint8_t key[16], random[8];
    uint16_t diversifier;
};
struct open_cfw_smp_act_irk {
    uint8_t key[16], address[6], address_type;
};
union open_cfw_smp_act_key_data {
    struct open_cfw_smp_act_ltk ltk;
    struct open_cfw_smp_act_irk irk;
    uint8_t csrk[16];
};
struct open_cfw_smp_act_key_indication {
    struct open_cfw_smp_act_header header;
    union open_cfw_smp_act_key_data key_data;
    uint8_t type, security_level, encryption_key_length;
};
union open_cfw_smp_act_scratch {
    struct { uint8_t b1[16], b2[16], b3[16], b4[16]; } buffers;
    struct open_cfw_smp_act_key_indication key_indication;
};
struct open_cfw_smp_act_sc_ltk { uint8_t mac[16], temporary_ltk[16]; };
struct open_cfw_smp_act_sc_ccb {
    uint8_t lesc_enabled, authentication_type, keypress_notify;
    uint8_t passkey_position, display, reserved[3];
    void *peer_public_key, *local_public_key;
    uint8_t *private_key;
    void *scratch;
    struct open_cfw_smp_act_sc_ltk *ltk;
};
struct open_cfw_smp_act_ccb {
    struct open_cfw_smp_act_timer response_timer, wait_timer;
    uint8_t pair_request[7], pair_response[7], reserved46[2];
    union open_cfw_smp_act_scratch *scratch;
    uint8_t *queued_packet;
    uint16_t handle;
    uint8_t initiator, security_request, flow_disabled, connection_id;
    uint8_t state, next_command, authentication, token, attempts;
    uint8_t last_sent_key, key_ready, reserved69[3];
    struct open_cfw_smp_act_sc_ccb *secure_connections;
};
typedef void (*open_cfw_smp_act_function)(struct open_cfw_smp_act_ccb *, void *);
typedef uint8_t open_cfw_smp_act_table_entry[3];
struct open_cfw_smp_act_interface {
    const open_cfw_smp_act_table_entry *const *state_table;
    const open_cfw_smp_act_function *action_table;
    const open_cfw_smp_act_table_entry *common_table;
};
struct open_cfw_smp_act_control_block {
    struct open_cfw_smp_act_ccb connections[3];
    const struct open_cfw_smp_act_interface *slave_interface, *master_interface;
    uint8_t handler_id, reserved237[3];
    void *process_pairing, *process_authentication;
    uint8_t lesc_supported, reserved249[3];
};
struct open_cfw_smp_act_config {
    uint32_t attempt_timeout;
    uint8_t io_capability, minimum_key_length, maximum_key_length;
    uint8_t maximum_attempts, authentication, reserved9[3];
    uint32_t maximum_attempt_timeout, attempt_decrement_timeout;
    uint16_t attempt_exponent;
};
struct open_cfw_smp_act_auth_response {
    struct open_cfw_smp_act_header header;
    uint8_t authentication_data[16], authentication_data_length;
};
struct open_cfw_smp_act_aes_message {
    struct open_cfw_smp_act_header header;
    uint8_t *ciphertext, *plaintext;
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

struct open_cfw_smp_act_control_block open_cfw_test_smp_act_control;
struct open_cfw_smp_act_config open_cfw_test_smp_act_config;

extern void open_cfw_cordio_smp_act_start_response_timer(struct open_cfw_smp_act_ccb *);
extern void open_cfw_cordio_smp_act_cleanup_core(struct open_cfw_smp_act_ccb *);
extern void open_cfw_cordio_smp_act_pairing_failed(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern void open_cfw_cordio_smp_act_security_request_timeout(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern uint8_t open_cfw_cordio_smp_act_process_pairing(struct open_cfw_smp_act_ccb *, uint8_t *, uint8_t *);
extern void open_cfw_cordio_smp_act_authentication_request(struct open_cfw_smp_act_ccb *, uint8_t, uint8_t);
extern void open_cfw_cordio_smp_act_confirm_calculate_one(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern void open_cfw_cordio_smp_act_send_confirm(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern void open_cfw_cordio_smp_act_verify_calculate_one(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern uint8_t open_cfw_cordio_smp_act_send_key(struct open_cfw_smp_act_ccb *, uint8_t);
extern uint8_t open_cfw_cordio_smp_act_receive_key(struct open_cfw_smp_act_ccb *, struct open_cfw_smp_act_key_indication *, uint8_t *, uint8_t);
extern void open_cfw_cordio_smp_act_max_attempts(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern void open_cfw_cordio_smp_act_check_attempts(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern void open_cfw_cordio_smp_act_pairing_complete(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);
extern void open_cfw_cordio_smp_act_execute(struct open_cfw_smp_act_ccb *, union open_cfw_smp_act_message *);

static uint8_t packet_storage[64], message_storage[64], irk[16], csrk[16], address[6];
static uint8_t security_level, role, allocate_ok, state_event, callback_event;
static uint8_t callback_status, callback_type, callback_auth, action_called;
static uint32_t start_sec_calls, start_ms_calls, stop_calls, buffer_free_calls;
static uint32_t send_packet_calls, callback_calls, state_calls, idle_calls;
static uint32_t message_send_calls, message_free_calls, generate_ltk_calls;
static uint32_t max_attempt_timeout;

static void reset_fixture(void)
{
    memset(&open_cfw_test_smp_act_control, 0, sizeof(open_cfw_test_smp_act_control));
    memset(&open_cfw_test_smp_act_config, 0, sizeof(open_cfw_test_smp_act_config));
    memset(packet_storage, 0, sizeof(packet_storage));
    memset(message_storage, 0, sizeof(message_storage));
    for (unsigned i = 0; i < 16; i++) { irk[i] = (uint8_t)(0x20 + i); csrk[i] = (uint8_t)(0x40 + i); }
    for (unsigned i = 0; i < 6; i++) address[i] = (uint8_t)(0xA0 + i);
    security_level = role = 0; allocate_ok = 1; state_event = 0;
    callback_event = callback_status = callback_type = callback_auth = 0;
    action_called = 0;
    start_sec_calls = start_ms_calls = stop_calls = buffer_free_calls = 0;
    send_packet_calls = callback_calls = state_calls = idle_calls = 0;
    message_send_calls = message_free_calls = generate_ltk_calls = 0;
    max_attempt_timeout = 1234;
    open_cfw_test_smp_act_config.minimum_key_length = 7;
    open_cfw_test_smp_act_control.handler_id = 9;
}

void open_cfw_retained_cordio_wsf_timer_start_sec(struct open_cfw_smp_act_timer *timer, uint32_t seconds)
{ start_sec_calls++; timer->ticks = seconds; timer->is_started = 1; }
void open_cfw_retained_cordio_wsf_timer_start_ms(struct open_cfw_smp_act_timer *timer, uint32_t ms)
{ start_ms_calls++; timer->ticks = ms; timer->is_started = 1; }
void open_cfw_retained_cordio_wsf_timer_stop(struct open_cfw_smp_act_timer *timer)
{ stop_calls++; timer->is_started = 0; }
void open_cfw_retained_cordio_wsf_buffer_free(void *buffer)
{ if (buffer) buffer_free_calls++; }
void open_cfw_retained_cordio_wsf_msg_free(void *message)
{ if (message) message_free_calls++; }
void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t length)
{ return allocate_ok && length <= sizeof(message_storage) ? message_storage : NULL; }
void open_cfw_retained_cordio_wsf_msg_send(uint8_t handler, void *message)
{ if (handler == 9 && message) message_send_calls++; }
void open_cfw_retained_cordio_dm_conn_set_idle(uint8_t id, uint16_t mask, uint8_t idle)
{ if (id == 2 && mask == 1 && idle == 0) idle_calls++; }
uint8_t open_cfw_retained_cordio_dm_conn_security_level(uint8_t id)
{ (void)id; return security_level; }
uint8_t open_cfw_retained_cordio_dm_conn_role(uint8_t id)
{ (void)id; return role; }
void open_cfw_cordio_dm_sec_smp_callback_execute(void *value)
{
    const struct open_cfw_smp_act_header *header = value;
    callback_calls++; callback_event = header->event; callback_status = header->status;
    if (header->event == 47) callback_type = ((struct open_cfw_smp_act_key_indication *)value)->type;
    if (header->event == 42) callback_auth = ((const uint8_t *)value)[4];
}
void open_cfw_retained_cordio_sec_rand(uint8_t *buffer, uint16_t length)
{ for (uint16_t i = 0; i < length; i++) buffer[i] = (uint8_t)(0x70 + i); }
void open_cfw_retained_cordio_calc128_copy(uint8_t destination[16], const uint8_t source[16])
{ memcpy(destination, source, 16); }
const uint8_t *open_cfw_cordio_dm_sec_get_local_irk(void) { return irk; }
const uint8_t *open_cfw_cordio_dm_sec_get_local_csrk(void) { return csrk; }
const uint8_t *open_cfw_retained_cordio_hci_get_bd_address(void) { return address; }
uint32_t open_cfw_cordio_smp_db_max_attempt_reached(uint8_t id)
{ (void)id; return max_attempt_timeout; }
uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length)
{ return allocate_ok && length <= sizeof(packet_storage) ? packet_storage : NULL; }
void open_cfw_cordio_smp_main_send_packet(struct open_cfw_smp_act_ccb *ccb, uint8_t *packet)
{ (void)ccb; if (packet == packet_storage) send_packet_calls++; }
void open_cfw_cordio_smp_main_calculate_c1_part1(struct open_cfw_smp_act_ccb *ccb, const uint8_t *key, const uint8_t *random)
{ (void)ccb; if (key && random) state_calls++; }
void open_cfw_cordio_smp_main_calculate_c1_part2(struct open_cfw_smp_act_ccb *ccb, const uint8_t *key, const uint8_t *part1)
{ (void)ccb; if (key && part1) state_calls++; }
void open_cfw_cordio_smp_main_generate_ltk(struct open_cfw_smp_act_ccb *ccb)
{
    generate_ltk_calls++;
    for (unsigned i = 0; i < 16; i++) ccb->scratch->key_indication.key_data.ltk.key[i] = (uint8_t)(0x60 + i);
}
uint8_t open_cfw_cordio_smp_main_get_sc_security_level(struct open_cfw_smp_act_ccb *ccb)
{ (void)ccb; return 3; }
void open_cfw_iar_memcpy_void(void *destination, const void *source, uint32_t size)
{ memcpy(destination, source, size); }
void *open_cfw_runtime_memory_zero(void *destination, uint32_t size)
{ return memset(destination, 0, size); }

static void test_action(struct open_cfw_smp_act_ccb *ccb, void *message)
{ (void)ccb; (void)message; action_called++; }

int open_cfw_test_smp_act_timer_cleanup_contract(void)
{
    struct open_cfw_smp_act_ccb ccb;
    union open_cfw_smp_act_scratch scratch;
    reset_fixture(); memset(&ccb, 0, sizeof(ccb));
    ccb.scratch = &scratch; ccb.initiator = 1; ccb.security_request = 1;
    ccb.last_sent_key = 9; ccb.response_timer.is_started = 1; ccb.wait_timer.is_started = 1;
    open_cfw_cordio_smp_act_start_response_timer(&ccb);
    if (start_sec_calls != 1 || ccb.response_timer.ticks != 30 || ccb.response_timer.message.event != 15 || ccb.response_timer.message.status != 0xE1) return 1;
    open_cfw_cordio_smp_act_cleanup_core(&ccb);
    return !(ccb.scratch == NULL && buffer_free_calls == 1 && stop_calls == 2 && ccb.security_request == 0 && ccb.next_command == 11 && ccb.last_sent_key == 0);
}

int open_cfw_test_smp_act_failure_contract(void)
{
    struct open_cfw_smp_act_ccb ccb; union open_cfw_smp_act_message message;
    reset_fixture(); memset(&ccb, 0, sizeof(ccb)); memset(&message, 0, sizeof(message)); ccb.connection_id = 2;
    open_cfw_cordio_smp_act_pairing_failed(&ccb, &message);
    if (idle_calls != 1 || callback_event != 43) return 1;
    security_level = 1; state_event = 0;
    static const open_cfw_smp_act_table_entry state0[] = {{31, 4, 0}, {0,0,0}};
    static const open_cfw_smp_act_table_entry common[] = {{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}};
    static const open_cfw_smp_act_table_entry *states[] = {state0};
    static const open_cfw_smp_act_function actions[] = {test_action};
    static const struct open_cfw_smp_act_interface interface = {states, actions, common};
    open_cfw_test_smp_act_control.master_interface = &interface; ccb.state = 0;
    open_cfw_cordio_smp_act_security_request_timeout(&ccb, &message);
    return !(message.header.event == 31 && ccb.state == 4 && action_called == 1);
}

int open_cfw_test_smp_act_pairing_auth_contract(void)
{
    struct open_cfw_smp_act_ccb ccb; uint8_t oob, display;
    reset_fixture(); memset(&ccb, 0, sizeof(ccb)); ccb.connection_id = 2; ccb.initiator = 1;
    ccb.pair_request[1] = 0; ccb.pair_response[1] = 2;
    ccb.pair_request[3] = ccb.pair_response[3] = 4;
    ccb.pair_request[4] = ccb.pair_response[4] = 16;
    if (!open_cfw_cordio_smp_act_process_pairing(&ccb, &oob, &display) || oob || !display || !(ccb.authentication & 4)) return 1;
    open_cfw_cordio_smp_act_authentication_request(&ccb, 0, display);
    if (callback_event != 46) return 2;
    ccb.authentication = 0; action_called = 0;
    static const open_cfw_smp_act_table_entry state0[] = {{4, 1, 0}, {0,0,0}};
    static const open_cfw_smp_act_table_entry common[] = {{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}};
    static const open_cfw_smp_act_table_entry *states[] = {state0};
    static const open_cfw_smp_act_function actions[] = {test_action};
    static const struct open_cfw_smp_act_interface interface = {states, actions, common};
    open_cfw_test_smp_act_control.master_interface = &interface; ccb.state = 0;
    open_cfw_cordio_smp_act_authentication_request(&ccb, 0, 0);
    return !(action_called == 1 && ccb.state == 1);
}

int open_cfw_test_smp_act_confirm_contract(void)
{
    struct open_cfw_smp_act_ccb ccb; union open_cfw_smp_act_scratch scratch;
    union open_cfw_smp_act_message message; uint8_t ciphertext[16], received[32];
    reset_fixture(); memset(&ccb, 0, sizeof(ccb)); memset(&scratch, 0xFF, sizeof(scratch)); memset(&message, 0, sizeof(message)); memset(ciphertext, 0x5A, sizeof(ciphertext)); memset(received, 0, sizeof(received));
    ccb.scratch = &scratch; ccb.initiator = 1;
    message.authentication.authentication_data_length = 4;
    message.authentication.authentication_data[0] = 1;
    open_cfw_cordio_smp_act_confirm_calculate_one(&ccb, &message);
    if (scratch.buffers.b1[0] != 1 || scratch.buffers.b1[4] != 0 || scratch.buffers.b4[0] != 0x70 || state_calls != 1) return 1;
    message.aes.ciphertext = ciphertext;
    open_cfw_cordio_smp_act_send_confirm(&ccb, &message);
    if (ccb.next_command != 3 || packet_storage[8] != 3 || packet_storage[9] != 0x5A || send_packet_calls != 1) return 2;
    for (unsigned i=0;i<16;i++) received[9+i]=(uint8_t)i;
    message.data.packet = received;
    open_cfw_cordio_smp_act_verify_calculate_one(&ccb, &message);
    return !(scratch.buffers.b2[15] == 15 && state_calls == 2);
}

int open_cfw_test_smp_act_key_contract(void)
{
    struct open_cfw_smp_act_ccb ccb; union open_cfw_smp_act_scratch scratch;
    struct open_cfw_smp_act_key_indication indication; uint8_t packet[32];
    reset_fixture(); memset(&ccb,0,sizeof(ccb)); memset(&scratch,0,sizeof(scratch)); memset(&indication,0,sizeof(indication)); memset(packet,0,sizeof(packet)); ccb.scratch=&scratch; ccb.connection_id=2;
    if (open_cfw_cordio_smp_act_send_key(&ccb, 1) != 0 || generate_ltk_calls != 1 || packet_storage[8] != 6 || send_packet_calls != 1 || message_send_calls != 1) return 1;
    ccb.next_command = 6; ccb.authentication = 4; packet[8] = 6; for(unsigned i=0;i<16;i++)packet[9+i]=(uint8_t)i;
    if (open_cfw_cordio_smp_act_receive_key(&ccb,&indication,packet,1) != 0 || ccb.next_command != 7 || indication.key_data.ltk.key[15] != 15) return 2;
    packet[8]=7; packet[9]=0x34; packet[10]=0x12;
    if (open_cfw_cordio_smp_act_receive_key(&ccb,&indication,packet,1) != 1 || indication.key_data.ltk.diversifier != 0x1234 || indication.type != 2 || indication.security_level != 2 || callback_event != 47) return 3;
    return 0;
}

int open_cfw_test_smp_act_attempts_execute_contract(void)
{
    struct open_cfw_smp_act_ccb ccb; union open_cfw_smp_act_message message;
    reset_fixture(); memset(&ccb,0,sizeof(ccb)); memset(&message,0,sizeof(message)); ccb.connection_id=2; message.header.status=9;
    open_cfw_cordio_smp_act_max_attempts(&ccb,&message);
    if (start_ms_calls!=1 || ccb.wait_timer.ticks!=1234 || ccb.wait_timer.message.event!=16) return 1;
    ccb.attempts=1; open_cfw_cordio_smp_act_check_attempts(&ccb,&message);
    if (ccb.attempts || callback_event!=43 || callback_status!=9) return 2;
    ccb.authentication=0x0D; open_cfw_cordio_smp_act_pairing_complete(&ccb,&message);
    return !(callback_event==42 && callback_auth==0x0D && idle_calls>=2);
}
