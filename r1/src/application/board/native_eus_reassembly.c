/* Stock0x32198 transport policy, with explicit C capacity admission.
 * Valid frames retain the native global-stream/retry/CRC behavior. */
#include <stdint.h>
#include <stddef.h>
#include "native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"
#include "../../include/r1_eus_transport.h"
extern void *pvPortMalloc(uint32_t);
extern void vPortFree(void *);
extern void *memmove(void *,const void *,size_t);
extern volatile uintptr_t r1_fragment_send_callback;
extern uint32_t r1_bae8_bc_rx_enqueue(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *),nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
struct r1_eus_rx_state {uint8_t counter,reserved;uint16_t wire_length;uint8_t *buffer;uint32_t used;};
_Static_assert(sizeof(struct r1_eus_rx_state)==12 && offsetof(struct r1_eus_rx_state,used)==8,"native receive prefix");
volatile struct r1_eus_rx_state r1_eus_reassembly_state __attribute__((section(".r1.eus.reassembly.state"),aligned(4)))={0};
/* Native scratch base0x20019c48.478 holds two239-byte payload fragments
 * when the initial counter is1; no claim about the original allocation size. */
uint8_t r1_eus_reassembly_scratch[R1_EUS_STATIC_CAPACITY] __attribute__((section(".bss.r1.eus.reassembly.scratch"),aligned(4)))={0};
volatile uintptr_t r1_eus_rx_complete_callback __attribute__((section(".r1.eus.reassembly.receive")))=(uintptr_t)&r1_bae8_bc_rx_enqueue;
/* New C-only safety metadata; it has no claimed native address. */
static uint32_t r1_eus_reassembly_capacity;
#define RING(marker,text,...) do {if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) (void)r1_structured_log_format(marker,text,text,##__VA_ARGS__);}while(0)
static const char text_32348[]="[pb.tran]length is too short =%d\r\n";
static const char text_3236c[]="length is too short =%d\r\n";
static const char text_32390[]="[pb.tran]PACKET TO LARGE =%d\r\n";
static const char text_323b0[]="PACKET TO LARGE =%d\r\n";
static const char text_323c8[]="[pb.tran]p_protocol_buf == NULL\r\n";
static const char text_323ec[]="p_protocol_buf == NULL\r\n";

static uint32_t abandon(void)
{
 uint8_t *buffer=r1_eus_reassembly_state.buffer;
 if(buffer && buffer!=r1_eus_reassembly_scratch)vPortFree(buffer);
 r1_eus_reassembly_state.buffer=0;r1_eus_reassembly_state.used=0;
 r1_eus_reassembly_state.counter=0;r1_eus_reassembly_state.wire_length=0;
 r1_eus_reassembly_capacity=0;return UINT32_MAX;
}
uint32_t r1_eus_rx_reassembly(uint32_t connection,uint32_t channel,const void *packet,uint32_t length)
{
 const volatile uint8_t *data=packet;
 if(length<R1_EUS_HEADER_SIZE){
  RING(0x04400000,text_32348,length);
  if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001,text_3236c,length);
  return UINT32_MAX;
 }
 /* New admission: the native239-byte fragments never need larger writes. */
 if(!data || length>R1_EUS_MAX_WIRE_SIZE)return UINT32_MAX;
 if(!r1_eus_reassembly_state.buffer && data[0]){
  uint32_t counter=data[0];r1_eus_reassembly_state.used=0;
  if(counter>R1_EUS_MAX_COUNTER){
   RING(0x04400000,text_32390,data[0]);
   if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0001,text_323b0,data[0]);
   return UINT32_MAX;
  }
  if(counter==1){r1_eus_reassembly_state.buffer=r1_eus_reassembly_scratch;r1_eus_reassembly_capacity=R1_EUS_STATIC_CAPACITY;}
  else{
   r1_eus_reassembly_capacity=(counter+1u)*R1_EUS_FRAGMENT_PAYLOAD;
   if(r1_eus_reassembly_capacity>R1_EUS_MAX_MESSAGE_SIZE)r1_eus_reassembly_capacity=R1_EUS_MAX_MESSAGE_SIZE;
   r1_eus_reassembly_state.buffer=pvPortMalloc(r1_eus_reassembly_capacity);
   if(!r1_eus_reassembly_state.buffer){
    r1_eus_reassembly_capacity=0;
    RING(0x04000000,text_323c8);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0001,text_323ec);
    return UINT32_MAX;
   }
  }
 }
 if(r1_eus_reassembly_state.buffer){
  uint32_t used=r1_eus_reassembly_state.used;
  if(r1_eus_reassembly_state.counter && data[0]==r1_eus_reassembly_state.counter){
   uint32_t previous=r1_eus_reassembly_state.wire_length;
   if(previous<5 || used<previous-5u)return abandon();
   used=used-previous+5u;r1_eus_reassembly_state.used=used;
  }
  if(used>r1_eus_reassembly_capacity || length-5u>r1_eus_reassembly_capacity-used)return abandon();
  (void)memmove(r1_eus_reassembly_state.buffer+used,(const void *)(uintptr_t)(data+5),length-5u);
  r1_eus_reassembly_state.used+=length-5u;
  r1_eus_reassembly_state.counter=data[0];r1_eus_reassembly_state.wire_length=(uint16_t)length;
 }
 if(data[0])return 0;
 uint32_t expected=read32(data+1);
 r1_eus_reassembly_state.wire_length=0;r1_eus_reassembly_state.counter=0;
 const uint8_t *message=r1_eus_reassembly_state.buffer;
 uint32_t size=(uint16_t)r1_eus_reassembly_state.used;
 if(!message){message=(const uint8_t *)packet+5;size=(uint16_t)(length-5u);}
 uint32_t computed=0;r1_stock_crc32_update(message,size,&computed);
 if(computed!=expected){
  uintptr_t callback=r1_fragment_send_callback;
  if(callback){
   r1_eus_reassembly_scratch[0]=0;
   /* Native copies message+1 as a word. For short malformed messages,
    * zero unavailable bytes instead of reading beyond the logical payload. */
   uint32_t reference=0;
   for(uint32_t i=0;i<4 && i+1u<size;i++)reference|=(uint32_t)message[i+1u]<<(8u*i);
   write32(r1_eus_reassembly_scratch+1,reference);r1_eus_reassembly_scratch[5]=1;
   (void)((r1_eus_send_callback_t)callback)((uint16_t)connection,r1_eus_reassembly_scratch,6);
  }
 }else{
  uintptr_t callback=r1_eus_rx_complete_callback;
  if(callback)(void)((uint32_t (*)(uint32_t,uint32_t,const void *,uint32_t))callback)(connection,channel,message,size);
 }
 uint8_t *buffer=r1_eus_reassembly_state.buffer;
 if(buffer!=r1_eus_reassembly_scratch)vPortFree(buffer);
 r1_eus_reassembly_state.buffer=0;r1_eus_reassembly_state.used=0;r1_eus_reassembly_capacity=0;
 return 0;
}
