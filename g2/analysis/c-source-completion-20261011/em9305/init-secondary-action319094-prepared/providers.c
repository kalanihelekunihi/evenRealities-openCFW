#include <stdint.h>
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
/* Complete324768..3247d0; output18B, native R0 is final source byte. */
uint32_t opencfw_em9305_init_secondary_fill_324768(uintptr_t record,uint8_t *output)
{
 (void)opencfw_em9305_memset(output,0u,18u);
 uint32_t kind=*(volatile uint8_t *)(record+716u);
 uint32_t high=*(volatile uint32_t *)(record+724u);
 uint32_t low=*(volatile uint32_t *)(record+720u);
 output[0]=(uint8_t)kind;
 (void)opencfw_em9305_radio_address_write_3045e8((uintptr_t)(output+2u),low,high);
 uint32_t time=*(volatile uint32_t *)(record+252u);
 uint32_t mode=*(volatile uint8_t *)(record+717u);
 uint64_t product=(uint64_t)time*0x1a36e3u;
 uint32_t marker=*(volatile uint8_t *)(record+256u);
 uint32_t option=*(volatile uint8_t *)(record+776u);
 output[1]=(uint8_t)mode;output[12]=(uint8_t)marker;
 output[8]=(uint8_t)option;
 *(uint16_t *)(void *)(output+10u)=(uint16_t)(product>>31u);
 uint32_t value=*(volatile uint8_t *)(record+512u);output[13]=(uint8_t)value;
 value=*(volatile uint8_t *)(record+513u);output[14]=(uint8_t)value;
 value=*(volatile uint8_t *)(record+514u);output[15]=(uint8_t)value;
 value=*(volatile uint8_t *)(record+515u);output[16]=(uint8_t)value;
 return value;
}
/* Complete30e928..30e984. Holes5,17,25..27 are unowned native stack
 * bytes; source owns only fields initialized by native stores. */
uint32_t opencfw_em9305_init_secondary_event_30e928(uint32_t code,uint32_t slot,uint8_t *input,uint32_t enabled)
{
 _Alignas(4) uint8_t event[28];
 event[4]=(uint8_t)code;*(uint32_t *)(void *)event=0x1e0000u;
 uint32_t first=*(uint16_t *)(void *)input;input+=2u;
 *(uint16_t *)(void *)(event+6u)=(uint16_t)slot;
 *(uint16_t *)(void *)(event+8u)=(uint16_t)first;
 uint32_t option=input[6],time=*(uint16_t *)(void *)(input+8u),marker=input[10];
 *(uint16_t *)(void *)(event+10u)=0u;*(uint16_t *)(void *)(event+12u)=0u;*(uint16_t *)(void *)(event+14u)=0u;
 event[16]=(uint8_t)option;*(uint16_t *)(void *)(event+18u)=(uint16_t)time;
 event[20]=(uint8_t)marker;uint32_t flag=enabled!=0u?input[11]:0u;
 uint32_t pair=*(uint16_t *)(void *)(input+12u),last=input[14];
 event[21]=(uint8_t)flag;*(uint16_t *)(void *)(event+22u)=(uint16_t)pair;event[24]=(uint8_t)last;
 (void)opencfw_em9305_radio_address_copy_304604((uintptr_t)(event+10u),(uintptr_t)input);
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
