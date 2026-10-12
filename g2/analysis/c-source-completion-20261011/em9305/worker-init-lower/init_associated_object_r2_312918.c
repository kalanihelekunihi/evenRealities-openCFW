#include <stdint.h>
#include "associated_312918_regs.h"

extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_duration_312be4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t);
static inline uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b)
{
#ifdef OPENCFW_EM9305_HOST_FIXTURE
 return (uint32_t)((int64_t)(int32_t)a*(int64_t)(int16_t)b);
#else
 uint32_t r;__asm__ volatile("mpywhl %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;
#endif
}
static inline uint32_t opencfw_em9305_config_link_divu_prior(uint32_t a,uint32_t b,uint32_t prior)
{
#ifdef OPENCFW_EM9305_HOST_FIXTURE
 return b!=0u?a/b:prior;
#else
 __asm__ volatile("divu %0,%1,%2":"+r"(prior):"r"(a),"r"(b));return prior;
#endif
}
/* Same native body as selected 312918, with a typed exit-R2 side channel.
 * R2 is tracked from original branch reads and fixed child register effects.
 * Incoming R2 is retained on branches where native does not define it. */
uint32_t opencfw_em9305_associated_object_init_with_regs_312918(uintptr_t object,uint32_t requested,struct opencfw_associated_312918_regs *regs)
{
 uintptr_t packet=*(volatile uint32_t *)(object+44u);
 uint32_t type=*(volatile uint8_t *)packet,index=type-2u,duration=0u,result=index;
 uint32_t kind,phy,mode,size;
 uint32_t live_r2=regs->r2;
 switch(index){
 case 0u:
  kind=*(volatile uint8_t *)(packet+13u);
  result=*(volatile uint32_t *)(packet+104u);duration=kind==3u?3088u:376u;
  if(result!=0u){
   size=*(volatile uint8_t *)(packet+149u);live_r2=size;phy=*(volatile uint8_t *)(packet+12u);
   result=opencfw_em9305_radio_duration_piece_312b88(phy,0u,size);duration+=result+150u;
   uint32_t extra=*(volatile uint32_t *)(packet+108u);
   if(extra!=0u)duration+=kind==3u?3238u:526u;
  }
  break;
 case 1u:{
  size=*(volatile uint8_t *)(packet+124u);mode=*(volatile uint8_t *)(packet+14u);phy=*(volatile uint8_t *)(packet+12u);
  uint32_t initial=opencfw_em9305_radio_duration_piece_312b88(phy,mode,size);
  uint32_t flags=*(volatile uint8_t *)(packet+127u);
  uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
  uint32_t adjusted=opencfw_em9305_channel_timing_adjust_312c5c(guard+initial);
  uint32_t count=(flags&1u)+((flags>>1u)&1u)+((flags>>2u)&1u);
  duration=(count-1u)*adjusted+initial;
  result=adjusted;
  uint32_t enabled=*(volatile uint32_t *)(packet+104u);live_r2=enabled;
  if(enabled!=0u){
   kind=*(volatile uint8_t *)(packet+13u);live_r2=0xc10u;
   uint32_t gap=count*150u,base=kind==3u?3088u:376u;
   result=(base&65535u)*(count&65535u);duration+=gap+result;
   uint32_t extra=*(volatile uint32_t *)(packet+108u);
   if(extra!=0u){
    size=*(volatile uint8_t *)(packet+149u);live_r2=size;phy=*(volatile uint8_t *)(packet+12u);
    result=opencfw_em9305_radio_duration_piece_312b88(phy,0u,size);
    result=opencfw_em9305_native_mpywhl(result,count);
    duration+=gap+result;
   }
  }
  break;
 }
 case 4u:{
  uint32_t extended=*(volatile uint8_t *)(packet+132u);kind=*(volatile uint8_t *)(packet+13u);
  if(extended!=0u){
   duration=kind==3u?720u:(kind==2u?44u:80u);
   if(kind==3u)*(volatile uint32_t *)(object+16u)=17040u;
   result=*(volatile uint32_t *)(packet+100u);
   live_r2=36u; /* 312a9c BREQ.D executes MOV R2,36 even when result=0. */
   if(result!=0u){
    mode=*(volatile uint8_t *)(packet+15u);phy=*(volatile uint8_t *)(packet+12u);
    result=opencfw_em9305_radio_duration_piece_312b88(phy,mode==0u?2u:mode,36u);
    duration+=kind==3u?1916u:(kind==2u?400u:492u);
    if(kind!=3u)live_r2=400u; /* 312abc executes for kind 2 and other. */
    duration+=result;
   }
  }else{
   duration=kind==3u?3792u:(kind==2u?236u:464u);
   if(kind==3u)*(volatile uint32_t *)(object+16u)=17040u;
   result=*(volatile uint32_t *)(packet+100u);
   if(result!=0u){
    mode=*(volatile uint8_t *)(packet+15u);size=*(volatile uint8_t *)(packet+124u);live_r2=size;phy=*(volatile uint8_t *)(packet+12u);
    result=opencfw_em9305_radio_duration_piece_312b88(phy,mode==0u?2u:mode,size);
    duration+=result+150u+(kind==3u?17190u:(kind==2u?1214u:2270u));
   }
  }
  break;
 }
 case 5u:{
  uint32_t step=requested!=0u?requested:241u,limit=requested!=0u?requested:244u;
  result=*(volatile uint32_t *)(packet+116u);
  live_r2=13u; /* 312a54 BREQ.D delay slot, including disabled path. */
  if(result!=0u){
   mode=*(volatile uint8_t *)(packet+14u);phy=*(volatile uint8_t *)(packet+12u);
   result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,13u);duration=result;
   kind=*(volatile uint8_t *)(packet+13u);
   duration+=150u+(kind==3u?17190u:(kind==2u?1214u:2270u));
  }
  uintptr_t source=*(volatile uint32_t *)(object+40u);
  uint32_t amount=source!=0u?*(volatile uint16_t *)source:0u;
  mode=*(volatile uint8_t *)(packet+14u);phy=*(volatile uint8_t *)(packet+12u);
  if(limit<amount){
   result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,step+16u);
   uint32_t quotient=opencfw_em9305_config_link_divu_prior(amount,step,step);
   result+=300u;
   uint32_t product=(uint32_t)((int32_t)(int16_t)step*(int32_t)(int16_t)quotient);
   result*=quotient;duration+=result;
   uint32_t remainder=amount-product;live_r2=remainder;
   if((uint16_t)remainder!=0u){live_r2=(uint32_t)(int32_t)(int16_t)(remainder+13u);result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,live_r2);duration+=result;}
  }else{
   uint32_t addition=*(volatile uint16_t *)(packet+100u);if(addition<13u)addition=13u;
   live_r2=(uint32_t)(int32_t)(int16_t)(amount+addition);result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,live_r2);duration+=result;
  }
  break;
 }
 case 6u:
  {uintptr_t source=*(volatile uint32_t *)(object+40u);size=source!=0u?*(volatile uint16_t *)source:64u;if(size<64u)size=64u;}
  phy=*(volatile uint8_t *)(packet+12u);mode=*(volatile uint8_t *)(packet+14u);
  result=opencfw_em9305_radio_duration_312be4(phy,0u,0u,0u,size,0u,mode,0u);duration=result;
  regs->r4=size;regs->r5=0u;regs->r6=mode;regs->r7=0u;
  live_r2=size<=252u?size+5u:(size%247u==0u?257u:(uint32_t)(int32_t)(int16_t)((size%247u)+5u));break;
 case 7u:
  phy=*(volatile uint8_t *)(packet+12u);mode=*(volatile uint8_t *)(packet+14u);
  result=opencfw_em9305_radio_duration_312be4(phy,0u,0u,0u,0u,0u,mode,0u);duration=result;
  regs->r4=0u;regs->r5=0u;regs->r6=mode;regs->r7=0u;
  live_r2=5u;break;
 default:break;
 }
 *(volatile uint32_t *)(object+12u)=duration;
 regs->r2=live_r2;
 regs->r3=duration; /* Native R3 is the stored accumulator at 312b82. */
 return result;
}
