#include <stdint.h>
extern uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t);
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t);
extern uint32_t opencfw_em9305_radio_request_30faec(uintptr_t,uint32_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t);
static uint32_t rd(uintptr_t p){return *(volatile uint32_t *)p;}
static uint8_t rb(uintptr_t p){return *(volatile uint8_t *)p;}
static void wr(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}
static void wb(uintptr_t p,uint8_t v){*(volatile uint8_t *)p=v;}
static uint32_t multiply(uint32_t a,uint32_t b)
{
#ifdef __arc__
 uint32_t r;
 __asm__ volatile("mpywhl %0,%1,%2":"=r"(r):"r"(a),"r"(b):"r58","r59","memory");
 return r;
#else
 return a*(uint32_t)(int32_t)(int16_t)b;
#endif
}
/* Authenticated3043ac..30442e; next-count store is unconditional delay. */
uint32_t opencfw_em9305_init_callback_3043ac(uint32_t incoming,
 uintptr_t context,uint32_t result)
{
 uintptr_t fields=context+224u;
 (void)opencfw_em9305_radio_cancel_30fab8(incoming);
 uint32_t old=rb(fields),limit=rb(fields+4u);
 uint8_t next=(uint8_t)(old+1u);
 wb(fields,next);
 if(next>=limit)goto fallback;
 uint32_t index=rb(context+225u),count=rb(context+226u);
 if(index>=count)goto fallback;
 if(rd(context+208u+index*4u)==0u)goto fallback;
 uint32_t interval=rd(fields+24u);
 uint32_t half=rd(fields+32u);
 uint32_t first=rd(fields+12u);
 uint32_t second=rd(fields+20u);
 uint32_t product=multiply(interval,next);
 wb(0x8015c4u,1u);
 uintptr_t binding=0x8015ccu;
 wr(binding+12u,half<<1u);
 wr(binding+8u,second+first+product-half);
 (void)opencfw_em9305_common_radio_bind_30fc10(binding);
 index=rb(context+225u);
 uintptr_t request=rd(context+208u+index*4u);
 (void)opencfw_em9305_radio_request_30faec(request,257u);
 return result;
fallback:
 {
  uint8_t frame[20];
  (void)opencfw_em9305_memset(frame,0u,20u);
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)frame);
  return 1u;
 }
}
/* Authenticated304430..304464. Incoming owner survives cancel's return;
 * the index store runs before child3043ac via the native BL delay slot. */
uint32_t opencfw_em9305_init_callback_304430(uint32_t owner,
 uintptr_t context,uint32_t result)
{
 (void)opencfw_em9305_radio_cancel_30fab8(owner);
 uintptr_t callback=rd(context+164u);
 if(callback!=0u){uint32_t index=rb(context+225u);
  (void)((uint32_t (*)(uint32_t,uint32_t,uintptr_t))callback)(owner,index,callback);}
 uint32_t index=(uint32_t)rb(context+225u)+1u;
 if((uint8_t)index==4u)index=0u;
 wb(context+225u,(uint8_t)index);
 return opencfw_em9305_init_callback_3043ac(index,context,result);
}
