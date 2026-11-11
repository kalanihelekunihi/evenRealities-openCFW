/* Native SpO2 transition0x36282 and channel state update0x36c32. */
#include <stdint.h>
#include "native_spo2_transition.h"
static uint8_t U(uintptr_t p,uint32_t o){return *(const volatile uint8_t *)(p+o);}
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static void SB(uintptr_t p,uint32_t o,uint8_t v){*(volatile uint8_t *)(p+o)=v;}
void r1_goodix_native_spo2_channel_transition(void *state,const void *summary,const void *filter)
{
 uintptr_t s=(uintptr_t)state;uint8_t previous=U((uintptr_t)filter,22);
 SB(s,4,previous);uint8_t flags=U((uintptr_t)summary,41);
 if(previous==0)SB(s,5,flags!=0);
 else if(previous==1){SB(s,5,0);if(flags)SB(s,6,(uint8_t)(U(s,6)+1u));else SB(s,6,0);}
}
void r1_goodix_spo2_transition(void *state_owner,void *summary,const void *descriptor,void *filter_owner)
{
 (void)descriptor;uintptr_t filter=W((uintptr_t)filter_owner,0);
 uintptr_t record=W((uintptr_t)summary,8),state=W((uintptr_t)state_owner,0);
 r1_goodix_native_spo2_channel_transition((void *)state,(const void *)record,(const void *)filter);
}
