/*
 * SPDX-License-Identifier: Apache-2.0
 * Production adapter for all twenty G2-linked Cordio responder Secure
 * Connections actions.  The stock r20/R4 keyReady transition is explicit.
 */
#include <stddef.h>
#include <stdint.h>

#if !defined(OPEN_CFW_SMPR_SC_STORE_PIN_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_SEND_PUBLIC_KEY_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_JWNC_SETUP_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_JWNC_SEND_CONFIRM_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_JWNC_G2_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_JWNC_DISPLAY_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_STORE_CONFIRM_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_STORE_CONFIRM_CALC_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_STORE_PIN_CALC_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_CB_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_SEND_CONFIRM_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_CA_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_PASSKEY_SEND_RANDOM_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_OOB_SETUP_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_OOB_CA_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_OOB_SEND_RANDOM_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_STORE_DH_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_WAIT_DH_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_CALC_DH_ONLY) && \
 !defined(OPEN_CFW_SMPR_SC_DH_SEND_ONLY)
#define OPEN_CFW_SMPR_SC_ALL 1
#else
#define OPEN_CFW_SMPR_SC_ALL 0
#endif

#define OPEN_CFW_SMPR_SC_PDU_OFFSET 8U
#define OPEN_CFW_SMPR_SC_PAIR_OOB 2U
#define OPEN_CFW_SMPR_SC_PAIR_MAX_KEY 4U
#define OPEN_CFW_SMPR_SC_OOB_PRESENT 1U
#define OPEN_CFW_SMPR_SC_AUTH_PASSKEY 3U
#define OPEN_CFW_SMPR_SC_CMD_CONFIRM 3U
#define OPEN_CFW_SMPR_SC_CMD_RANDOM 4U
#define OPEN_CFW_SMPR_SC_CMD_DH_CHECK 13U
#define OPEN_CFW_SMPR_SC_CMD_MAX 15U
#define OPEN_CFW_SMPR_SC_EVENT_MAX_ATTEMPTS 13U
#define OPEN_CFW_SMPR_SC_EVENT_PASSKEY_NEXT 26U
#define OPEN_CFW_SMPR_SC_EVENT_PASSKEY_COMPLETE 27U
#define OPEN_CFW_SMPR_SC_EVENT_CMAC_COMPLETE 28U
#define OPEN_CFW_SMPR_SC_EVENT_DH_FAILURE 29U
#define OPEN_CFW_SMPR_SC_ERROR_DH_CHECK 11U
#define OPEN_CFW_SMPR_SC_PASSKEY_BITS 20U

struct open_cfw_smpr_sc_header { uint16_t param; uint8_t event, status; };
struct open_cfw_smpr_sc_timer {
    uint32_t next; struct open_cfw_smpr_sc_header message; uint32_t ticks;
    uint8_t handler_id, is_started, reserved[2];
};
union open_cfw_smpr_sc_legacy_scratch { uint8_t bytes[64]; uint32_t alignment; };
struct open_cfw_smpr_sc_public_key { uint8_t x[32], y[32]; };
struct open_cfw_smpr_sc_scratch {
    uint8_t initiator_random[16], responder_random[16], ra[16], rb[16];
    uint8_t peer_cb[16], peer_ca_or_ea[16];
};
struct open_cfw_smpr_sc_ltk { uint8_t mac[16], temporary_ltk[16]; };
struct open_cfw_smpr_sc_record {
    uint8_t lesc_enabled, authentication_type, keypress_notify;
    uint8_t passkey_position, display, reserved[3];
    struct open_cfw_smpr_sc_public_key *peer_public_key, *local_public_key;
    uint8_t *private_key; struct open_cfw_smpr_sc_scratch *scratch;
    struct open_cfw_smpr_sc_ltk *ltk;
};
struct open_cfw_smpr_sc_ccb {
    struct open_cfw_smpr_sc_timer response_timer, wait_timer;
    uint8_t pair_request[7], pair_response[7], reserved46[2];
    union open_cfw_smpr_sc_legacy_scratch *legacy_scratch; uint8_t *queued_packet;
    uint16_t handle; uint8_t initiator, security_request, flow_disabled;
    uint8_t connection_id, state, next_command, authentication, token, attempts;
    uint8_t last_sent_key, key_ready, reserved69[3];
    struct open_cfw_smpr_sc_record *secure_connections;
};
struct open_cfw_smpr_sc_config {
    uint32_t attempt_timeout; uint8_t io_capability, minimum_key_length;
    uint8_t maximum_key_length, maximum_attempts, authentication, reserved9[3];
    uint32_t maximum_attempt_timeout, attempt_decrement_timeout;
    uint16_t attempt_exponent;
};
struct open_cfw_smpr_sc_auth_response {
    struct open_cfw_smpr_sc_header header; uint8_t data[16], length;
};
struct open_cfw_smpr_sc_data_message {
    struct open_cfw_smpr_sc_header header; uint8_t *packet;
};
struct open_cfw_smpr_sc_aes_message {
    struct open_cfw_smpr_sc_header header; uint8_t *ciphertext, *plaintext;
};
union open_cfw_smpr_sc_message {
    struct open_cfw_smpr_sc_header header;
    struct open_cfw_smpr_sc_auth_response authentication;
    struct open_cfw_smpr_sc_data_message data;
    struct open_cfw_smpr_sc_aes_message aes;
};
#if UINTPTR_MAX == 0xFFFFFFFFU
_Static_assert(sizeof(struct open_cfw_smpr_sc_record)==0x1CU,"SC ABI");
_Static_assert(sizeof(struct open_cfw_smpr_sc_ccb)==0x4CU,"SMP ABI");
_Static_assert(offsetof(struct open_cfw_smpr_sc_ccb,key_ready)==0x44U,"keyReady ABI");
#endif
#ifndef OPEN_CFW_SMPR_SC_CONFIG
#define OPEN_CFW_SMPR_SC_CONFIG (**(struct open_cfw_smpr_sc_config **)(uintptr_t)0x200004B8U)
#endif
#ifndef OPEN_CFW_SMPR_SC_ZEROS
#define OPEN_CFW_SMPR_SC_ZEROS ((const uint8_t *)(uintptr_t)0x007856B0U)
#endif

extern void open_cfw_retained_cordio_wstr_reverse_copy(uint8_t *,const uint8_t *,uint16_t);
extern void open_cfw_retained_cordio_calc128_copy(uint8_t[16],const uint8_t[16]);
extern void open_cfw_retained_cordio_sec_rand(uint8_t *,uint16_t);
extern int open_cfw_retained_iar_memcmp(const void *,const void *,uint32_t);
extern void *open_cfw_runtime_memory_zero(void *,uint32_t);
extern void open_cfw_retained_cordio_smp_state_machine_execute(struct open_cfw_smpr_sc_ccb *,void *);
extern void open_cfw_cordio_smp_sc_act_authentication_select(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
extern void open_cfw_cordio_smp_sc_send_public_key(struct open_cfw_smpr_sc_ccb *,struct open_cfw_smpr_sc_header *);
extern void open_cfw_cordio_smp_sc_send_random(struct open_cfw_smpr_sc_ccb *,struct open_cfw_smpr_sc_header *,uint8_t *);
extern void open_cfw_cordio_smp_sc_send_pairing_confirm(struct open_cfw_smpr_sc_ccb *,struct open_cfw_smpr_sc_header *,uint8_t *);
extern void open_cfw_cordio_smp_sc_send_dh_key_check(struct open_cfw_smpr_sc_ccb *,struct open_cfw_smpr_sc_header *,uint8_t *);
extern void open_cfw_cordio_smp_sc_calculate_f4(struct open_cfw_smpr_sc_ccb *,struct open_cfw_smpr_sc_header *,uint8_t *,uint8_t *,uint8_t,uint8_t *);
extern uint8_t open_cfw_cordio_smp_sc_get_passkey_bit(struct open_cfw_smpr_sc_ccb *);
extern void open_cfw_cordio_smp_sc_fail_with_reattempt(struct open_cfw_smpr_sc_ccb *);
extern void open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
extern void open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
extern void open_cfw_cordio_smp_sc_act_jwnc_display(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
extern void open_cfw_cordio_smp_sc_act_calculate_shared_secret(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
extern void open_cfw_cordio_smp_db_pairing_failed(uint8_t);

void open_cfw_cordio_smpr_sc_store_pin(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
void open_cfw_cordio_smpr_sc_passkey_store_confirm(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);
void open_cfw_cordio_smpr_sc_passkey_calculate_cb(struct open_cfw_smpr_sc_ccb *,union open_cfw_smpr_sc_message *);

#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_STORE_PIN_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_store_pin(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_record *s=c->secure_connections;
    if(s->authentication_type==OPEN_CFW_SMPR_SC_AUTH_PASSKEY){
        open_cfw_retained_cordio_calc128_copy(s->scratch->ra,OPEN_CFW_SMPR_SC_ZEROS);
        open_cfw_retained_cordio_calc128_copy(s->scratch->rb,OPEN_CFW_SMPR_SC_ZEROS);
        if(m->authentication.length<=3U){
            open_cfw_retained_cordio_wstr_reverse_copy(&s->scratch->ra[13],m->authentication.data,m->authentication.length);
            open_cfw_retained_cordio_wstr_reverse_copy(&s->scratch->rb[13],m->authentication.data,m->authentication.length);
        }
    }
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_SEND_PUBLIC_KEY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_send_public_key(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_cordio_smp_sc_act_authentication_select(c,m);open_cfw_cordio_smp_sc_send_public_key(c,&m->header);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_JWNC_SETUP_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_jwnc_setup(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_scratch *s=c->secure_connections->scratch;
    open_cfw_retained_cordio_sec_rand(s->responder_random,16U);
    open_cfw_retained_cordio_calc128_copy(s->ra,OPEN_CFW_SMPR_SC_ZEROS);
    open_cfw_retained_cordio_calc128_copy(s->rb,OPEN_CFW_SMPR_SC_ZEROS);
    c->next_command=OPEN_CFW_SMPR_SC_CMD_RANDOM;
    open_cfw_cordio_smp_sc_act_jwnc_calculate_f4(c,m);
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_JWNC_SEND_CONFIRM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_jwnc_send_confirm(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_cordio_smp_sc_send_pairing_confirm(c,&m->header,m->aes.ciphertext);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_JWNC_G2_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_jwnc_calculate_g2(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_retained_cordio_wstr_reverse_copy(c->secure_connections->scratch->initiator_random,m->data.packet+9U,16U);open_cfw_cordio_smp_sc_act_jwnc_calculate_g2(c,m);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_JWNC_DISPLAY_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_jwnc_display(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{c->next_command=OPEN_CFW_SMPR_SC_CMD_DH_CHECK;open_cfw_cordio_smp_sc_send_random(c,&m->header,c->secure_connections->scratch->responder_random);open_cfw_cordio_smp_sc_act_jwnc_display(c,m);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_STORE_CONFIRM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_store_confirm(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_retained_cordio_wstr_reverse_copy(c->secure_connections->scratch->peer_ca_or_ea,m->data.packet+9U,16U);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_STORE_CONFIRM_CALC_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_store_confirm_and_calculate_cb(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_cordio_smpr_sc_passkey_store_confirm(c,m);open_cfw_cordio_smpr_sc_passkey_calculate_cb(c,m);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_STORE_PIN_CALC_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_store_pin_and_calculate_cb(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_cordio_smpr_sc_store_pin(c,m);open_cfw_cordio_smpr_sc_passkey_calculate_cb(c,m);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_CB_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_calculate_cb(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_record *s=c->secure_connections;open_cfw_retained_cordio_sec_rand(s->scratch->responder_random,16U);c->next_command=OPEN_CFW_SMPR_SC_CMD_RANDOM;
    open_cfw_cordio_smp_sc_calculate_f4(c,&m->header,s->local_public_key->x,s->peer_public_key->x,open_cfw_cordio_smp_sc_get_passkey_bit(c),s->scratch->responder_random);
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_SEND_CONFIRM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_send_confirm(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{open_cfw_cordio_smp_sc_send_pairing_confirm(c,&m->header,m->aes.ciphertext);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_CA_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_calculate_ca(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_record *s=c->secure_connections;open_cfw_retained_cordio_wstr_reverse_copy(s->scratch->initiator_random,m->data.packet+9U,16U);
    open_cfw_cordio_smp_sc_calculate_f4(c,&m->header,s->peer_public_key->x,s->local_public_key->x,open_cfw_cordio_smp_sc_get_passkey_bit(c),s->scratch->initiator_random);
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_PASSKEY_SEND_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_passkey_send_random(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_record *s=c->secure_connections;struct open_cfw_smpr_sc_header h={c->connection_id,0U,0U};
    if(open_cfw_retained_iar_memcmp(s->scratch->peer_ca_or_ea,m->aes.ciphertext,16U)!=0){open_cfw_cordio_smp_sc_fail_with_reattempt(c);return;}
    s->passkey_position++;if(s->passkey_position>=OPEN_CFW_SMPR_SC_PASSKEY_BITS)h.event=OPEN_CFW_SMPR_SC_EVENT_PASSKEY_COMPLETE;
    else{c->next_command=OPEN_CFW_SMPR_SC_CMD_CONFIRM;h.event=OPEN_CFW_SMPR_SC_EVENT_PASSKEY_NEXT;open_cfw_cordio_smp_sc_send_random(c,&m->header,s->scratch->responder_random);}
    open_cfw_retained_cordio_smp_state_machine_execute(c,&h);
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_OOB_SETUP_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_oob_setup(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{(void)m;c->next_command=OPEN_CFW_SMPR_SC_CMD_RANDOM;}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_OOB_CA_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_oob_calculate_ca(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_record *s=c->secure_connections;open_cfw_retained_cordio_wstr_reverse_copy(s->scratch->initiator_random,m->data.packet+9U,16U);
    if(c->pair_request[OPEN_CFW_SMPR_SC_PAIR_OOB]!=OPEN_CFW_SMPR_SC_OOB_PRESENT)open_cfw_retained_cordio_calc128_copy(s->scratch->rb,OPEN_CFW_SMPR_SC_ZEROS);
    if(c->pair_response[OPEN_CFW_SMPR_SC_PAIR_OOB]==OPEN_CFW_SMPR_SC_OOB_PRESENT)open_cfw_cordio_smp_sc_calculate_f4(c,&m->header,s->peer_public_key->x,s->peer_public_key->x,0U,s->scratch->ra);
    else{struct open_cfw_smpr_sc_aes_message done;open_cfw_retained_cordio_calc128_copy(s->scratch->ra,OPEN_CFW_SMPR_SC_ZEROS);done.header.param=c->connection_id;done.header.event=OPEN_CFW_SMPR_SC_EVENT_CMAC_COMPLETE;done.header.status=0U;done.plaintext=NULL;open_cfw_retained_cordio_smp_state_machine_execute(c,&done);}
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_OOB_SEND_RANDOM_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_oob_send_random(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_scratch *s=c->secure_connections->scratch;if(c->pair_response[OPEN_CFW_SMPR_SC_PAIR_OOB]==OPEN_CFW_SMPR_SC_OOB_PRESENT&&open_cfw_retained_iar_memcmp(s->peer_ca_or_ea,m->aes.ciphertext,16U)!=0){open_cfw_cordio_smp_sc_fail_with_reattempt(c);return;}
    c->next_command=OPEN_CFW_SMPR_SC_CMD_DH_CHECK;open_cfw_retained_cordio_sec_rand(s->responder_random,16U);open_cfw_cordio_smp_sc_send_random(c,&m->header,s->responder_random);
}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_STORE_DH_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_store_dh_key_check(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{c->next_command=OPEN_CFW_SMPR_SC_CMD_MAX;open_cfw_retained_cordio_wstr_reverse_copy(c->secure_connections->scratch->peer_ca_or_ea,m->data.packet+9U,16U);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_WAIT_DH_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_wait_dh_key_check(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{c->next_command=OPEN_CFW_SMPR_SC_CMD_DH_CHECK;if(c->secure_connections->authentication_type==OPEN_CFW_SMPR_SC_AUTH_PASSKEY)open_cfw_cordio_smp_sc_send_random(c,&m->header,c->secure_connections->scratch->responder_random);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_CALC_DH_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_calculate_dh_key(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{if(c->next_command==OPEN_CFW_SMPR_SC_CMD_DH_CHECK)open_cfw_retained_cordio_wstr_reverse_copy(c->secure_connections->scratch->peer_ca_or_ea,m->data.packet+9U,16U);open_cfw_cordio_smp_sc_act_calculate_shared_secret(c,m);}
#endif
#if OPEN_CFW_SMPR_SC_ALL || defined(OPEN_CFW_SMPR_SC_DH_SEND_ONLY)
__attribute__((noinline)) void open_cfw_cordio_smpr_sc_dh_key_check_send(struct open_cfw_smpr_sc_ccb *c,union open_cfw_smpr_sc_message *m)
{
    struct open_cfw_smpr_sc_record *s=c->secure_connections;open_cfw_retained_cordio_calc128_copy(s->scratch->responder_random,m->aes.ciphertext);
    if(open_cfw_retained_iar_memcmp(s->scratch->peer_ca_or_ea,s->scratch->initiator_random,16U)==0){uint8_t n=c->pair_request[OPEN_CFW_SMPR_SC_PAIR_MAX_KEY]<c->pair_response[OPEN_CFW_SMPR_SC_PAIR_MAX_KEY]?c->pair_request[OPEN_CFW_SMPR_SC_PAIR_MAX_KEY]:c->pair_response[OPEN_CFW_SMPR_SC_PAIR_MAX_KEY];open_cfw_runtime_memory_zero(s->ltk->temporary_ltk+n,16U-n);c->key_ready=1U;open_cfw_cordio_smp_sc_send_dh_key_check(c,&m->header,s->scratch->responder_random);}
    else{struct open_cfw_smpr_sc_header h;h.param=c->connection_id;h.status=OPEN_CFW_SMPR_SC_ERROR_DH_CHECK;c->attempts++;open_cfw_cordio_smp_db_pairing_failed(c->connection_id);h.event=c->attempts==OPEN_CFW_SMPR_SC_CONFIG.maximum_attempts?OPEN_CFW_SMPR_SC_EVENT_MAX_ATTEMPTS:OPEN_CFW_SMPR_SC_EVENT_DH_FAILURE;open_cfw_retained_cordio_smp_state_machine_execute(c,&h);}
}
#endif
