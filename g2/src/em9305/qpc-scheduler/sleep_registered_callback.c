/* Native registered callback 0x3128e4..0x312918. Its incidental R0 is
 * unused by the source registration contract; no invented return value. */
#include <stdint.h>
extern void opencfw_em9305_sleep_rom_restore(uint32_t); /* 0x103b7c */
static uintptr_t context(void) { return *(volatile uint32_t *)(uintptr_t)0x80fb8cu; }
void opencfw_em9305_sleep_registered_callback(void)
{
 volatile uint32_t *timer=(volatile uint32_t *)(uintptr_t)0xf0045cu;
 uint32_t first,second;
 do { first=*timer; second=*timer; } while(first!=second);
 *(volatile uint32_t *)(context()+16u)=first;
 if(*(volatile uint8_t *)(context()+45u)!=0 && *(volatile uint8_t *)(context()+44u)==0)
  opencfw_em9305_sleep_rom_restore(0);
}
