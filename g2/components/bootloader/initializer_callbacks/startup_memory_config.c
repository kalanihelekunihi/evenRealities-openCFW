/* SPDX-License-Identifier: MIT. Locked-f89a4c46 reconstruction.
 * Five-byte stock layouts differ from public HAL enum-typed structure sizes. */
#include "startup_memory_config.h"
#include "../platform_control/power_domains.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern uint32_t opencfw_hal_status_poll(uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t);
NI uint32_t opencfw_boot_startup_mcu_memory(const uint8_t config[5]){
 uint32_t desired=0,enable=0;uint8_t force=0;B(0x200271a7)=config[0];
 if(config[0]==0){enable|=32;desired|=128;}
 enable|=config[1]&7;desired|=config[1]&7;
 if(config[3]==1){enable|=8;desired|=8;}else if(config[3]==3){enable|=24;desired|=72;}
 if(config[3]==3&&(W(0x40021018)&72)==8){W(0x40020284)|=1;force=1;}
 if(desired!=W(0x40021018)){
  uint32_t expected=desired&W(0x40021018);W(0x40021014)&=enable;
  uint32_t status=opencfw_hal_status_poll(5,0x40021018,0xcf,expected,1);if(status)return status;
  (void)opencfw_boot_power_callback(5,1,&desired);W(0x40021014)=enable;
  status=opencfw_hal_status_poll(5,0x40021018,0xcf,desired,1);
  if(force)W(0x40020284)&=~1u;
  if(status)return status;
  if((W(0x40021018)&7)!=(W(0x40021014)&7)||((W(0x40021018)>>3)&1)!=((W(0x40021014)>>3)&1)||((W(0x40021018)>>6)&(W(0x40021018)>>3)&1)!=((W(0x40021014)>>4)&1)||((W(0x40021018)>>7)&1)!=((W(0x40021014)>>5)&1)||((W(0x40021008)>>27)&1)!=((W(0x40021004)>>27)&1))return 1;
 }
 if(config[4])W(0x4002101c)&=~2u;else W(0x4002101c)|=2;
 if(config[2]==1)W(0x4002101c)|=1;else if(config[2]==0)W(0x4002101c)&=~1u;else return 5;
 return 0;
}
NI uint32_t opencfw_boot_startup_shared_memory(const uint8_t config[5]){
 uint8_t lower=0;
 if(config[0]!=(W(0x40021028)&7)){
  if((W(0x40021028)&7)<config[0]){(void)opencfw_boot_power_callback(6,1,(void *)config);lower=0;}else lower=1;
  W(0x40021024)=(W(0x40021024)&~7u)|(config[0]&7);
  uint32_t status=opencfw_hal_status_poll(5,0x40021028,7,W(0x40021024),1);if(status)return status;
  if((W(0x40021028)&7)!=(W(0x40021024)&7))return 1;
  if(lower)(void)opencfw_boot_power_callback(6,0,(void *)0);
 }
 W(0x4002102c)=(W(0x4002102c)&~56u)|((config[1]&7)<<3);
 W(0x4002102c)=(W(0x4002102c)&~0xe00u)|((config[2]&7)<<9);
 W(0x4002102c)=(W(0x4002102c)&~0x7000u)|((config[3]&7)<<12);
 if(config[4]==0)W(0x4002102c)|=7;
 else if(config[4]==1)W(0x4002102c)=(W(0x4002102c)&~7u)|6;
 else if(config[4]==3)W(0x4002102c)=(W(0x4002102c)&~7u)|4;
 else if(config[4]==7)W(0x4002102c)&=~7u;
 W(0x40021040)&=~0x3800u;W(0x40021040)&=~0x700u;return 0;
}
