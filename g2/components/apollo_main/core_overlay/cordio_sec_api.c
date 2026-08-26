/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Packetcraft Cordio r20.05c security-service compatibility implementation
 * for the G2 2.2.6.10 image. Cryptographic primitives remain controller/HCI
 * operations; this module owns queueing, CMAC framing, ECC byte order, and
 * completion dispatch.
 */

#include <stddef.h>
#include <stdint.h>

typedef uint8_t sec_u8;
typedef uint16_t sec_u16;
typedef uint32_t sec_u32;

typedef struct __attribute__((packed)) {
    sec_u16 param;
    sec_u8 event;
    sec_u8 status;
} sec_header;

typedef struct __attribute__((packed)) sec_queue_buf {
    sec_header header;
    uintptr_t ciphertext_pointer;
    uintptr_t plaintext_pointer;
    sec_u8 reserved0[4];
    sec_u8 ciphertext[16];
    sec_u8 reserved1[16];
    uintptr_t control_pointer;
    sec_u8 type;
    sec_u8 reserved2[3];
} sec_queue_buf;

typedef struct __attribute__((packed)) {
    uintptr_t plaintext_pointer;
    sec_u8 key[16];
    sec_u8 subkey[16];
    sec_u16 length;
    sec_u16 position;
    sec_u8 handler;
    sec_u8 state;
    sec_u8 reserved[2];
} sec_cmac_control;

typedef void (*sec_completion)(sec_queue_buf *, const sec_u8 *, sec_u8);

typedef struct __attribute__((packed)) {
    sec_u8 random[32];
    sec_u32 aes_queue[2];
    sec_u32 public_key_queue[2];
    sec_u32 dh_key_queue[2];
    sec_u8 token;
    sec_u8 random_top;
    sec_u8 random_bottom;
    sec_u8 reserved;
    sec_completion completion[3];
} sec_control;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(sec_queue_buf) == 56U, "Cordio secQueueBuf ABI");
_Static_assert(sizeof(sec_cmac_control) == 44U, "Cordio CMAC ABI");
_Static_assert(offsetof(sec_control, token) == 0x38U, "Cordio token ABI");
_Static_assert(offsetof(sec_control, completion) == 0x3CU, "Cordio callback ABI");
#endif

void *open_cfw_retained_cordio_sec_alloc(sec_u16);
void open_cfw_retained_cordio_sec_free(void *);
void open_cfw_retained_cordio_sec_enqueue(void *, sec_u8, void *);
void *open_cfw_retained_cordio_sec_dequeue(void *, sec_u8 *);
void open_cfw_retained_cordio_sec_send(sec_u8, void *);
void *open_cfw_retained_cordio_sec_memcpy(void *, const void *, sec_u32);
void *open_cfw_retained_cordio_sec_memset(void *, int, sec_u32);
void open_cfw_retained_cordio_sec_reverse(sec_u8 *, sec_u32);
void open_cfw_retained_cordio_sec_reverse_copy(sec_u8 *, const sec_u8 *, sec_u32);
void open_cfw_retained_cordio_sec_copy128(sec_u8 *, const sec_u8 *);
void open_cfw_retained_cordio_sec_xor128(sec_u8 *, const sec_u8 *);
void open_cfw_retained_cordio_sec_hci_register(void (*)(const sec_u8 *));
void open_cfw_retained_cordio_sec_hci_random(void);
void open_cfw_retained_cordio_sec_hci_encrypt(const sec_u8 *, const sec_u8 *);
void open_cfw_retained_cordio_sec_hci_public_key(void);
void open_cfw_retained_cordio_sec_hci_dh_key(const sec_u8 *, const sec_u8 *);

#ifndef OPEN_CFW_CORDIO_SEC_STATE
#define OPEN_CFW_CORDIO_SEC_STATE (*(volatile sec_control *)0x20072CB8U)
#endif

#define SEC_TYPE_AES 0U
#define SEC_TYPE_CMAC 1U
#define SEC_TYPE_DH 2U
#define SEC_TYPE_CCM 3U
#define SEC_TYPE_AES_REV 4U
#define SEC_CMAC_SUBKEY 0U
#define SEC_CMAC_BLOCK 1U
#define SEC_CMAC_COMPLETE 2U
#define SEC_TOKEN_INVALID 0xFFU
#define SEC_EVT_RESET 0x14U
#define SEC_EVT_ENCRYPT 0x1BU
#define SEC_EVT_RANDOM 0x1CU
#define SEC_EVT_PUBLIC_KEY 0x25U
#define SEC_EVT_DH_KEY 0x26U

#if defined(OPEN_CFW_CORDIO_SEC_HCI_CALLBACK_ONLY)
#define SEC_SELECTOR 1
#elif defined(OPEN_CFW_CORDIO_SEC_INIT_ONLY)
#define SEC_SELECTOR 2
#elif defined(OPEN_CFW_CORDIO_SEC_RANDOM_ONLY)
#define SEC_SELECTOR 3
#elif defined(OPEN_CFW_CORDIO_SEC_LE_ENCRYPT_ONLY)
#define SEC_SELECTOR 4
#elif defined(OPEN_CFW_CORDIO_SEC_NEXT_TOKEN_ONLY)
#define SEC_SELECTOR 5
#elif defined(OPEN_CFW_CORDIO_SEC_AES_ONLY)
#define SEC_SELECTOR 6
#elif defined(OPEN_CFW_CORDIO_SEC_AES_CALLBACK_ONLY)
#define SEC_SELECTOR 7
#elif defined(OPEN_CFW_CORDIO_SEC_AES_INIT_ONLY)
#define SEC_SELECTOR 8
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_BLOCK_ONLY)
#define SEC_SELECTOR 9
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_SUBKEY1_ONLY)
#define SEC_SELECTOR 10
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_SHIFT_ONLY)
#define SEC_SELECTOR 11
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_SUBKEY2_ONLY)
#define SEC_SELECTOR 12
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_COMPLETE_ONLY)
#define SEC_SELECTOR 13
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_CALLBACK_ONLY)
#define SEC_SELECTOR 14
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_ONLY)
#define SEC_SELECTOR 15
#elif defined(OPEN_CFW_CORDIO_SEC_CMAC_INIT_ONLY)
#define SEC_SELECTOR 16
#elif defined(OPEN_CFW_CORDIO_SEC_ECC_CALLBACK_ONLY)
#define SEC_SELECTOR 17
#elif defined(OPEN_CFW_CORDIO_SEC_ECC_KEY_ONLY)
#define SEC_SELECTOR 18
#elif defined(OPEN_CFW_CORDIO_SEC_ECC_SECRET_ONLY)
#define SEC_SELECTOR 19
#elif defined(OPEN_CFW_CORDIO_SEC_ECC_INIT_ONLY)
#define SEC_SELECTOR 20
#elif !defined(SEC_SELECTOR)
#define SEC_SELECTOR 0
#endif
#define SEC_BUILD(n) (SEC_SELECTOR == 0 || SEC_SELECTOR == (n))

void open_cfw_cordio_sec_hci_callback(const sec_u8 *event);
void open_cfw_cordio_sec_init(void);
void open_cfw_cordio_sec_random(sec_u8 *output, sec_u8 length);
void open_cfw_cordio_sec_le_encrypt(const sec_u8 *, const sec_u8 *, sec_queue_buf *, sec_u8);
sec_u8 open_cfw_cordio_sec_next_token(void);
sec_u8 open_cfw_cordio_sec_aes(const sec_u8 *, const sec_u8 *, sec_u8, sec_u16, sec_u8);
void open_cfw_cordio_sec_aes_callback(sec_queue_buf *, const sec_u8 *, sec_u8);
void open_cfw_cordio_sec_aes_init(void);
void open_cfw_cordio_sec_cmac_block(sec_queue_buf *);
void open_cfw_cordio_sec_cmac_subkey1(sec_queue_buf *);
sec_u8 open_cfw_cordio_sec_cmac_shift(sec_u8 *, sec_u8);
void open_cfw_cordio_sec_cmac_subkey2(sec_queue_buf *);
void open_cfw_cordio_sec_cmac_complete(sec_queue_buf *);
void open_cfw_cordio_sec_cmac_callback(sec_queue_buf *, const sec_u8 *, sec_u8);
sec_u8 open_cfw_cordio_sec_cmac(const sec_u8 *, sec_u8 *, sec_u16, sec_u8, sec_u16, sec_u8);
void open_cfw_cordio_sec_cmac_init(void);
void open_cfw_cordio_sec_ecc_callback(sec_queue_buf *, const sec_u8 *, sec_u8);
sec_u8 open_cfw_cordio_sec_ecc_key(sec_u8, sec_u16, sec_u8);
sec_u8 open_cfw_cordio_sec_ecc_secret(const sec_u8 *, sec_u8, sec_u16, sec_u8);
void open_cfw_cordio_sec_ecc_init(void);

#if defined(__arm__) || defined(__thumb__)
__asm__(
 ".type open_cfw_cordio_sec_hci_callback,%function\n"
 ".type open_cfw_cordio_sec_init,%function\n"
 ".type open_cfw_cordio_sec_random,%function\n"
 ".type open_cfw_cordio_sec_le_encrypt,%function\n"
 ".type open_cfw_cordio_sec_next_token,%function\n"
 ".type open_cfw_cordio_sec_aes,%function\n"
 ".type open_cfw_cordio_sec_aes_callback,%function\n"
 ".type open_cfw_cordio_sec_aes_init,%function\n"
 ".type open_cfw_cordio_sec_cmac_block,%function\n"
 ".type open_cfw_cordio_sec_cmac_subkey1,%function\n"
 ".type open_cfw_cordio_sec_cmac_shift,%function\n"
 ".type open_cfw_cordio_sec_cmac_subkey2,%function\n"
 ".type open_cfw_cordio_sec_cmac_complete,%function\n"
 ".type open_cfw_cordio_sec_cmac_callback,%function\n"
 ".type open_cfw_cordio_sec_cmac,%function\n"
 ".type open_cfw_cordio_sec_cmac_init,%function\n"
 ".type open_cfw_cordio_sec_ecc_callback,%function\n"
 ".type open_cfw_cordio_sec_ecc_key,%function\n"
 ".type open_cfw_cordio_sec_ecc_secret,%function\n"
 ".type open_cfw_cordio_sec_ecc_init,%function\n"
);
#endif

#if SEC_BUILD(1)
__attribute__((used,noinline)) void open_cfw_cordio_sec_hci_callback(const sec_u8 *event)
{
    sec_queue_buf *buffer = NULL; sec_u8 handler = 0U; sec_u8 kind = event[2];
    if (kind == SEC_EVT_RESET) {
        while ((buffer = open_cfw_retained_cordio_sec_dequeue((void *)OPEN_CFW_CORDIO_SEC_STATE.public_key_queue,&handler)) != NULL) open_cfw_retained_cordio_sec_free(buffer);
        while ((buffer = open_cfw_retained_cordio_sec_dequeue((void *)OPEN_CFW_CORDIO_SEC_STATE.dh_key_queue,&handler)) != NULL) open_cfw_retained_cordio_sec_free(buffer);
        while ((buffer = open_cfw_retained_cordio_sec_dequeue((void *)OPEN_CFW_CORDIO_SEC_STATE.aes_queue,&handler)) != NULL) open_cfw_retained_cordio_sec_free(buffer);
        return;
    }
    if (kind == SEC_EVT_RANDOM) {
        open_cfw_retained_cordio_sec_memcpy((void *)&OPEN_CFW_CORDIO_SEC_STATE.random[OPEN_CFW_CORDIO_SEC_STATE.random_top * 8U],event+5,8U);
        OPEN_CFW_CORDIO_SEC_STATE.random_top = OPEN_CFW_CORDIO_SEC_STATE.random_top >= 3U ? 0U : (sec_u8)(OPEN_CFW_CORDIO_SEC_STATE.random_top+1U);
        return;
    }
    if (kind == SEC_EVT_ENCRYPT) {
        buffer=open_cfw_retained_cordio_sec_dequeue((void *)OPEN_CFW_CORDIO_SEC_STATE.aes_queue,&handler);
        if (buffer != NULL && (buffer->type==SEC_TYPE_CCM || buffer->type==SEC_TYPE_CMAC || buffer->type==SEC_TYPE_AES_REV)) open_cfw_retained_cordio_sec_reverse((sec_u8 *)event+5,16U);
    } else if (kind == SEC_EVT_PUBLIC_KEY) buffer=open_cfw_retained_cordio_sec_dequeue((void *)OPEN_CFW_CORDIO_SEC_STATE.public_key_queue,&handler);
    else if (kind == SEC_EVT_DH_KEY) buffer=open_cfw_retained_cordio_sec_dequeue((void *)OPEN_CFW_CORDIO_SEC_STATE.dh_key_queue,&handler);
    if (buffer != NULL && buffer->type < 3U && OPEN_CFW_CORDIO_SEC_STATE.completion[buffer->type] != NULL) OPEN_CFW_CORDIO_SEC_STATE.completion[buffer->type](buffer,event,handler);
}
#endif

#if SEC_BUILD(2)
__attribute__((used,noinline)) void open_cfw_cordio_sec_init(void)
{
    open_cfw_retained_cordio_sec_memset((void *)OPEN_CFW_CORDIO_SEC_STATE.aes_queue,0,24U);
    OPEN_CFW_CORDIO_SEC_STATE.token=0U;
    open_cfw_retained_cordio_sec_hci_register(open_cfw_cordio_sec_hci_callback);
}
#endif

#if SEC_BUILD(3)
__attribute__((used,noinline)) void open_cfw_cordio_sec_random(sec_u8 *output,sec_u8 length)
{
    sec_u8 index=(sec_u8)(OPEN_CFW_CORDIO_SEC_STATE.random_bottom*8U); sec_u8 count=(sec_u8)((length+7U)/8U);
    while(length-- != 0U){*output++=OPEN_CFW_CORDIO_SEC_STATE.random[index];index=index==31U?0U:(sec_u8)(index+1U);}
    while(count-- != 0U){open_cfw_retained_cordio_sec_hci_random();OPEN_CFW_CORDIO_SEC_STATE.random_bottom=OPEN_CFW_CORDIO_SEC_STATE.random_bottom>=3U?0U:(sec_u8)(OPEN_CFW_CORDIO_SEC_STATE.random_bottom+1U);}
}
#endif

#if SEC_BUILD(4)
__attribute__((used,noinline)) void open_cfw_cordio_sec_le_encrypt(const sec_u8 *key,const sec_u8 *text,sec_queue_buf *buffer,sec_u8 handler)
{sec_u8 rk[16],rt[16];open_cfw_retained_cordio_sec_reverse_copy(rk,key,16U);open_cfw_retained_cordio_sec_reverse_copy(rt,text,16U);open_cfw_retained_cordio_sec_enqueue((void *)OPEN_CFW_CORDIO_SEC_STATE.aes_queue,handler,buffer);open_cfw_retained_cordio_sec_hci_encrypt(rk,rt);}
#endif

#if SEC_BUILD(5)
__attribute__((used,noinline)) sec_u8 open_cfw_cordio_sec_next_token(void)
{sec_u8 token=OPEN_CFW_CORDIO_SEC_STATE.token++;if(token==SEC_TOKEN_INVALID)token=OPEN_CFW_CORDIO_SEC_STATE.token++;return token;}
#endif

#if SEC_BUILD(6)
__attribute__((used,noinline)) sec_u8 open_cfw_cordio_sec_aes(const sec_u8 *key,const sec_u8 *text,sec_u8 handler,sec_u16 param,sec_u8 event)
{sec_queue_buf *b=open_cfw_retained_cordio_sec_alloc((sec_u16)sizeof(*b));if(!b)return SEC_TOKEN_INVALID;b->header.status=open_cfw_cordio_sec_next_token();b->header.param=param;b->header.event=event;b->type=SEC_TYPE_AES;open_cfw_retained_cordio_sec_enqueue((void *)OPEN_CFW_CORDIO_SEC_STATE.aes_queue,handler,b);open_cfw_retained_cordio_sec_hci_encrypt(key,text);return b->header.status;}
#endif

#if SEC_BUILD(7)
__attribute__((used,noinline)) void open_cfw_cordio_sec_aes_callback(sec_queue_buf *b,const sec_u8 *event,sec_u8 handler)
{b->ciphertext_pointer=(uintptr_t)b->ciphertext;open_cfw_retained_cordio_sec_copy128(b->ciphertext,event+5);open_cfw_retained_cordio_sec_send(handler,b);}
#endif

#if SEC_BUILD(8)
__attribute__((used,noinline)) void open_cfw_cordio_sec_aes_init(void){OPEN_CFW_CORDIO_SEC_STATE.completion[SEC_TYPE_AES]=open_cfw_cordio_sec_aes_callback;}
#endif

#if SEC_BUILD(9)
__attribute__((used,noinline)) void open_cfw_cordio_sec_cmac_block(sec_queue_buf *b)
{sec_cmac_control *c=(sec_cmac_control *)(uintptr_t)b->control_pointer;sec_u8 text[16];int remaining=(int)c->length-(int)c->position;sec_u8 *p=(sec_u8 *)(uintptr_t)c->plaintext_pointer+c->position;if(remaining<=16){open_cfw_retained_cordio_sec_memcpy(text,p,(sec_u32)remaining);if(remaining!=16){open_cfw_retained_cordio_sec_memset(text+remaining,0,(sec_u32)(16-remaining));text[remaining]=0x80U;}open_cfw_retained_cordio_sec_xor128(text,c->subkey);c->state=SEC_CMAC_COMPLETE;}else open_cfw_retained_cordio_sec_copy128(text,p);if(c->position!=0U)open_cfw_retained_cordio_sec_xor128(text,b->ciphertext);c->position=(sec_u16)(c->position+16U);open_cfw_cordio_sec_le_encrypt(c->key,text,b,c->handler);}
#endif

#if SEC_BUILD(10)
__attribute__((used,noinline)) void open_cfw_cordio_sec_cmac_subkey1(sec_queue_buf *b)
{sec_cmac_control *c=(sec_cmac_control *)(uintptr_t)b->control_pointer;sec_u8 zero[16];open_cfw_retained_cordio_sec_memset(zero,0,16U);open_cfw_cordio_sec_le_encrypt(c->key,zero,b,c->handler);}
#endif

#if SEC_BUILD(11)
__attribute__((used,noinline)) sec_u8 open_cfw_cordio_sec_cmac_shift(sec_u8 *p,sec_u8 shift)
{sec_u8 out=(sec_u8)(p[0]>>(8U-shift));sec_u8 i;for(i=0U;i<16U;++i){sec_u8 next=i<15U?(sec_u8)(p[i+1U]>>(8U-shift)):0U;p[i]=(sec_u8)((p[i]<<shift)|next);}return out;}
#endif

#if SEC_BUILD(12)
__attribute__((used,noinline)) void open_cfw_cordio_sec_cmac_subkey2(sec_queue_buf *b)
{sec_cmac_control *c=(sec_cmac_control *)(uintptr_t)b->control_pointer;open_cfw_retained_cordio_sec_copy128(c->subkey,b->ciphertext);if(open_cfw_cordio_sec_cmac_shift(c->subkey,1U))c->subkey[15]^=0x87U;if((c->length&15U)!=0U&&open_cfw_cordio_sec_cmac_shift(c->subkey,1U))c->subkey[15]^=0x87U;c->state=SEC_CMAC_BLOCK;open_cfw_cordio_sec_cmac_block(b);}
#endif

#if SEC_BUILD(13)
__attribute__((used,noinline)) void open_cfw_cordio_sec_cmac_complete(sec_queue_buf *b)
{sec_cmac_control *c=(sec_cmac_control *)(uintptr_t)b->control_pointer;b->ciphertext_pointer=(uintptr_t)b->ciphertext;b->plaintext_pointer=c->plaintext_pointer;open_cfw_retained_cordio_sec_send(c->handler,b);}
#endif

#if SEC_BUILD(14)
__attribute__((used,noinline)) void open_cfw_cordio_sec_cmac_callback(sec_queue_buf *b,const sec_u8 *event,sec_u8 handler)
{sec_cmac_control *c=(sec_cmac_control *)(uintptr_t)b->control_pointer;(void)handler;if(c){open_cfw_retained_cordio_sec_copy128(b->ciphertext,event+5);if(c->state==SEC_CMAC_SUBKEY)open_cfw_cordio_sec_cmac_subkey2(b);else if(c->state==SEC_CMAC_BLOCK)open_cfw_cordio_sec_cmac_block(b);else if(c->state==SEC_CMAC_COMPLETE)open_cfw_cordio_sec_cmac_complete(b);}}
#endif

#if SEC_BUILD(15)
__attribute__((used,noinline)) sec_u8 open_cfw_cordio_sec_cmac(const sec_u8 *key,sec_u8 *text,sec_u16 length,sec_u8 handler,sec_u16 param,sec_u8 event)
{sec_queue_buf *b=open_cfw_retained_cordio_sec_alloc((sec_u16)(sizeof(*b)+sizeof(sec_cmac_control)));sec_cmac_control *c;if(!b)return 0U;c=(sec_cmac_control *)(b+1);b->control_pointer=(uintptr_t)c;b->type=SEC_TYPE_CMAC;b->header.status=OPEN_CFW_CORDIO_SEC_STATE.token++;b->header.param=param;b->header.event=event;c->plaintext_pointer=(uintptr_t)text;c->length=length;c->position=0U;c->handler=handler;c->state=SEC_CMAC_SUBKEY;open_cfw_retained_cordio_sec_copy128(c->key,key);open_cfw_cordio_sec_cmac_subkey1(b);return 1U;}
#endif

#if SEC_BUILD(16)
__attribute__((used,noinline)) void open_cfw_cordio_sec_cmac_init(void){OPEN_CFW_CORDIO_SEC_STATE.completion[SEC_TYPE_CMAC]=open_cfw_cordio_sec_cmac_callback;}
#endif

#if SEC_BUILD(17)
__attribute__((used,noinline)) void open_cfw_cordio_sec_ecc_callback(sec_queue_buf *b,const sec_u8 *event,sec_u8 handler)
{if(event[2]==SEC_EVT_PUBLIC_KEY){open_cfw_retained_cordio_sec_reverse_copy((sec_u8 *)b+4,event+5,32U);open_cfw_retained_cordio_sec_reverse_copy((sec_u8 *)b+36,event+37,32U);b->header.status=event[4];open_cfw_retained_cordio_sec_send(handler,b);}else if(event[2]==SEC_EVT_DH_KEY){if(event[3]==0x12U)b->header.status=0x12U;else{open_cfw_retained_cordio_sec_reverse_copy((sec_u8 *)b+4,event+5,32U);b->header.status=event[4];}open_cfw_retained_cordio_sec_send(handler,b);}}
#endif

#if SEC_BUILD(18)
__attribute__((used,noinline)) sec_u8 open_cfw_cordio_sec_ecc_key(sec_u8 handler,sec_u16 param,sec_u8 event)
{sec_queue_buf *b=open_cfw_retained_cordio_sec_alloc(156U);if(!b)return 0U;b->header.param=param;b->header.event=event;b->type=SEC_TYPE_DH;open_cfw_retained_cordio_sec_enqueue((void *)OPEN_CFW_CORDIO_SEC_STATE.public_key_queue,handler,b);open_cfw_retained_cordio_sec_hci_public_key();return 1U;}
#endif

#if SEC_BUILD(19)
__attribute__((used,noinline)) sec_u8 open_cfw_cordio_sec_ecc_secret(const sec_u8 *key,sec_u8 handler,sec_u16 param,sec_u8 event)
{sec_queue_buf *b=open_cfw_retained_cordio_sec_alloc(156U);sec_u8 x[32],y[32];if(!b)return 0U;b->header.param=param;b->header.event=event;b->type=SEC_TYPE_DH;open_cfw_retained_cordio_sec_enqueue((void *)OPEN_CFW_CORDIO_SEC_STATE.dh_key_queue,handler,b);open_cfw_retained_cordio_sec_reverse_copy(x,key,32U);open_cfw_retained_cordio_sec_reverse_copy(y,key+32,32U);open_cfw_retained_cordio_sec_hci_dh_key(x,y);return 1U;}
#endif

#if SEC_BUILD(20)
__attribute__((used,noinline)) void open_cfw_cordio_sec_ecc_init(void){OPEN_CFW_CORDIO_SEC_STATE.completion[SEC_TYPE_DH]=open_cfw_cordio_sec_ecc_callback;}
#endif
