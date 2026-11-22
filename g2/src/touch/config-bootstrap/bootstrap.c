/* Independent instruction-derived bootstrap. Offline fixed ARM32 guest ABI;
 * logger is the observed return-zero leaf, not a working hardware logger. */
#include "bootstrap.h"
#include "eeprom.h"
#include "init.h"
#include "cy_syslib.h"
#include "../application/ram_state.h"
#include "../glue/touch_clock_state.h"
#define READY touch_eeprom_ready_ram
#define CONTEXT touch_eeprom_context_ram
#define RECORD (&touch_saved_record_ram)
/* Locked Touch ROM 0xAA5C and 0xAAB8..0xAC3D: logger arguments are
 * source-owned even though the stock logger itself returns zero. */
const char touch_log_color_reset[] = "\x1b[0m";
static const char log_eeprom_init_failed[] = "\x1b[31m[E] EEPROM init failed: %lu%s\r\n";
static const char log_eeprom_first_use[] = "\x1b[36m[I] EEPROM first use, initializing default config...%s\r\n";
static const char log_eeprom_erase_failed[] = "\x1b[31m[E] EEPROM erase failed: %lu%s\r\n";
static const char log_default_write_failed[] = "\x1b[31m[E] Write default config failed: %lu%s\r\n";
static const char log_default_initialized[] = "\x1b[36m[I] EEPROM default config initialized%s\r\n";
static const char log_config_loaded[] = "\x1b[36m[I] EEPROM config loaded: prox_bsln=%u, long=%u%s\r\n";
const char touch_log_save_failed[] = "\x1b[31m[E] Save config failed: %lu%s\r\n";
const char touch_log_saved[] = "\x1b[36m[I] Config saved: prox_bsln=%u, long=%u%s\r\n";
/* Stock 0x00003520 (touch_storage_0220_read) */
uint32_t touch_application_read(uint32_t address,uint8_t *out,uint32_t size) {
 if(!out || address+size>256u)return 4;
 if(!READY)return 1;
 uint32_t s=touch_eeprom_read(address,out,size,CONTEXT);
 return s==0 || s==TOUCH_EEPROM_REDUNDANT_USED?0:2;
}
/* Stock 0x00003568 (touch_config_read_adapter) */
uint32_t touch_application_write(uint32_t address,const uint8_t *data,uint32_t size) {
 if(!data || address+size>256u)return 4;
 if(!READY)return 1;
 uint32_t s=touch_eeprom_write(address,data,size,CONTEXT);
 return s==0 || s==TOUCH_EEPROM_REDUNDANT_USED?0:3;
}
/* Stock 0x000035B0 (touch_storage_02b0_context_operation) */
uint32_t touch_application_erase(void) {
 if(!READY)return 1;
 uint32_t s=touch_eeprom_erase(CONTEXT);
 return s==0 || s==TOUCH_EEPROM_REDUNDANT_USED?0:3;
}
/* Stock 0x00003EE0 (logger_stub) */
__attribute__((noinline,noipa)) uint32_t touch_bootstrap_log(uint32_t format,uint32_t a,uint32_t b,uint32_t c) {
 (void)format;(void)a;(void)b;(void)c;return 0;
}
/* Stock 0x0000A2F0 (Cy_SysLib_Delay) */
void touch_bootstrap_delay(uint32_t argument) {
 while(argument>32768u){Cy_SysLib_DelayCycles(cy_delay32kMs);argument-=32768u;}
 Cy_SysLib_DelayCycles(cy_delayFreqKhz * argument);
}
/* Stock 0x0000395C (touch_config_065c_bootstrap) */
void touch_config_bootstrap(void) {
 uint32_t s=touch_application_eeprom_init();
 if(s){touch_bootstrap_log(TOUCH_LOG_ADDR(log_eeprom_init_failed),s,TOUCH_LOG_ADDR(touch_log_color_reset),0);return;}
 s=touch_application_read(0,(uint8_t *)RECORD,8);
 if(s || RECORD->magic!=0x45564e55u) {
  touch_bootstrap_log(TOUCH_LOG_ADDR(log_eeprom_first_use),TOUCH_LOG_ADDR(touch_log_color_reset),0,0);
  s=touch_application_erase();
  if(s){touch_bootstrap_log(TOUCH_LOG_ADDR(log_eeprom_erase_failed),s,TOUCH_LOG_ADDR(touch_log_color_reset),0);return;}
  touch_bootstrap_delay(10);
  RECORD->magic=0x45564e55u;RECORD->baseline=0;RECORD->parameter=1000;
  s=touch_application_write(0,(const uint8_t *)RECORD,8);
  if(s){touch_bootstrap_log(TOUCH_LOG_ADDR(log_default_write_failed),s,TOUCH_LOG_ADDR(touch_log_color_reset),0);return;}
  touch_bootstrap_log(TOUCH_LOG_ADDR(log_default_initialized),TOUCH_LOG_ADDR(touch_log_color_reset),0,0);return;
 }
 if(!RECORD->parameter)RECORD->parameter=1000;
 touch_bootstrap_log(TOUCH_LOG_ADDR(log_config_loaded),RECORD->baseline,RECORD->parameter,TOUCH_LOG_ADDR(touch_log_color_reset));
}
