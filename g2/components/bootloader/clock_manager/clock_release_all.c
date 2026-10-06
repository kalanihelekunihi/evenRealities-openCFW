/* SPDX-License-Identifier: MIT. Locked bootloader 4223d8.
 * Releases every registered class and ignores each release result. */
#include "clock_manager.h"
uint32_t opencfw_bl_clock_release_all(uint32_t user_register) {
 uint8_t user=(uint8_t)user_register;
 if(user>=57u)return 6u;
 for(uint32_t id=0;id<7u;++id) {
  volatile uint32_t *word=(volatile uint32_t *)(uintptr_t)(0x20026e74u+(id*2u+(user>>5))*4u);
  if((*word&(1u<<(user&31u)))!=0u)(void)clock_release(id,user);
 }
 return 0u;
}
