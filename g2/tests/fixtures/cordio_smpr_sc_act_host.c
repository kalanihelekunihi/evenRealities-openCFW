#include <stdint.h>
#include <string.h>

static unsigned char test_config_storage[32];
static const uint8_t test_zeros[16] = {0};
#define OPEN_CFW_SMPR_SC_CONFIG \
    (*(struct open_cfw_smpr_sc_config *)test_config_storage)
#define OPEN_CFW_SMPR_SC_ZEROS test_zeros
#include "../../components/apollo_main/core_overlay/cordio_smpr_sc_act.c"

static struct open_cfw_smpr_sc_public_key local_key, peer_key;
static struct open_cfw_smpr_sc_scratch scratch;
static struct open_cfw_smpr_sc_ltk ltk;
static uint8_t packet[64], cipher[16];
static uint8_t state_event, state_status, sent_kind, fail_calls, db_calls;
static uint8_t f4_z, auth_select_calls, display_calls, shared_secret_calls;

static void reset_fixture(struct open_cfw_smpr_sc_ccb *ccb,
    struct open_cfw_smpr_sc_record *sc, union open_cfw_smpr_sc_message *message)
{
    memset(test_config_storage, 0, sizeof(test_config_storage));
    memset(ccb, 0, sizeof(*ccb)); memset(sc, 0, sizeof(*sc));
    memset(message, 0, sizeof(*message)); memset(&scratch, 0, sizeof(scratch));
    memset(&ltk, 0, sizeof(ltk)); memset(packet, 0, sizeof(packet));
    memset(cipher, 0, sizeof(cipher)); memset(&local_key, 0, sizeof(local_key));
    memset(&peer_key, 0, sizeof(peer_key));
    sc->local_public_key = &local_key; sc->peer_public_key = &peer_key;
    sc->scratch = &scratch; sc->ltk = &ltk; ccb->secure_connections = sc;
    ccb->connection_id = 2U; message->data.packet = packet;
    state_event = state_status = sent_kind = fail_calls = db_calls = 0U;
    f4_z = auth_select_calls = display_calls = shared_secret_calls = 0U;
    OPEN_CFW_SMPR_SC_CONFIG.maximum_attempts = 3U;
}

void open_cfw_retained_cordio_wstr_reverse_copy(uint8_t *d,const uint8_t *s,uint16_t n)
{ for(uint16_t i=0;i<n;i++)d[i]=s[n-i-1U]; }
void open_cfw_retained_cordio_calc128_copy(uint8_t d[16],const uint8_t s[16])
{ memcpy(d,s,16); }
void open_cfw_retained_cordio_sec_rand(uint8_t *b,uint16_t n)
{ for(uint16_t i=0;i<n;i++)b[i]=(uint8_t)(0x40U+i); }
int open_cfw_retained_iar_memcmp(const void *a,const void *b,uint32_t n)
{ return memcmp(a,b,n); }
void *open_cfw_runtime_memory_zero(void *d,uint32_t n){return memset(d,0,n);}
void open_cfw_retained_cordio_smp_state_machine_execute(struct open_cfw_smpr_sc_ccb *c,void *m)
{ const struct open_cfw_smpr_sc_header *h=m;(void)c;state_event=h->event;state_status=h->status; }
void open_cfw_cordio_smp_sc_act_authentication_select(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{(void)c;(void)m;auth_select_calls++;}
void open_cfw_cordio_smp_sc_send_public_key(struct open_cfw_smpr_sc_ccb *c,struct open_cfw_smpr_sc_header *m)
{(void)c;(void)m;sent_kind=12U;}
void open_cfw_cordio_smp_sc_send_random(struct open_cfw_smpr_sc_ccb *c,struct open_cfw_smpr_sc_header *m,uint8_t *v)
{(void)c;(void)m;if(v)sent_kind=4U;}
void open_cfw_cordio_smp_sc_send_pairing_confirm(struct open_cfw_smpr_sc_ccb *c,struct open_cfw_smpr_sc_header *m,uint8_t *v)
{(void)c;(void)m;if(v)sent_kind=3U;}
void open_cfw_cordio_smp_sc_send_dh_key_check(struct open_cfw_smpr_sc_ccb *c,struct open_cfw_smpr_sc_header *m,uint8_t *v)
{(void)c;(void)m;if(v)sent_kind=13U;}
void open_cfw_cordio_smp_sc_calculate_f4(struct open_cfw_smpr_sc_ccb *c,struct open_cfw_smpr_sc_header *m,uint8_t *u,uint8_t *v,uint8_t z,uint8_t *x)
{(void)c;(void)m;(void)u;(void)v;(void)x;f4_z=z;}
uint8_t open_cfw_cordio_smp_sc_get_passkey_bit(struct open_cfw_smpr_sc_ccb *c)
{(void)c;return 0x81U;}
void open_cfw_cordio_smp_sc_fail_with_reattempt(struct open_cfw_smpr_sc_ccb *c)
{(void)c;fail_calls++;}
void open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{(void)c;(void)m;sent_kind=0xf4U;}
void open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{(void)c;(void)m;sent_kind=0xf2U;}
void open_cfw_cordio_smp_sc_act_jwnc_display(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{(void)c;(void)m;display_calls++;}
void open_cfw_cordio_smp_sc_act_calculate_shared_secret(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{(void)c;(void)m;shared_secret_calls++;}
void open_cfw_cordio_smp_db_pairing_failed(uint8_t id){if(id==2U)db_calls++;}

int open_cfw_test_smpr_sc_store_and_setup(void)
{
    struct open_cfw_smpr_sc_ccb c;struct open_cfw_smpr_sc_record s;union open_cfw_smpr_sc_message m;
    reset_fixture(&c,&s,&m);s.authentication_type=OPEN_CFW_SMPR_SC_AUTH_PASSKEY;
    m.authentication.length=3U;m.authentication.data[0]=1U;m.authentication.data[1]=2U;m.authentication.data[2]=3U;
    open_cfw_cordio_smpr_sc_store_pin(&c,&m);if(scratch.ra[13]!=3U||scratch.ra[15]!=1U||memcmp(scratch.ra,scratch.rb,16U)!=0)return 1;
    open_cfw_cordio_smpr_sc_send_public_key(&c,&m);open_cfw_cordio_smpr_sc_jwnc_setup(&c,&m);
    return !(auth_select_calls==1U&&scratch.responder_random[0]==0x40U&&c.next_command==4U&&sent_kind==0xf4U);
}
int open_cfw_test_smpr_sc_jwnc_and_passkey(void)
{
    struct open_cfw_smpr_sc_ccb c;struct open_cfw_smpr_sc_record s;union open_cfw_smpr_sc_message m;
    reset_fixture(&c,&s,&m);for(unsigned i=0;i<16;i++){packet[9+i]=(uint8_t)i;cipher[i]=(uint8_t)(15U-i);}
    m.aes.ciphertext=cipher;open_cfw_cordio_smpr_sc_jwnc_send_confirm(&c,&m);if(sent_kind!=3U)return 1;
    m.data.packet=packet;open_cfw_cordio_smpr_sc_jwnc_calculate_g2(&c,&m);if(scratch.initiator_random[0]!=15U||sent_kind!=0xf2U)return 1;
    open_cfw_cordio_smpr_sc_jwnc_display(&c,&m);if(c.next_command!=13U||sent_kind!=4U||display_calls!=1U)return 1;
    open_cfw_cordio_smpr_sc_passkey_store_confirm(&c,&m);m.aes.ciphertext=scratch.peer_ca_or_ea;s.passkey_position=19U;
    open_cfw_cordio_smpr_sc_passkey_send_random(&c,&m);
    return !(s.passkey_position==20U&&state_event==27U&&fail_calls==0U);
}
int open_cfw_test_smpr_sc_passkey_failure_and_oob(void)
{
    struct open_cfw_smpr_sc_ccb c;struct open_cfw_smpr_sc_record s;union open_cfw_smpr_sc_message m;
    reset_fixture(&c,&s,&m);m.aes.ciphertext=cipher;cipher[0]=1U;
    open_cfw_cordio_smpr_sc_passkey_send_random(&c,&m);if(fail_calls!=1U)return 1;
    reset_fixture(&c,&s,&m);c.pair_request[2]=0U;c.pair_response[2]=0U;m.data.packet=packet;
    open_cfw_cordio_smpr_sc_oob_calculate_ca(&c,&m);if(state_event!=28U||scratch.ra[0]!=0U||scratch.rb[0]!=0U)return 1;
    open_cfw_cordio_smpr_sc_oob_send_random(&c,&m);
    return !(c.next_command==13U&&scratch.responder_random[0]==0x40U&&sent_kind==4U);
}
int open_cfw_test_smpr_sc_dh_success_key_ready(void)
{
    struct open_cfw_smpr_sc_ccb c;struct open_cfw_smpr_sc_record s;union open_cfw_smpr_sc_message m;
    reset_fixture(&c,&s,&m);for(unsigned i=0;i<16;i++){scratch.peer_ca_or_ea[i]=(uint8_t)i;scratch.initiator_random[i]=(uint8_t)i;ltk.temporary_ltk[i]=(uint8_t)(0xa0U+i);cipher[i]=(uint8_t)(0x70U+i);}
    c.pair_request[4]=12U;c.pair_response[4]=10U;m.aes.ciphertext=cipher;
    open_cfw_cordio_smpr_sc_dh_key_check_send(&c,&m);
    return !(c.key_ready==1U&&sent_kind==13U&&scratch.responder_random[0]==0x70U&&ltk.temporary_ltk[9]==0xa9U&&ltk.temporary_ltk[10]==0U&&ltk.temporary_ltk[15]==0U);
}
int open_cfw_test_smpr_sc_dh_failure_retry(void)
{
    struct open_cfw_smpr_sc_ccb c;struct open_cfw_smpr_sc_record s;union open_cfw_smpr_sc_message m;
    reset_fixture(&c,&s,&m);scratch.peer_ca_or_ea[0]=1U;m.aes.ciphertext=cipher;c.attempts=1U;
    open_cfw_cordio_smpr_sc_dh_key_check_send(&c,&m);if(c.attempts!=2U||db_calls!=1U||state_event!=29U||state_status!=11U)return 1;
    open_cfw_cordio_smpr_sc_dh_key_check_send(&c,&m);
    return !(c.attempts==3U&&db_calls==2U&&state_event==13U);
}
int open_cfw_test_smpr_sc_dh_store_wait_calculate(void)
{
    struct open_cfw_smpr_sc_ccb c;struct open_cfw_smpr_sc_record s;union open_cfw_smpr_sc_message m;
    reset_fixture(&c,&s,&m);for(unsigned i=0;i<16;i++)packet[9+i]=(uint8_t)i;m.data.packet=packet;
    open_cfw_cordio_smpr_sc_store_dh_key_check(&c,&m);if(c.next_command!=15U||scratch.peer_ca_or_ea[0]!=15U)return 1;
    s.authentication_type=OPEN_CFW_SMPR_SC_AUTH_PASSKEY;open_cfw_cordio_smpr_sc_wait_dh_key_check(&c,&m);if(c.next_command!=13U||sent_kind!=4U)return 1;
    open_cfw_cordio_smpr_sc_calculate_dh_key(&c,&m);
    return !(scratch.peer_ca_or_ea[0]==15U&&shared_secret_calls==1U);
}
