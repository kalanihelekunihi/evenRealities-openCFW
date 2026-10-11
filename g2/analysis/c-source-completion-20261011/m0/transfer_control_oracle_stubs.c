#include <stdint.h>
uint32_t case_tick_word2(void){return *(volatile uint32_t *)(uintptr_t)0x20000120u;}
uint32_t case_transfer_clock_config(uint32_t p){return p;}
