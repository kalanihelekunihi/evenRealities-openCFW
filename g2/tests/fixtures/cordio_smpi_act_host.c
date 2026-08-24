#include <assert.h>
#include <stdint.h>
#include <string.h>

static uint8_t host_control_bytes[512];
static uint8_t host_config_bytes[64];
#define OPEN_CFW_SMPI_CONTROL_BLOCK \
    (*(struct open_cfw_smpi_control_block *)(void *)host_control_bytes)
#define OPEN_CFW_SMPI_CONFIG \
    (*(struct open_cfw_smpi_config *)(void *)host_config_bytes)
#include "../../components/apollo_main/core_overlay/cordio_smpi_act.c"

static union open_cfw_smpi_scratch host_scratch;
static uint8_t host_packet[64];
static uint8_t host_sent[64];
static uint16_t host_alloc_length;
static uint8_t host_exec_event, host_exec_status, host_callback_event;
static uint8_t host_pairing_result = 1U, host_auth_calls;
static uint8_t host_receive_done, host_send_done, host_failed;
static uint8_t host_encrypt_level, host_encrypt_key[16];

void *open_cfw_retained_cordio_wsf_buffer_alloc(uint16_t size)
{ assert(size == 64U); memset(&host_scratch, 0, sizeof(host_scratch)); return &host_scratch; }
void open_cfw_retained_cordio_dm_conn_set_idle(uint8_t id, uint16_t mask, uint8_t idle)
{ assert(id == 2U && mask == 1U && idle == 1U); }
void open_cfw_cordio_dm_sec_smp_callback_execute(void *message)
{ host_callback_event = ((struct open_cfw_smpi_header *)message)->event; }
void open_cfw_cordio_dm_sec_master_smp_encrypt_request(
    uint8_t id, uint8_t level, const uint8_t key[16])
{ assert(id == 2U); host_encrypt_level = level; memcpy(host_encrypt_key, key, 16U); }
uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t length)
{ host_alloc_length = length; memset(host_packet, 0, sizeof(host_packet)); return host_packet; }
void open_cfw_cordio_smp_main_send_packet(struct open_cfw_smpi_ccb *ccb, uint8_t *packet)
{ (void)ccb; memcpy(host_sent, packet, host_alloc_length); }
void open_cfw_cordio_smp_main_calculate_s1(struct open_cfw_smpi_ccb *ccb,
    const uint8_t key[16], const uint8_t r1[16], const uint8_t r2[16])
{ (void)ccb; assert(key == host_scratch.buffers.b1); assert(r1 == host_scratch.buffers.b2); assert(r2 == host_scratch.buffers.b4); host_exec_event = 0xA1U; }
void open_cfw_cordio_smp_act_start_response_timer(struct open_cfw_smpi_ccb *ccb)
{ ccb->response_timer.is_started = 1U; }
void open_cfw_cordio_smp_act_send_pairing_failed(struct open_cfw_smpi_ccb *ccb, uint8_t reason)
{ (void)ccb; host_failed = reason; }
uint8_t open_cfw_cordio_smp_act_receive_key(struct open_cfw_smpi_ccb *ccb,
    struct open_cfw_smpi_key_indication *ind, uint8_t *packet, uint8_t distribution)
{ (void)ccb; (void)ind; (void)packet; assert(distribution == 3U); return host_receive_done; }
uint8_t open_cfw_cordio_smp_act_send_key(struct open_cfw_smpi_ccb *ccb, uint8_t distribution)
{ (void)ccb; assert(distribution == 5U); return host_send_done; }
void open_cfw_cordio_smp_act_execute(struct open_cfw_smpi_ccb *ccb,
    union open_cfw_smpi_message *message)
{ (void)ccb; host_exec_event = message->header.event; host_exec_status = message->header.status; }
void open_cfw_cordio_smp_db_pairing_failed(uint8_t id)
{ assert(id == 2U); host_failed++; }
void open_cfw_iar_memcpy_void(void *d, const void *s, uint32_t n) { memcpy(d, s, n); }
void *open_cfw_runtime_memory_zero(void *d, uint32_t n) { return memset(d, 0, n); }
int open_cfw_retained_iar_memcmp(const void *a, const void *b, uint32_t n) { return memcmp(a, b, n); }

static uint8_t pair(struct open_cfw_smpi_ccb *ccb, uint8_t *oob, uint8_t *display)
{ (void)ccb; *oob = 1U; *display = 1U; return host_pairing_result; }
static void auth(struct open_cfw_smpi_ccb *ccb, uint8_t oob, uint8_t display)
{ (void)ccb; assert(oob == 1U && display == 1U); host_auth_calls++; }

static void reset(struct open_cfw_smpi_ccb *ccb, union open_cfw_smpi_message *msg)
{
    memset(ccb, 0, sizeof(*ccb)); memset(msg, 0, sizeof(*msg));
    memset(host_sent, 0, sizeof(host_sent)); host_exec_event = host_exec_status = 0U;
    host_callback_event = host_auth_calls = host_failed = 0U;
    ccb->connection_id = 2U; ccb->scratch = &host_scratch;
    OPEN_CFW_SMPI_CONTROL_BLOCK.process_pairing = pair;
    OPEN_CFW_SMPI_CONTROL_BLOCK.process_authentication = auth;
    OPEN_CFW_SMPI_CONFIG.io_capability = 4U;
    OPEN_CFW_SMPI_CONFIG.maximum_key_length = 16U;
    OPEN_CFW_SMPI_CONFIG.maximum_attempts = 3U;
}

int main(void)
{
    struct open_cfw_smpi_ccb ccb; union open_cfw_smpi_message msg;
    uint8_t incoming[32], cipher[16]; unsigned i;
    reset(&ccb, &msg); msg.pair.oob=1U; msg.pair.authentication=5U;
    msg.pair.initiator_keys=5U; msg.pair.responder_keys=3U;
    open_cfw_cordio_smpi_pair_request(&ccb,&msg);
    assert(host_alloc_length==15U && ccb.next_command==2U && ccb.scratch==&host_scratch);
    assert(memcmp(host_sent+8U,(uint8_t[]){1,4,1,5,16,5,3},7U)==0);

    reset(&ccb,&msg); memset(incoming,0,sizeof(incoming)); msg.data.packet=incoming;
    incoming[8]=2U; incoming[13]=7U; ccb.pair_request[5]=1U;
    open_cfw_cordio_smpi_process_pair_response(&ccb,&msg);
    assert(host_exec_event==3U && host_exec_status==10U);
    reset(&ccb,&msg); msg.data.packet=incoming; memset(incoming,0,sizeof(incoming));
    incoming[8]=2U; ccb.pair_request[5]=7U; ccb.pair_request[6]=7U;
    open_cfw_cordio_smpi_process_pair_response(&ccb,&msg); assert(host_auth_calls==1U);

    reset(&ccb,&msg); msg.data.packet=incoming; incoming[9]=0xA5U;
    open_cfw_cordio_smpi_process_security_request(&ccb,&msg);
    assert(ccb.security_request==1U && host_callback_event==50U);
    msg.header.status=9U; open_cfw_cordio_smpi_check_security_request(&ccb,&msg);
    assert(ccb.security_request==0U && host_failed==9U);

    reset(&ccb,&msg); msg.aes.ciphertext=cipher; memset(cipher,0x11,16U);
    memset(host_scratch.buffers.b3,0x22,16U); ccb.attempts=1U;
    open_cfw_cordio_smpi_confirm_verify(&ccb,&msg);
    assert(ccb.attempts==2U && host_exec_event==3U && host_exec_status==4U);
    memcpy(host_scratch.buffers.b3,cipher,16U); host_exec_event=0U;
    open_cfw_cordio_smpi_confirm_verify(&ccb,&msg); assert(host_exec_event==0xA1U);

    reset(&ccb,&msg); msg.aes.ciphertext=cipher;
    for(i=0;i<16U;i++) cipher[i]=(uint8_t)(i+1U);
    ccb.pair_request[4]=12U; ccb.pair_response[4]=16U; ccb.authentication=4U;
    open_cfw_cordio_smpi_stk_encrypt(&ccb,&msg);
    assert(ccb.key_ready==1U && host_encrypt_level==2U);
    assert(memcmp(host_encrypt_key,cipher,12U)==0 && host_encrypt_key[12]==0U);

    reset(&ccb,&msg); ccb.pair_request[6]=3U; ccb.pair_response[6]=3U;
    open_cfw_cordio_smpi_setup_key_distribution(&ccb,&msg); assert(ccb.next_command==6U);
    host_receive_done=1U; msg.data.packet=incoming;
    open_cfw_cordio_smpi_receive_key(&ccb,&msg); assert(host_exec_event==12U);
    reset(&ccb,&msg); ccb.pair_request[5]=5U; ccb.pair_response[5]=5U;
    host_send_done=1U; open_cfw_cordio_smpi_send_key(&ccb,&msg);
    assert(host_exec_event==14U);
    return 0;
}
