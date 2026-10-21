/* Independent5fc6/6044/6078/60ea; native critical-section assembly. */
#include "pins.h"
static void hsiom(volatile uint32_t *port,uint32_t pin,uint32_t value){uint32_t address=((((uint32_t)port+0xbffc0000u)>>8)+0x400200u)<<8;volatile uint32_t *reg=(volatile uint32_t *)address;uint32_t shift=pin*4;*reg=(*reg&~(15u<<shift))|((value&15u)<<shift);}
static void drive(volatile uint32_t *port,uint32_t pin,uint32_t value){uint32_t shift=pin*3;port[2]=(port[2]&~(7u<<shift))|((value&7u)<<shift);port[6]=(port[6]&~(1u<<pin))|(((value>>3)&1u)<<pin);}
void touch_config_pin(volatile uint32_t *port,uint32_t pin,uint32_t dm,uint32_t mux,uint32_t analog){uint32_t irq;__asm__ volatile("mrs %0, primask\n cpsid i":"=r"(irq)::"memory");if(!mux){hsiom(port,pin,0);drive(port,pin,dm);}else{drive(port,pin,dm);hsiom(port,pin,mux);}uint32_t mask=(1u<<pin)&255u;if(analog)port[9]|=mask;else port[9]&=~mask;__asm__ volatile("msr primask, %0"::"r"(irq):"memory");}
void touch_config_electrodes(uint32_t dm,uint32_t mux,uint32_t output,uint32_t analog,const uint8_t *c){const uint8_t *common=*(const uint8_t **)c,*p=*(const uint8_t **)(c+20);for(uint32_t i=0;i<*(const uint16_t *)(common+12);i++,p+=8){volatile uint32_t *port=*(volatile uint32_t **)p;uint32_t pin=p[4];touch_config_pin(port,pin,dm,mux,analog);port[output?16:17]=1u<<pin;}}
void touch_config_shields(uint32_t dm,uint32_t mux,uint32_t analog,const uint8_t *c){const uint8_t *common=*(const uint8_t **)c,*p=*(const uint8_t **)(c+24);for(uint32_t i=0;i<common[44];i++,p+=8){volatile uint32_t *port=*(volatile uint32_t **)p;uint32_t pin=p[4];touch_config_pin(port,pin,dm,mux,analog);port[17]=1u<<pin;}}
void touch_config_cmod(uint32_t dm,uint32_t mux,uint32_t analog,const uint8_t *c){const uint8_t *common=*(const uint8_t **)c,*ch=*(const uint8_t **)(common+8);touch_config_pin(*(volatile uint32_t **)(ch+8),ch[12],dm,mux,analog);touch_config_pin(*(volatile uint32_t **)(ch+16),ch[20],dm,mux,analog);}
void touch_mode_ios(uint8_t *c){touch_config_electrodes(9,0,0,1,c);}
void touch_mode_shield(uint8_t *c){touch_config_shields(9,0,1,c);}
void touch_mode_cmod(uint8_t *c){touch_config_cmod(9,0,1,c);}
