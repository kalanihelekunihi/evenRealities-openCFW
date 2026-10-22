#include "initialize.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
uint32_t pcm_variant_initialize(void) {
 uint32_t major=W(0x4002000c)&255, rev=W(0x200001e8), date=W(0x2007198c);
 B(0x20074f6e)=major==0x21&&rev==2;
 B(0x20074f6f)=(major==0x21&&(rev==2||rev==3))||(major==0x22&&rev==0);
 uint32_t screened=((date&0x3fe00000)==0x31800000&&((date>>16)&31)>=20&&(date&65535)==0)||(((date>>25)&31)>=25&&(date&65535)==0);
 B(0x20074f70)=(major==0x22&&rev==1)||(major==0x23&&rev==0&&!screened);
 return 0;
}
/* The original-trim capture block (g_bOrigTrimsStored) is part of upstream
 * am_hal_pwrctrl_low_power_init (0x47FAE8) in the am_hal_pwrctrl.c unit. */
uint32_t pcm_early_initialize_noop(void){return 0;}
uint32_t pcm_middle_reset_noop(void){return 0;}
