#include <stdint.h>
#include <string.h>

static unsigned char test_config_storage[32];
static const uint8_t test_zeros[16] = {0};
#define OPEN_CFW_SMPI_SC_CONFIG \
    (*(struct open_cfw_smpi_sc_config *)test_config_storage)
#define OPEN_CFW_SMPI_SC_ZEROS test_zeros
#include "../../components/apollo_main/core_overlay/cordio_smpi_sc_act.c"

static struct open_cfw_smpi_sc_public_key local_key, peer_key;
static struct open_cfw_smpi_sc_scratch scratch;
static struct open_cfw_smpi_sc_ltk ltk;
static uint8_t packet[64], cipher[16];
static uint8_t state_event, state_status, sent_kind, fail_calls, db_calls;
static uint8_t encrypt_calls, encrypt_level, f4_z, auth_select_calls;

static void reset_fixture(struct open_cfw_smpi_sc_ccb *ccb,
    struct open_cfw_smpi_sc_record *sc, union open_cfw_smpi_sc_message *message)
{
    memset(test_config_storage, 0, sizeof(test_config_storage));
    memset(ccb, 0, sizeof(*ccb)); memset(sc, 0, sizeof(*sc));
    memset(message, 0, sizeof(*message)); memset(&scratch, 0, sizeof(scratch));
    memset(&ltk, 0, sizeof(ltk)); memset(packet, 0, sizeof(packet));
    memset(cipher, 0, sizeof(cipher));
    sc->local_public_key = &local_key; sc->peer_public_key = &peer_key;
    sc->scratch = &scratch; sc->ltk = &ltk; ccb->secure_connections = sc;
    ccb->connection_id = 2U; message->data.packet = packet;
    state_event = state_status = sent_kind = fail_calls = db_calls = 0U;
    encrypt_calls = encrypt_level = f4_z = auth_select_calls = 0U;
    OPEN_CFW_SMPI_SC_CONFIG.maximum_attempts = 3U;
}

void open_cfw_retained_cordio_wstr_reverse_copy(uint8_t *d,const uint8_t *s,uint16_t n)
{ for(uint16_t i=0;i<n;i++)d[i]=s[n-i-1U]; }
void open_cfw_retained_cordio_calc128_copy(uint8_t d[16],const uint8_t s[16])
{ memcpy(d,s,16); }
void open_cfw_retained_cordio_sec_rand(uint8_t *b,uint16_t n)
{ for(uint16_t i=0;i<n;i++)b[i]=(uint8_t)(0x40U+i); }
void open_cfw_iar_memcpy_void(void *d,const void *s,uint32_t n){memcpy(d,s,n);}
void *open_cfw_runtime_memory_zero(void *d,uint32_t n){return memset(d,0,n);}
int open_cfw_retained_iar_memcmp(const void *a,const void *b,uint32_t n)
{return memcmp(a,b,n);}
void open_cfw_retained_cordio_smp_state_machine_execute(struct open_cfw_smpi_sc_ccb *c,void *m)
{ const struct open_cfw_smpi_sc_header *h=m;(void)c;state_event=h->event;state_status=h->status; }
void open_cfw_cordio_smp_sc_act_authentication_select(struct open_cfw_smpi_sc_ccb *c,union open_cfw_smpi_sc_message *m)
{(void)c;(void)m;auth_select_calls++;}
void open_cfw_cordio_smp_sc_send_public_key(struct open_cfw_smpi_sc_ccb *c,struct open_cfw_smpi_sc_header *m)
{(void)c;(void)m;sent_kind=12U;}
void open_cfw_cordio_smp_sc_send_random(struct open_cfw_smpi_sc_ccb *c,struct open_cfw_smpi_sc_header *m,uint8_t *v)
{(void)c;(void)m;if(v)sent_kind=4U;}
void open_cfw_cordio_smp_sc_send_pairing_confirm(struct open_cfw_smpi_sc_ccb *c,struct open_cfw_smpi_sc_header *m,uint8_t *v)
{(void)c;(void)m;if(v)sent_kind=3U;}
void open_cfw_cordio_smp_sc_send_dh_key_check(struct open_cfw_smpi_sc_ccb *c,struct open_cfw_smpi_sc_header *m,uint8_t *v)
{(void)c;(void)m;if(v)sent_kind=13U;}
void open_cfw_cordio_smp_sc_calculate_f4(struct open_cfw_smpi_sc_ccb *c,struct open_cfw_smpi_sc_header *m,uint8_t *u,uint8_t *v,uint8_t z,uint8_t *x)
{(void)c;(void)m;(void)u;(void)v;(void)x;f4_z=z;}
uint8_t open_cfw_cordio_smp_sc_get_passkey_bit(struct open_cfw_smpi_sc_ccb *c)
{(void)c;return 0x81U;}
void open_cfw_cordio_smp_sc_fail_with_reattempt(struct open_cfw_smpi_sc_ccb *c)
{(void)c;fail_calls++;}
void open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(struct open_cfw_smpi_sc_ccb *c,union open_cfw_smpi_sc_message *m)
{(void)c;(void)m;sent_kind=0xf4U;}
void open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(struct open_cfw_smpi_sc_ccb *c,union open_cfw_smpi_sc_message *m)
{(void)c;(void)m;sent_kind=0xf2U;}
void open_cfw_cordio_smp_sc_act_calculate_shared_secret(struct open_cfw_smpi_sc_ccb *c,union open_cfw_smpi_sc_message *m)
{(void)c;(void)m;sent_kind=0xd1U;}
void open_cfw_cordio_smp_db_pairing_failed(uint8_t id){if(id==2U)db_calls++;}
uint8_t open_cfw_cordio_smp_main_get_sc_security_level(struct open_cfw_smpi_sc_ccb *c)
{(void)c;return 3U;}
void open_cfw_cordio_dm_sec_master_smp_encrypt_request(uint8_t id,uint8_t level,const uint8_t key[16])
{if(id==2U&&key){encrypt_calls++;encrypt_level=level;memcpy(cipher,key,16);}}

int open_cfw_test_smpi_sc_setup_and_send(void)
{
    struct open_cfw_smpi_sc_ccb c;struct open_cfw_smpi_sc_record s;union open_cfw_smpi_sc_message m;
    reset_fixture(&c,&s,&m);open_cfw_cordio_smpi_sc_authentication_select(&c,&m);
    open_cfw_cordio_smpi_sc_send_public_key(&c,&m);if(auth_select_calls!=1U||c.next_command!=12U||sent_kind!=12U)return 1;
    open_cfw_cordio_smpi_sc_jwnc_setup(&c,&m);
    return !(scratch.initiator_random[0]==0x40U&&scratch.ra[0]==0U&&c.next_command==3U);
}
int open_cfw_test_smpi_sc_jwnc_and_passkey(void)
{
    struct open_cfw_smpi_sc_ccb c;struct open_cfw_smpi_sc_record s;union open_cfw_smpi_sc_message m;
    reset_fixture(&c,&s,&m);for(unsigned i=0;i<16;i++){packet[9+i]=(uint8_t)i;cipher[i]=(uint8_t)(15-i);}
    open_cfw_cordio_smpi_sc_jwnc_send_random(&c,&m);if(scratch.peer_cb[0]!=15U||sent_kind!=4U)return 1;
    m.aes.ciphertext=cipher;open_cfw_cordio_smpi_sc_jwnc_calculate_g2(&c,&m);if(sent_kind!=0xf2U)return 1;
    s.passkey_position=19U;open_cfw_cordio_smpi_sc_passkey_check(&c,&m);
    return !(s.passkey_position==20U&&state_event==27U);
}
int open_cfw_test_smpi_sc_passkey_and_oob_crypto(void)
{
    struct open_cfw_smpi_sc_ccb c;struct open_cfw_smpi_sc_record s;union open_cfw_smpi_sc_message m;
    reset_fixture(&c,&s,&m);m.authentication.length=3U;m.authentication.data[0]=1U;m.authentication.data[1]=2U;m.authentication.data[2]=3U;
    open_cfw_cordio_smpi_sc_passkey_calculate_ca(&c,&m);if(f4_z!=0x81U||scratch.ra[13]!=3U||scratch.ra[15]!=1U)return 1;
    c.pair_request[2]=0U;c.pair_response[2]=0U;open_cfw_cordio_smpi_sc_oob_calculate_cb(&c,&m);
    return !(state_event==28U&&scratch.rb[0]==0U);
}
int open_cfw_test_smpi_sc_dh_success_key_ready(void)
{
    struct open_cfw_smpi_sc_ccb c;struct open_cfw_smpi_sc_record s;union open_cfw_smpi_sc_message m;
    reset_fixture(&c,&s,&m);for(unsigned i=0;i<16;i++){scratch.responder_random[i]=(uint8_t)i;packet[9+i]=(uint8_t)i;ltk.temporary_ltk[i]=(uint8_t)(0xa0U+i);}
    c.pair_request[4]=12U;c.pair_response[4]=10U;open_cfw_cordio_smpi_sc_dh_key_check_verify(&c,&m);
    return !(c.key_ready==1U&&encrypt_calls==1U&&encrypt_level==3U&&cipher[0]==0xa0U&&cipher[9]==0xa9U&&cipher[10]==0U&&cipher[15]==0U);
}
int open_cfw_test_smpi_sc_dh_failure_retry(void)
{
    struct open_cfw_smpi_sc_ccb c;struct open_cfw_smpi_sc_record s;union open_cfw_smpi_sc_message m;
    reset_fixture(&c,&s,&m);packet[9]=1U;c.attempts=1U;open_cfw_cordio_smpi_sc_dh_key_check_verify(&c,&m);
    if(c.attempts!=2U||db_calls!=1U||state_event!=29U||state_status!=11U)return 1;
    c.attempts=2U;open_cfw_cordio_smpi_sc_dh_key_check_verify(&c,&m);
    return !(c.attempts==3U&&state_event==13U);
}
