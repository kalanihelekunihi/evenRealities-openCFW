#include "driver.h"
#include "../clock_manager_ownership_offline/ownership.h"
#include "../xtal_request_offline/request.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_save_irq(void),stock_hfrc2_ratio(uint32_t,uint32_t,uint32_t,uint32_t *),stock_pll_generate(void *,uint32_t,uint32_t);
extern uint32_t stock_ext_request(uint32_t),stock_ext_release(uint32_t),stock_hfrc2_apply(const void *),stock_hfrc2_disable(void);
static void restore(uint32_t m){__asm volatile("msr primask, %0"::"r"(m):"memory");}
uint32_t audio_hfrc2_config(uint32_t hz,const uint32_t *cfg){
 uint32_t status=0,sw=(hz==0||hz==250000000)&&(W(0x20074254)==0||W(0x20074254)==250000000);uint32_t generated[3]={0x200,0xc49ba,0};
 if(hz!=0&&hz!=196608000&&hz!=250000000)return 5;
 if(hz){
  if(!cfg){uint32_t reference;if(W(0x200001d0)){((uint8_t*)generated)[0]=0;reference=W(0x200001d0);}else if(W(0x200001dc)){((uint8_t*)generated)[0]=1;reference=W(0x200001dc);}else return 7;
   status=stock_hfrc2_ratio(reference,hz,((uint8_t*)generated)[1],generated+1);cfg=generated;
  }else{if(((const uint8_t*)cfg)[0]==0&&!W(0x200001d0))return 7;if(((const uint8_t*)cfg)[0]==1&&!W(0x200001dc))return 7;}
 }
 if(!status){uint32_t requested=0,m=stock_save_irq();if(audio_clock_count(5)){if(sw)requested=1;else status=3;}
  if(!status){if(hz)for(unsigned i=0;i<3;i++)W(0x20073f3c+4*i)=cfg[i];W(0x20074254)=hz;B(0x20004537)=1;}restore(m);
  if(requested){if(B(0x20073f3c)==0)audio_xtal_request(54);else stock_ext_request(54);
   m=stock_save_irq();if(audio_clock_count(5)){
    if(!W(0x20074254))status=stock_hfrc2_disable();else{status=stock_hfrc2_apply((void*)0x20073f3c);if(!status){if(B(0x20073f3c)==0)stock_ext_release(54);else audio_xtal_release(54);}}
    if(status||!W(0x20074254)){stock_ext_release(54);audio_xtal_release(54);}
   }else{audio_xtal_release(54);stock_ext_release(54);}restore(m);
  }
 }
 return status;
}
uint32_t audio_syspll_config(uint32_t hz,const uint32_t *cfg){
 uint32_t status=0,generated[3]={0,0,0};
 if(!cfg){uint32_t reference;if(W(0x200001d0)){((uint8_t*)generated)[0]=0;reference=W(0x200001d0);}else if(W(0x200001dc)){((uint8_t*)generated)[0]=1;reference=W(0x200001dc);}else return 7;status=stock_pll_generate(generated,reference,hz);cfg=generated;
 }else{if(((const uint8_t*)cfg)[0]==0&&!W(0x200001d0))return 7;if(((const uint8_t*)cfg)[0]==1&&!W(0x200001dc))return 7;}
 if(!status){uint32_t m=stock_save_irq();if(audio_clock_count(6))status=3;if(!status){for(unsigned i=0;i<3;i++)W(0x20073f48+4*i)=cfg[i];W(0x20074258)=hz;B(0x20074f55)=1;}restore(m);}return status;
}
uint32_t audio_clock_config(uint32_t clock,uint32_t hz,const uint32_t *cfg){switch((uint8_t)clock){case 4:return audio_hfrc_config(hz,cfg);case 5:return audio_hfrc2_config(hz,cfg);case 6:return audio_syspll_config(hz,cfg);default:return 7;}}
