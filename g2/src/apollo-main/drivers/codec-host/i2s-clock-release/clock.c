#include <stdint.h>
extern uint32_t audio_clock_save_disable_irq(void);
uint32_t audio_i2s_power_command(uint32_t enabled){
 volatile uint32_t *reg=(void*)0x40004044u;
 *reg=(*reg&~1u)|((uint8_t)enabled!=0);return 0;
}
uint32_t audio_i2s_release_group4(uint32_t peripheral){
 uint32_t bit=1u<<((uint8_t)peripheral&31u),word=(uint8_t)peripheral>>5;
 volatile uint32_t *clients=(void*)(0x20073324u+32);
 if(!(clients[word]&bit))return 0;
 uint32_t mask=audio_clock_save_disable_irq();clients[word]&=~bit;
 if(!(clients[0]|clients[1]))audio_i2s_power_command(0);
 __asm__ volatile("msr primask, %0"::"r"(mask):"memory");return 0;
}
