/* Independent 0x8aac write dispatcher. Provider bodies are unresolved and
 * deliberately explicit test boundaries; no flash implementation is supplied. */
#include <stdint.h>
extern uint32_t eeprom_simple_boundary(uint32_t,uint8_t *,uint32_t,void *);
extern uint32_t eeprom_extended_boundary(uint32_t,uint8_t *,uint32_t,void *);
uint32_t touch_eeprom_write_dispatch(uint32_t address,uint8_t *data,uint32_t size,void *context) {
 if(!size)return 0x093e0000u;
 uint8_t *c=(uint8_t *)context;
 if(address+size>*(uint32_t *)(c+8))return 0x093e0000u;
 if(!data)return 0x093e0000u;
 return c[13] ? eeprom_simple_boundary(address,data,size,context) : eeprom_extended_boundary(address,data,size,context);
}
