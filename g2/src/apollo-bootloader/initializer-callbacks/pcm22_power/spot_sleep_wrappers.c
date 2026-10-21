/* Locked f89a4c46 wrappers 0x41cd1a and 0x41cdb8; callback bodies remain providers. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t power_state_wrapper(uint32_t stimulus,uint32_t on,uint8_t *args){
 if(!W(0x20026e3c))return 0;
 return ((uint32_t(*)(uint32_t,uint32_t,uint8_t *))(uintptr_t)W(0x20026e3c))((uint8_t)stimulus,(uint8_t)on,args);
}
void boost_service_wrapper(void){if(W(0x20026e64))((void(*)(void))(uintptr_t)W(0x20026e64))();}
