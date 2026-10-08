/* Independent reconstruction of locked-image provider adapters. */
#include <stdint.h>
#include "provider.h"
void touch_storage_copy(uint32_t handle,uint32_t address,uint32_t size,uint8_t *data) {
 (void)handle;const uint8_t *src=(const uint8_t *)address;
 for(uint32_t i=0;i<size;i++)data[i]=src[i];
}
uint32_t touch_storage_zero(uint32_t handle,uint32_t address,uint32_t size) {
 (void)handle;uint8_t zeros[512];for(unsigned i=0;i<512;i++)((volatile uint8_t *)zeros)[i]=0;
 if(size&127u)return 0x06160002u;
 uint32_t end=address+size;for(uint32_t a=address;a<end;a+=128)(void)touch_flash_write_row(a,zeros);
 return 0;
}
uint32_t touch_storage_program(uint32_t handle,uint32_t address,uint32_t size,const uint8_t *data) {
 (void)handle;if(size&127u)return 0x06160002u;
 uint32_t end=address+size;for(uint32_t a=address;a<end;a+=128,data+=128)(void)touch_flash_write_row(a,data);
 return 0;
}
uint32_t touch_eeprom_program_gate(uint32_t address,const uint8_t *data,const uint8_t *context) {
 uint32_t *provider=*(uint32_t **)(context+28);
 uint32_t (*check)(uint32_t,uint32_t,uint32_t)=(void *)provider[11];
 uint32_t (*erase)(uint32_t,uint32_t,uint32_t)=(void *)provider[7];
 uint32_t (*program)(uint32_t,uint32_t,uint32_t,const uint8_t *)=(void *)provider[6];
 uint32_t physical=*(const uint16_t *)(context+2);uint32_t needs=check(provider[0],address,physical);
 uint32_t step=*(const uint32_t *)(context+4);if(step>physical)physical=step;
 if(!context[15])return 0;
 if(needs && erase(provider[0],address,physical))return 0x093e0003u;
 return program(provider[0],address,physical,data) ? 0x093e0003u : 0;
}
uint32_t touch_storage_no_erase(uint32_t handle,uint32_t address,uint32_t size) {
 (void)handle;(void)address;(void)size;return 0;
}
