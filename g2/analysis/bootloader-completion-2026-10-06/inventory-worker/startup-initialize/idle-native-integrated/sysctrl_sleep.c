/* Reconstruction of locked41a71e..41ac44. SDK pin corroborates, bytes govern.
 * Peripheral completion and WFI wake are explicit test-model boundaries. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t irq_save(void);
extern void cp_get(uint8_t *),cp_set(uint32_t),power_state(uint32_t,uint32_t,uint8_t *);
extern void buck_override(uint32_t),lp_enable(void),lp_disable(void),delay_one(uint32_t),boost_service(void);
#define HP_TO_DEEP B(0x200271b0)
#define CPU_OVERRIDES B(0x200271af)
#define PCM22 B(0x200271ad)
#define PCM21 B(0x200271a9)
#define SWITCHING_HP B(0x200271b2)
#define LP_MINUS B(0x200271b1)
#define APP_FORCE B(0x200271c1)
#define FORCE B(0x200271c0)
#define INFO W(0x20026ba0)
#define MEMCFG W(0x20026c08)
#define GPUCFG W(0x20026bf4)
static void prepare_trims(uint8_t *restore){
 if(HP_TO_DEEP){W(0x40020374)=(W(0x40020374)&~31u)|((MEMCFG>>20)&31);
  if(CPU_OVERRIDES){W(0x4002037c)&=~8u;W(0x4002037c)&=~64u;}
  *restore=(PCM22&&CPU_OVERRIDES)||(PCM21&&CPU_OVERRIDES&&!SWITCHING_HP);
 }
 if(LP_MINUS)W(0x40020374)=(W(0x40020374)&~31u)|11;
}
static void restore_trims(uint8_t restore){
 if(HP_TO_DEEP){if(restore){W(0x4002037c)|=8;W(0x4002037c)|=64;}W(0x40020374)&=~31u;}
 if(LP_MINUS)W(0x40020374)&=~31u;
}
static void sleep_instruction(void){(void)W(0x47ff0000);__asm__ volatile("wfi\n isb sy":::"memory");}
uint32_t deep_sleep(uint32_t deep){
 uint8_t act[3],state=0,reported=0,periph_off=0,buck_low=0,restore=0,changed=0,other=0;
 uint32_t old_trim=0,mask=irq_save();cp_get(act);
 uint32_t packed=((uint32_t)act[0]<<8)|((uint32_t)act[1]<<4)|act[2];
 uint8_t simo=((W(0x40021108)>>4)&3)==3;
 if((uint8_t)deep==1 && !(W(0x40021008)&0x08000000)){
  uint32_t config=(0x00020200u&~255u)|act[0];if(act[1]==3)config=(config&~0xff00u)|0x300;
  cp_set(config);state=2;power_state(0,0,&state);state=(W(0x40021000)&3)==2;reported=1;
  if(simo && (((W(0x4002000c)&255)==0x22 && W(0x20000098)>1)||((W(0x4002000c)&255)==0x23 && W(0x20000098)!=0)||(!(W(0x40021010)&0x4c4)&&!(W(0x40021008)&0x3fffffff)&&!(W(0x400204d8)&0x20000000)))){
   periph_off=1;if(!APP_FORCE&&!FORCE){buck_low=1;buck_override(0);lp_enable();}
  }
  W(0xe000ed10)|=4;
  if((W(0x40021000)&3)==2)while(((W(0x40021000)>>3)&3)!=2)delay_one(1);
  prepare_trims(&restore);
  if(INFO==0x1f01600d && PCM21 && ((GPUCFG>>5)&31)<((W(0x40020344)>>25)&31)){
   old_trim=(W(0x40020344)>>25)&31;W(0x40020344)=(W(0x40020344)&0xc1ffffff)|(((GPUCFG>>5)&31)<<25);changed=1;
  }
 }else{
  uint32_t elp=(act[1]==3||act[1]==2)?act[1]:1;
  cp_set(act[0]|(elp<<8)|0x10000);W(0xe000ed10)&=~4u;
 }
 sleep_instruction();
 if(changed)W(0x40020344)=(W(0x40020344)&0xc1ffffff)|(old_trim<<25);
 restore_trims(restore);
 if((PCM21||PCM22)&&((W(0xe000ed04)>>12)&0x1ff)==0x62){
  boost_service();
  if(((W(0xe000ed04)>>12)&0x1ff)==0){
   if((uint8_t)deep==1 && (W(0x40021000)&3)==2){while(((W(0x40021000)>>3)&3)!=2){if(((W(0xe000ed04)>>12)&0x1ff)!=0){other=1;break;}delay_one(1);}}
   if(!other){
    if(reported){power_state(0,0,&state);uint8_t ds=2;power_state(0,0,&ds);}
    if(periph_off&&!APP_FORCE&&!FORCE){buck_low=1;buck_override(0);lp_enable();}
    /* On second sleep preserve the first restore decision. */
    uint8_t unused=restore;prepare_trims(&unused);
    if(changed)W(0x40020344)=(W(0x40020344)&0xc1ffffff)|(((GPUCFG>>5)&31)<<25);
    sleep_instruction();
    if(changed)W(0x40020344)=(W(0x40020344)&0xc1ffffff)|(old_trim<<25);
    restore_trims(restore);
   }
  }
 }
 if(HP_TO_DEEP){HP_TO_DEEP=0;CPU_OVERRIDES=0;}if(LP_MINUS)LP_MINUS=0;
 if(reported)power_state(0,0,&state);
 if(buck_low){W(0x40020060)|=0x10000;W(0x40020060)|=1;W(0x40020060)|=0x20;}
 lp_disable();W(0xe001e300)=packed;
 __asm__ volatile("msr primask,%0"::"r"(mask):"memory");return mask;
}
