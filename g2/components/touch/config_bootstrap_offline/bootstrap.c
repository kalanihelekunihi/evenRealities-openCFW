/* Independent instruction-derived bootstrap. Offline fixed ARM32 guest ABI;
 * logger is the observed return-zero leaf, not a working hardware logger. */
#include "bootstrap.h"
#include "eeprom.h"
#include "init.h"
#define READY (*(volatile uint8_t *)0x200008c4u)
#define CONTEXT ((uint8_t *)0x200008c8u)
#define RECORD ((touch_saved_record *)0x200009d0u)
uint32_t touch_application_read(uint32_t address,uint8_t *out,uint32_t size) {
 if(!out || address+size>256u)return 4;
 if(!READY)return 1;
 uint32_t s=touch_eeprom_read(address,out,size,CONTEXT);
 return s==0 || s==TOUCH_EEPROM_REDUNDANT_USED?0:2;
}
uint32_t touch_application_write(uint32_t address,const uint8_t *data,uint32_t size) {
 if(!data || address+size>256u)return 4;
 if(!READY)return 1;
 uint32_t s=touch_eeprom_write(address,data,size,CONTEXT);
 return s==0 || s==TOUCH_EEPROM_REDUNDANT_USED?0:3;
}
uint32_t touch_application_erase(void) {
 if(!READY)return 1;
 uint32_t s=touch_eeprom_erase(CONTEXT);
 return s==0 || s==TOUCH_EEPROM_REDUNDANT_USED?0:3;
}
__attribute__((noinline,noipa)) uint32_t touch_bootstrap_log(uint32_t format,uint32_t a,uint32_t b,uint32_t c) {
 (void)format;(void)a;(void)b;(void)c;return 0;
}
__attribute__((noinline)) void touch_bootstrap_cycles(uint32_t cycles) {
 volatile uint32_t n=(cycles+2u)>>2;
 if(n){n++; do {n-=2u;if(n)n++;}while(n);}
}
void touch_bootstrap_delay(uint32_t argument) {
 while(argument>32768u){touch_bootstrap_cycles(*(volatile uint32_t *)0x2000086cu);argument-=32768u;}
 touch_bootstrap_cycles(*(volatile uint32_t *)0x20000874u * argument);
}
void touch_config_bootstrap(void) {
 uint32_t s=touch_application_eeprom_init();
 if(s){touch_bootstrap_log(0xaab8,s,0xaa5c,0);return;}
 s=touch_application_read(0,(uint8_t *)RECORD,8);
 if(s || RECORD->magic!=0x45564e55u) {
  touch_bootstrap_log(0xaae0,0xaa5c,0,0);
  s=touch_application_erase();
  if(s){touch_bootstrap_log(0xab20,s,0xaa5c,0);return;}
  touch_bootstrap_delay(10);
  RECORD->magic=0x45564e55u;RECORD->baseline=0;RECORD->parameter=1000;
  s=touch_application_write(0,(const uint8_t *)RECORD,8);
  if(s){touch_bootstrap_log(0xab48,s,0xaa5c,0);return;}
  touch_bootstrap_log(0xab78,0xaa5c,0,0);return;
 }
 if(!RECORD->parameter)RECORD->parameter=1000;
 touch_bootstrap_log(0xaba8,RECORD->baseline,RECORD->parameter,0xaa5c);
}
