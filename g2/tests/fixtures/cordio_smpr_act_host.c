#include <assert.h>
#include <stdint.h>
#include <string.h>
static uint8_t host_control_bytes[512], host_config_bytes[64];
#define OPEN_CFW_SMPR_CONTROL_BLOCK (*(struct open_cfw_smpr_control_block *)(void *)host_control_bytes)
#define OPEN_CFW_SMPR_CONFIG (*(struct open_cfw_smpr_config *)(void *)host_config_bytes)
#include "../../components/apollo_main/core_overlay/cordio_smpr_act.c"

static union open_cfw_smpr_scratch host_scratch;
static uint8_t host_packet[64], host_sent[64], host_exec_event, host_exec_status;
static uint8_t host_callback_event, host_auth_calls, host_failed, host_c1, host_s1;
static uint8_t host_send_done, host_receive_done; static uint16_t host_alloc_length;
void *open_cfw_retained_cordio_wsf_buffer_alloc(uint16_t n)
{ assert(n==64U); memset(&host_scratch,0,sizeof(host_scratch)); return &host_scratch; }
void open_cfw_retained_cordio_dm_conn_set_idle(uint8_t id,uint16_t mask,uint8_t idle)
{ assert(id==2U&&mask==1U&&idle==1U); }
void open_cfw_cordio_dm_sec_smp_callback_execute(void *m)
{ host_callback_event=((struct open_cfw_smpr_header *)m)->event; }
void open_cfw_retained_cordio_sec_rand(uint8_t *p,uint16_t n)
{ memset(p,0x5AU,n); }
uint8_t *open_cfw_cordio_smp_main_message_allocate(uint16_t n)
{ host_alloc_length=n;memset(host_packet,0,sizeof(host_packet));return host_packet; }
void open_cfw_cordio_smp_main_send_packet(struct open_cfw_smpr_ccb *c,uint8_t *p)
{ (void)c;memcpy(host_sent,p,host_alloc_length); }
void open_cfw_cordio_smp_main_calculate_c1_part1(struct open_cfw_smpr_ccb *c,const uint8_t *k,const uint8_t *r)
{ (void)c;assert(k==host_scratch.buffers.b1&&r==host_scratch.buffers.b4);host_c1=1U; }
void open_cfw_cordio_smp_main_calculate_s1(struct open_cfw_smpr_ccb *c,const uint8_t *k,const uint8_t *r1,const uint8_t *r2)
{ (void)c;assert(k==host_scratch.buffers.b1&&r1==host_scratch.buffers.b4&&r2==host_scratch.buffers.b2);host_s1=1U; }
void open_cfw_cordio_smp_act_start_response_timer(struct open_cfw_smpr_ccb *c)
{c->response_timer.is_started=1U;}
uint8_t open_cfw_cordio_smp_act_receive_key(struct open_cfw_smpr_ccb *c,struct open_cfw_smpr_key_indication *i,uint8_t *p,uint8_t d)
{(void)c;(void)i;(void)p;assert(d==5U);return host_receive_done;}
uint8_t open_cfw_cordio_smp_act_send_key(struct open_cfw_smpr_ccb *c,uint8_t d)
{(void)c;assert(d==3U);return host_send_done;}
void open_cfw_cordio_smp_act_execute(struct open_cfw_smpr_ccb *c,union open_cfw_smpr_message *m)
{(void)c;host_exec_event=m->header.event;host_exec_status=m->header.status;}
void open_cfw_cordio_smp_db_pairing_failed(uint8_t id){assert(id==2U);host_failed++;}
void open_cfw_iar_memcpy_void(void*d,const void*s,uint32_t n){memcpy(d,s,n);}
void *open_cfw_runtime_memory_zero(void*d,uint32_t n){return memset(d,0,n);}
int open_cfw_retained_iar_memcmp(const void*a,const void*b,uint32_t n){return memcmp(a,b,n);}
static uint8_t pair(struct open_cfw_smpr_ccb*c,uint8_t*o,uint8_t*d)
{(void)c;*o=1U;*d=1U;return 1U;}
static void auth(struct open_cfw_smpr_ccb*c,uint8_t o,uint8_t d)
{(void)c;assert(o==1U&&d==1U);host_auth_calls++;}
static void reset(struct open_cfw_smpr_ccb*c,union open_cfw_smpr_message*m)
{
 memset(c,0,sizeof(*c));memset(m,0,sizeof(*m));memset(host_sent,0,sizeof(host_sent));
 host_exec_event=host_exec_status=host_callback_event=host_auth_calls=host_failed=host_c1=host_s1=0U;
 c->connection_id=2U;c->scratch=&host_scratch;
 OPEN_CFW_SMPR_CONTROL_BLOCK.process_pairing=pair;OPEN_CFW_SMPR_CONTROL_BLOCK.process_authentication=auth;
 OPEN_CFW_SMPR_CONFIG.io_capability=4U;OPEN_CFW_SMPR_CONFIG.maximum_key_length=16U;OPEN_CFW_SMPR_CONFIG.maximum_attempts=3U;
}
int main(void)
{
 struct open_cfw_smpr_ccb c;union open_cfw_smpr_message m;uint8_t in[32],cipher[16];unsigned i;
 reset(&c,&m);m.security.authentication=5U;open_cfw_cordio_smpr_send_security_request(&c,&m);
 assert(host_alloc_length==10U&&memcmp(host_sent+8U,(uint8_t[]){11,5},2U)==0);

 reset(&c,&m);memset(in,0,sizeof(in));m.data.packet=in;
 memcpy(in+8U,(uint8_t[]){1,2,1,5,16,3,5},7U);
 open_cfw_cordio_smpr_process_pair_request(&c,&m);
 assert(c.scratch==&host_scratch&&host_callback_event==49U&&memcmp(c.pair_request,in+8U,7U)==0);

 reset(&c,&m);m.pair.oob=1U;m.pair.authentication=5U;m.pair.initiator_keys=3U;m.pair.responder_keys=5U;
 c.pair_request[3]=5U;open_cfw_cordio_smpr_send_pair_response(&c,&m);
 assert(c.next_command==3U&&host_auth_calls==1U);
 assert(memcmp(host_sent+8U,(uint8_t[]){2,4,1,5,16,3,5},7U)==0);
 m.pair.authentication=13U;c.pair_request[3]=13U;open_cfw_cordio_smpr_send_pair_response(&c,&m);assert(c.next_command==12U);

 reset(&c,&m);m.data.packet=in;for(i=0;i<16U;i++)in[9U+i]=(uint8_t)i;
 open_cfw_cordio_smpr_process_pair_confirm_calculate(&c,&m);
 assert(c.next_command==0U&&host_c1==1U&&host_scratch.buffers.b3[15]==15U&&host_scratch.buffers.b4[0]==0x5AU);

 reset(&c,&m);m.aes.ciphertext=cipher;memset(cipher,1,16U);memset(host_scratch.buffers.b3,2,16U);
 c.attempts=2U;open_cfw_cordio_smpr_confirm_verify(&c,&m);
 assert(host_failed==1U&&host_exec_event==13U&&host_exec_status==4U);
 memcpy(host_scratch.buffers.b3,cipher,16U);open_cfw_cordio_smpr_confirm_verify(&c,&m);assert(host_s1==1U);

 reset(&c,&m);m.aes.ciphertext=cipher;for(i=0;i<16U;i++)cipher[i]=(uint8_t)(i+1U);
 c.pair_request[4]=10U;c.pair_response[4]=16U;open_cfw_cordio_smpr_send_pair_random(&c,&m);
 assert(c.key_ready==1U&&host_scratch.buffers.b3[9]==10U&&host_scratch.buffers.b3[10]==0U);
 assert(host_sent[8U]==4U&&host_sent[9U]==0x5AU);

 reset(&c,&m);c.pair_request[6]=3U;c.pair_response[6]=3U;c.pair_request[5]=5U;c.pair_response[5]=5U;
 host_send_done=1U;open_cfw_cordio_smpr_setup_key_distribution(&c,&m);assert(c.next_command==6U);
 c.next_command=0U;open_cfw_cordio_smpr_send_key(&c,&m);assert(c.next_command==6U);
 host_receive_done=1U;m.data.packet=in;open_cfw_cordio_smpr_receive_key(&c,&m);assert(host_exec_event==14U);
 return 0;
}
