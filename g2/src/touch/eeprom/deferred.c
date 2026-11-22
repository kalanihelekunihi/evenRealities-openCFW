/* Reconstructed deferred dispatch and bounded configuration-write adapter.
 * Real reconstructed EEPROM/flash choreography; only SROM is externally modeled. */
#include "cy_syslib.h"
#include <stdint.h>
#include "../application/ram_state.h"
extern uint32_t touch_eeprom_write(uint32_t,const uint8_t *,uint32_t,uint8_t *);
static uint32_t config_persist(void) {
 uint8_t *config=(uint8_t *)&touch_saved_record_ram;
 *(uint32_t *)config=0x45564e55u;
 if(!touch_eeprom_ready_ram)return 1u;
 uint32_t status=touch_eeprom_write(0,config,8,touch_eeprom_context_ram);
 return status==0u || status==0x093e0004u ? 0u : 3u;
}
/* Stock 0x00003A80 (touch_deferred_0780_process) */
void touch_deferred(void) {
 uint32_t mask=Cy_SysLib_EnterCriticalSection();
 uint8_t restart=touch_restart_ram;
 uint8_t persist=touch_persist_ram;
 uint16_t threshold=touch_application_threshold;
 touch_restart_ram=0;
 touch_persist_ram=0;
 Cy_SysLib_ExitCriticalSection(mask);
 if(restart) {
  uint8_t *state=touch_gesture_state_ram;
  for(unsigned i=0;i<80;i++)state[i]=0;
  *(uint16_t *)state=threshold ? threshold : 1000u;
 }
 if(persist)(void)config_persist(); /* actual logger is return-zero leaf */
}
