/* Reconstructed deferred dispatch and bounded configuration-write adapter.
 * Real reconstructed EEPROM/flash choreography; only SROM is externally modeled. */
#include "cy_syslib.h"
#include <stdint.h>
extern uint32_t touch_eeprom_write(uint32_t,const uint8_t *,uint32_t,uint8_t *);
static uint32_t config_persist(void) {
 uint8_t *config=(uint8_t *)0x200009d0u;
 *(uint32_t *)config=0x45564e55u;
 if(!*(uint8_t *)0x200008c4u)return 1u;
 uint32_t status=touch_eeprom_write(0,config,8,(void *)0x200008c8u);
 return status==0u || status==0x093e0004u ? 0u : 3u;
}
void touch_deferred(void) {
 uint32_t mask=Cy_SysLib_EnterCriticalSection();
 uint8_t restart=*(volatile uint8_t *)0x200009ceu;
 uint8_t persist=*(volatile uint8_t *)0x200009cdu;
 uint16_t threshold=*(volatile uint16_t *)0x200004e8u;
 *(volatile uint8_t *)0x200009ceu=0;
 *(volatile uint8_t *)0x200009cdu=0;
 Cy_SysLib_ExitCriticalSection(mask);
 if(restart) {
  uint8_t *state=(uint8_t *)0x20000940u;
  for(unsigned i=0;i<80;i++)state[i]=0;
  *(uint16_t *)state=threshold ? threshold : 1000u;
 }
 if(persist)(void)config_persist(); /* actual logger is return-zero leaf */
}
