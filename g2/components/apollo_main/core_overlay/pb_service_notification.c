/* SPDX-License-Identifier: GPL-3.0-only
 * Clean-room implementation of the nine linked G2 pb_service_notification.c
 * entries. Diagnostic-only logging/assertions are omitted.
 */
#include <stdint.h>

typedef struct { void *callback; void *state; uint32_t bytes_left; const char *error; }
    open_cfw_pb_notification_input;
struct open_cfw_pb_notification_output;
typedef uint32_t (*open_cfw_pb_notification_write_fn)(
    struct open_cfw_pb_notification_output *, const void *, uint32_t);
typedef struct open_cfw_pb_notification_output {
    open_cfw_pb_notification_write_fn write;
    void *context;
    uint32_t capacity;
    uint32_t length;
    const char *error;
} open_cfw_pb_notification_output;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(open_cfw_pb_notification_input) == 16U, "input ABI");
_Static_assert(sizeof(open_cfw_pb_notification_output) == 20U, "output ABI");
#endif

#ifndef OPEN_CFW_PB_NOTIFICATION_DECODED_MESSAGE
#define OPEN_CFW_PB_NOTIFICATION_DECODED_MESSAGE ((uint8_t *)(uintptr_t)0x200F60E0U)
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_MESSAGE
#define OPEN_CFW_PB_NOTIFICATION_MESSAGE ((uint8_t *)(uintptr_t)0x200F60E0U)
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_ENCODE_BUFFER
#define OPEN_CFW_PB_NOTIFICATION_ENCODE_BUFFER ((uint8_t *)(uintptr_t)0x2037C7A0U)
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR
#define OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR ((const void *)(uintptr_t)0x007799F4U)
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_INPUT_FROM_BUFFER
open_cfw_pb_notification_input open_cfw_nanopb_istream_from_buffer(const void *, uint32_t);
#define OPEN_CFW_PB_NOTIFICATION_INPUT_FROM_BUFFER(d,n) open_cfw_nanopb_istream_from_buffer((d),(n))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_DECODE
uint32_t open_cfw_nanopb_decode(open_cfw_pb_notification_input *, const void *, void *);
#define OPEN_CFW_PB_NOTIFICATION_DECODE(i,d,m) open_cfw_nanopb_decode((i),(d),(m))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_ENCODE
uint32_t open_cfw_format_message_encode(void *, const void *, const void *);
#define OPEN_CFW_PB_NOTIFICATION_ENCODE(o,d,m) open_cfw_format_message_encode((o),(d),(m))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_SEND
int open_cfw_ble_msgtx_pb_send(uint32_t,uint32_t,const void *,uint32_t);
#define OPEN_CFW_PB_NOTIFICATION_SEND(r,s,d,n) open_cfw_ble_msgtx_pb_send((r),(s),(d),(n))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_NOTIFY
int open_cfw_ble_msgtx_pb_notify(uint32_t,uint32_t,const void *,uint32_t);
#define OPEN_CFW_PB_NOTIFICATION_NOTIFY(r,s,d,n) open_cfw_ble_msgtx_pb_notify((r),(s),(d),(n))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE
uint8_t *open_cfw_pb_notification_control_state(void);
#define OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE() open_cfw_pb_notification_control_state()
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_SET_WHITELIST_DISABLED
void open_cfw_pb_notification_set_whitelist_disabled(uint32_t);
#define OPEN_CFW_PB_NOTIFICATION_SET_WHITELIST_DISABLED(v) open_cfw_pb_notification_set_whitelist_disabled((v))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_READ_WHITELIST_CRC
int open_cfw_pb_notification_read_whitelist_crc(uint32_t *);
#define OPEN_CFW_PB_NOTIFICATION_READ_WHITELIST_CRC(p) open_cfw_pb_notification_read_whitelist_crc((p))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_ALLOC
void *open_cfw_heap_alloc(uint32_t);
#define OPEN_CFW_PB_NOTIFICATION_ALLOC(n) open_cfw_heap_alloc((n))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_FREE
void open_cfw_heap_free(void *);
#define OPEN_CFW_PB_NOTIFICATION_FREE(p) open_cfw_heap_free((p))
#endif
#ifndef OPEN_CFW_PB_NOTIFICATION_TICK
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_PB_NOTIFICATION_TICK() open_cfw_cmsis_kernel_get_tick_count()
#endif

#if defined(OPEN_CFW_PB_NOTIFICATION_BUFFER_WRITE_ONLY)
#define INC_BUFFER 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_ZERO_ONLY)
#define INC_ZERO 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_ENCODE_ONLY)
#define INC_ENCODE 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_DISPATCH_ONLY)
#define INC_DISPATCH 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_RX_CTRL_ONLY)
#define INC_RX_CTRL 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_TX_CTRL_ONLY)
#define INC_TX_CTRL 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_TX_COMM_RESP_ONLY)
#define INC_TX_COMM_RESP 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_NOTIFY_APP_ONLY)
#define INC_NOTIFY_APP 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_RX_WHITELIST_CTRL_ONLY)
#define INC_RX_WHITELIST_CTRL 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_TX_WHITELIST_CTRL_ONLY)
#define INC_TX_WHITELIST_CTRL 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_RX_WHITELIST_CHECK_ONLY)
#define INC_RX_WHITELIST_CHECK 1
#elif defined(OPEN_CFW_PB_NOTIFICATION_TX_WHITELIST_CHECK_ONLY)
#define INC_TX_WHITELIST_CHECK 1
#else
#define INC_BUFFER 1
#define INC_ZERO 1
#define INC_ENCODE 1
#define INC_DISPATCH 1
#define INC_RX_CTRL 1
#define INC_TX_CTRL 1
#define INC_TX_COMM_RESP 1
#define INC_NOTIFY_APP 1
#define INC_RX_WHITELIST_CTRL 1
#define INC_TX_WHITELIST_CTRL 1
#define INC_RX_WHITELIST_CHECK 1
#define INC_TX_WHITELIST_CHECK 1
#endif

uint32_t open_cfw_pb_service_notification_buffer_write(open_cfw_pb_notification_output *,const void *,uint32_t);
void open_cfw_pb_service_notification_zero(void *,uint32_t);
uint32_t open_cfw_pb_notification_encode_and_send(uint32_t,uint32_t,const void *);
uint32_t PB_RxNotifCtrl(uint32_t,const void *);
uint32_t APP_PbTxEncodeNotifCtrl(uint32_t,const void *);
uint32_t APP_PbTxEncodeNotifCommResp(uint32_t,const void *);
uint32_t APP_PbTxEncodeNotifAppIDNotInWhitelist(const char *,const char *);
uint32_t PB_RxNotifWhitelistCtrl(uint32_t,const void *);
uint32_t APP_PbTxEncodeNotifWhitelistCtrl(uint32_t,const void *);
uint32_t PB_RxNotifWhitelistChk(uint32_t,const void *);
uint32_t APP_PbTxEncodeNotifWhitelistChk(uint32_t,const void *);

#if defined(INC_BUFFER)
__attribute__((used,noinline)) uint32_t open_cfw_pb_service_notification_buffer_write(
    open_cfw_pb_notification_output *o,const void *raw,uint32_t n) {
    const uint8_t *s=(const uint8_t *)raw; uint8_t *d=(uint8_t *)o->context; uint32_t i;
    if(o->length>o->capacity || n>o->capacity-o->length) return 0U;
    for(i=0;i<n;i++) d[o->length+i]=s[i]; return 1U;
}
#endif
#if defined(INC_ZERO)
__attribute__((used,noinline)) void open_cfw_pb_service_notification_zero(void *raw,uint32_t n) {
    uint8_t *p=(uint8_t *)raw; uint32_t i; for(i=0;i<n;i++) p[i]=0U;
}
#endif
static __attribute__((always_inline,unused)) inline void store16(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static __attribute__((always_inline,unused)) inline void store32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
static __attribute__((always_inline,unused)) inline uint32_t load32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}

#if defined(INC_ENCODE)
__attribute__((used,noinline)) uint32_t open_cfw_pb_notification_encode_and_send(
    uint32_t command,uint32_t magic,const void *raw) {
    const uint8_t *p=(const uint8_t *)raw; uint8_t *m=OPEN_CFW_PB_NOTIFICATION_MESSAGE;
    open_cfw_pb_notification_output o; uint32_t local_crc=0U; int valid;
    if(p==0) return 2U;
    open_cfw_pb_service_notification_zero(m,0x4cU); m[0]=(uint8_t)command; m[1]=(uint8_t)magic;
    if(command==1U){store16(m+2U,3U);m[4]=p[0];m[5]=p[1];m[6]=p[2];m[8]=p[4];}
    else if(command==0xa1U){store16(m+2U,5U);m[4]=p[0];m[5]=p[1];}
    else if(command==3U){store16(m+2U,6U);m[4]=p[0];}
    else {store16(m+2U,7U);valid=OPEN_CFW_PB_NOTIFICATION_READ_WHITELIST_CRC(&local_crc);store32(m+4U,local_crc);if(valid==0){m[8]=1U;m[9]=7U;}else{m[8]=(load32(p)==local_crc)?2U:3U;m[9]=0U;}}
    o.write=open_cfw_pb_service_notification_buffer_write;o.context=OPEN_CFW_PB_NOTIFICATION_ENCODE_BUFFER;
    o.capacity=0x100U;o.length=0U;o.error=0;
    if(OPEN_CFW_PB_NOTIFICATION_ENCODE(&o,OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR,m)==0U) return 0x2bU;
    OPEN_CFW_PB_NOTIFICATION_SEND(1U,4U,OPEN_CFW_PB_NOTIFICATION_ENCODE_BUFFER,o.length&0xffffU);return 0U;
}
#endif
#if defined(INC_RX_CTRL)
__attribute__((used,noinline)) uint32_t PB_RxNotifCtrl(uint32_t magic,const void *raw){const uint8_t *p=(const uint8_t *)raw;uint8_t *s;(void)magic;if(!p)return 2U;s=OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE();s[0]=p[0];s=OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE();s[1]=p[1];s=OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE();s[2]=p[2];s=OPEN_CFW_PB_NOTIFICATION_CONTROL_STATE();s[3]=p[4];return 0U;}
#endif
#if defined(INC_TX_CTRL)
__attribute__((used,noinline)) uint32_t APP_PbTxEncodeNotifCtrl(uint32_t magic,const void *p){return open_cfw_pb_notification_encode_and_send(1U,magic,p);}
#endif
#if defined(INC_TX_COMM_RESP)
__attribute__((used,noinline)) uint32_t APP_PbTxEncodeNotifCommResp(uint32_t magic,const void *p){return open_cfw_pb_notification_encode_and_send(0xa1U,magic,p);}
#endif
#if defined(INC_NOTIFY_APP)
__attribute__((used,noinline)) uint32_t APP_PbTxEncodeNotifAppIDNotInWhitelist(const char *a,const char *b){
    uint8_t *block,*m;open_cfw_pb_notification_output o;uint32_t i,n;int sent;
    block=(uint8_t *)OPEN_CFW_PB_NOTIFICATION_ALLOC(0x9cU);if(!block)return 2U;
    open_cfw_pb_service_notification_zero(block,0x9cU);m=block+0x4eU;m[0]=2U;m[1]=(uint8_t)OPEN_CFW_PB_NOTIFICATION_TICK();store16(m+2U,4U);
    n=0U;while(a[n]!=0 && n<31U)n++;store16(m+4U,n+1U);for(i=0;i<n;i++)m[6U+i]=(uint8_t)a[i];m[6U+n]=0U;
    n=0U;while(b[n]!=0 && n<31U)n++;store16(m+38U,n+1U);for(i=0;i<n;i++)m[40U+i]=(uint8_t)b[i];m[40U+n]=0U;m[72]=0U;
    o.write=open_cfw_pb_service_notification_buffer_write;o.context=block;o.capacity=0x4eU;o.length=0U;o.error=0;
    if(OPEN_CFW_PB_NOTIFICATION_ENCODE(&o,OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR,m)==0U){OPEN_CFW_PB_NOTIFICATION_FREE(block);return 0x2bU;}
    sent=OPEN_CFW_PB_NOTIFICATION_NOTIFY(1U,4U,block,o.length&0xffffU);OPEN_CFW_PB_NOTIFICATION_FREE(block);return sent==0?0U:0xffffffffU;
}
#endif
#if defined(INC_RX_WHITELIST_CTRL)
__attribute__((used,noinline)) uint32_t PB_RxNotifWhitelistCtrl(uint32_t magic,const void *raw){const uint8_t *p=(const uint8_t *)raw;(void)magic;if(!p)return 2U;OPEN_CFW_PB_NOTIFICATION_SET_WHITELIST_DISABLED(p[0]!=0U);return 0U;}
#endif
#if defined(INC_TX_WHITELIST_CTRL)
__attribute__((used,noinline)) uint32_t APP_PbTxEncodeNotifWhitelistCtrl(uint32_t magic,const void *p){return open_cfw_pb_notification_encode_and_send(3U,magic,p);}
#endif
#if defined(INC_RX_WHITELIST_CHECK)
__attribute__((used,noinline)) uint32_t PB_RxNotifWhitelistChk(uint32_t magic,const void *p){(void)magic;return p?0U:2U;}
#endif
#if defined(INC_TX_WHITELIST_CHECK)
__attribute__((used,noinline)) uint32_t APP_PbTxEncodeNotifWhitelistChk(uint32_t magic,const void *p){return open_cfw_pb_notification_encode_and_send(4U,magic,p);}
#endif
#if defined(INC_DISPATCH)
__attribute__((used,noinline)) uint32_t APP_PbRxNotificationFrameDataProcess(const void *data,uint32_t length){
    uint8_t decoded_message[0x4c];uint8_t *m=decoded_message;open_cfw_pb_notification_input in;uint8_t resp[2];uint32_t r;
    if(!data)return 2U;open_cfw_pb_service_notification_zero(m,0x4cU);in=OPEN_CFW_PB_NOTIFICATION_INPUT_FROM_BUFFER(data,length);
    if(OPEN_CFW_PB_NOTIFICATION_DECODE(&in,OPEN_CFW_PB_NOTIFICATION_DESCRIPTOR,m)==0U)return 0x2bU;
    if(m[0]==1U){r=PB_RxNotifCtrl(m[1],m+4U);if(r==0U)return APP_PbTxEncodeNotifCtrl(m[1],m+4U);}
    else if(m[0]==3U){r=PB_RxNotifWhitelistCtrl(m[1],m+4U);if(r==0U)return APP_PbTxEncodeNotifWhitelistCtrl(m[1],m+4U);}
    else if(m[0]==4U){r=PB_RxNotifWhitelistChk(m[1],m+4U);if(r==0U)return APP_PbTxEncodeNotifWhitelistChk(m[1],m+4U);}
    else {resp[0]=m[0];resp[1]=8U;(void)APP_PbTxEncodeNotifCommResp(m[1],resp);}return 0U;
}
#endif
