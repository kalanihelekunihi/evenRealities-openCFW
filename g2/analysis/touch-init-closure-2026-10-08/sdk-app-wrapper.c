#include <stdint.h>
#include "init.h"
const touch_eeprom_configuration touch_factory_eeprom_configuration={256,0,2,1,1,0};
uint32_t touch_application_eeprom_init(void){
 uint8_t *flag=(uint8_t *)0x200008c4u;if(*flag)return 0;
 uint8_t *cfg=(uint8_t *)0x200004c0u;*(uint32_t *)(cfg+8)=0xe400u;uint32_t status=touch_eeprom_init(cfg,(uint8_t *)0x200008c8u);
 if(!status||status==0x093e0004u){*flag=1;return 0;}return 1;
}
