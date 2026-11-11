#include "driver.h"
#include "../clock-manager-ownership/ownership.h"
#include "../../xtal-request/request.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200001c8[] __asm__("g2_stock_ram_200001c8");
extern unsigned char g2ref_g2_stock_ram_20004530[] __asm__("g2_stock_ram_20004530");
extern unsigned char g2ref_g2_stock_ram_20073f30[] __asm__("g2_stock_ram_20073f30");
extern unsigned char g2ref_g2_stock_ram_20074228[] __asm__("g2_stock_ram_20074228");
extern unsigned char g2ref_g2_stock_ram_20074f30[] __asm__("g2_stock_ram_20074f30");
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_save_irq(void),stock_hfrc2_ratio(uint32_t,uint32_t,uint32_t,uint32_t *),stock_pll_generate(void *,uint32_t,uint32_t);
extern uint32_t stock_ext_request(uint32_t),stock_ext_release(uint32_t),stock_hfrc2_apply(const void *),stock_hfrc2_disable(void);
static void restore(uint32_t m){__asm volatile("msr primask, %0"::"r"(m):"memory");}
/* Stock 0x4C399E (am_hal_clkmgr HFRC2 config) */
uint32_t audio_hfrc2_config(uint32_t hz,const uint32_t *cfg){
 uint32_t status=0,sw=(hz==0||hz==250000000)&&(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))==0||W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))==250000000);uint32_t generated[3]={0x200,0xc49ba,0};
 if(hz!=0&&hz!=196608000&&hz!=250000000)return 5;
 if(hz){
  if(!cfg){uint32_t reference;if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u))){((uint8_t*)generated)[0]=0;reference=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u));}else if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u))){((uint8_t*)generated)[0]=1;reference=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u));}else return 7;
   status=stock_hfrc2_ratio(reference,hz,((uint8_t*)generated)[1],generated+1);cfg=generated;
  }else{if(((const uint8_t*)cfg)[0]==0&&!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u)))return 7;if(((const uint8_t*)cfg)[0]==1&&!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u)))return 7;}
 }
 if(!status){uint32_t requested=0,m=stock_save_irq();if(audio_clock_count(5)){if(sw)requested=1;else status=3;}
  if(!status){if(hz)for(unsigned i=0;i<3;i++)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu)+4*i)=cfg[i];W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))=hz;B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20004530+0x7u))=1;}restore(m);
  if(requested){if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu))==0)audio_xtal_request(54);else stock_ext_request(54);
   m=stock_save_irq();if(audio_clock_count(5)){
    if(!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu)))status=stock_hfrc2_disable();else{status=stock_hfrc2_apply((void*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu));if(!status){if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0xcu))==0)stock_ext_release(54);else audio_xtal_release(54);}}
    if(status||!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x2cu))){stock_ext_release(54);audio_xtal_release(54);}
   }else{audio_xtal_release(54);stock_ext_release(54);}restore(m);
  }
 }
 return status;
}
/* Stock 0x4C3B44 (am_hal_clkmgr SYSPLL config) */
uint32_t audio_syspll_config(uint32_t hz,const uint32_t *cfg){
 uint32_t status=0,generated[3]={0,0,0};
 if(!cfg){uint32_t reference;if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u))){((uint8_t*)generated)[0]=0;reference=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u));}else if(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u))){((uint8_t*)generated)[0]=1;reference=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u));}else return 7;status=stock_pll_generate(generated,reference,hz);cfg=generated;
 }else{if(((const uint8_t*)cfg)[0]==0&&!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u)))return 7;if(((const uint8_t*)cfg)[0]==1&&!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x14u)))return 7;}
 if(!status){uint32_t m=stock_save_irq();if(audio_clock_count(6))status=3;if(!status){for(unsigned i=0;i<3;i++)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30+0x18u)+4*i)=cfg[i];W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x30u))=hz;B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x25u))=1;}restore(m);}return status;
}
/* Stock 0x4C446C (am_hal_clkmgr_clock_config) */
uint32_t audio_clock_config(uint32_t clock,uint32_t hz,const uint32_t *cfg){switch((uint8_t)clock){case 4:return audio_hfrc_config(hz,cfg);case 5:return audio_hfrc2_config(hz,cfg);case 6:return audio_syspll_config(hz,cfg);default:return 7;}}
