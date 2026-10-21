#include "memory.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern uint32_t stock_wait5(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t stock_dispatch(uint32_t,uint32_t,const void*);
_Static_assert(sizeof(audio_mcu_memory_cfg)==5,"MCU config layout");
_Static_assert(sizeof(audio_sram_cfg)==5,"SRAM config layout");
uint32_t audio_mcu_memory_config(const audio_mcu_memory_cfg *cfg){
 uint32_t enable=0,target=0,forced=0;
 B(0x20074f62)=cfg->rom_mode;
 if(cfg->rom_mode==0){enable|=32;target|=128;}
 enable|=cfg->dtcm_active&7;target|=cfg->dtcm_active&7;
 if(cfg->nvm_active==1){enable|=8;target|=8;}
 else if(cfg->nvm_active==3){enable|=24;target|=72;}
 if(cfg->nvm_active==3&&(W(0x40021018)&72)==8){W(0x40020284)|=1;forced=1;}
 if(target!=W(0x40021018)){
  uint32_t after_disables=W(0x40021018)&target;
  W(0x40021014)&=enable;
  uint32_t status=stock_wait5(5,0x40021018,207,after_disables,1);
  if(status)return status; /* Original leaves forced AXI on here. */
  (void)stock_dispatch(5,1,&target); /* Stock discards dispatcher error. */
  W(0x40021014)=enable;
  status=stock_wait5(5,0x40021018,207,target,1);
  if(forced)W(0x40020284)&=~1u;
  if(status)return status;
  if((W(0x40021018)&7)!=(W(0x40021014)&7)||
     ((W(0x40021018)>>3)&1)!=((W(0x40021014)>>3)&1)||
     (((W(0x40021018)>>6)&(W(0x40021018)>>3))&1)!=((W(0x40021014)>>4)&1)||
     ((W(0x40021018)>>7)&1)!=((W(0x40021014)>>5)&1)||
     ((W(0x40021008)>>27)&1)!=((W(0x40021004)>>27)&1))return 1;
 }
 if(cfg->keep_nvm_on_sleep)W(0x4002101c)&=~2u;else W(0x4002101c)|=2;
 if(cfg->dtcm_retain==1)W(0x4002101c)|=1;
 else if(cfg->dtcm_retain==0)W(0x4002101c)&=~1u;
 else return 5;
 return 0;
}
uint32_t audio_sram_config(const audio_sram_cfg *cfg){
 if(cfg->active!=(W(0x40021028)&7)){
  uint32_t update_later=(W(0x40021028)&7)>=cfg->active;
  if(!update_later)(void)stock_dispatch(6,1,cfg);
  W(0x40021024)=(W(0x40021024)&~7u)|(cfg->active&7);
  uint32_t status=stock_wait5(5,0x40021028,7,W(0x40021024),1);
  if(status)return status;
  if((W(0x40021028)&7)!=(W(0x40021024)&7))return 1;
  if(update_later)(void)stock_dispatch(6,0,0);
 }
 W(0x4002102c)=(W(0x4002102c)&~56u)|((cfg->with_mcu&7)<<3);
 W(0x4002102c)=(W(0x4002102c)&~3584u)|((cfg->with_gpu&7)<<9);
 W(0x4002102c)=(W(0x4002102c)&~28672u)|((cfg->with_display&7)<<12);
 if(cfg->retain==0)W(0x4002102c)|=7;
 else if(cfg->retain==1)W(0x4002102c)=(W(0x4002102c)&~7u)|6;
 else if(cfg->retain==3)W(0x4002102c)=(W(0x4002102c)&~7u)|4;
 else if(cfg->retain==7)W(0x4002102c)&=~7u;
 W(0x40021040)&=~14336u;W(0x40021040)&=~1792u;
 return 0;
}
