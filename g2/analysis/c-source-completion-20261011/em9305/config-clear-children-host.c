#include <stdint.h>
#include <stdio.h>
#include <string.h>
static unsigned calls;
uint32_t opencfw_em9305_command_count_down_30e48c(void){if(calls!=0)__builtin_trap();++calls;return 0xff;}
uint32_t opencfw_em9305_common_release_304588(uint32_t role){if(calls!=1||role!=1)__builtin_trap();++calls;return 0xdeadbeef;}
/* Native31b2f8..31b2fc: channel byte23, returned in delay slot. */
uint32_t opencfw_em9305_config_channel_busy_31b2f8(uintptr_t channel)
{return *(volatile uint8_t *)(channel+23u);}
/* Native31ad88..31ad90: active-byte clear; R0 pointer remains intact. */
uint32_t opencfw_em9305_config_link_clear_31ad88(uintptr_t link)
{*(volatile uint8_t *)link=0u;return (uint32_t)link;}
/* Native31ad64..31ad88: exact channel clear stores, decrement and release1 result. */
uint32_t opencfw_em9305_config_channel_clear_31ad64(uintptr_t channel)
{
 *(volatile uint8_t *)(channel+112u)=0u;
 *(volatile uint16_t *)(channel+108u)=0u;
 *(volatile uint8_t *)(channel+23u)=0u;
 *(volatile uint8_t *)(channel+4u)=0u;
 *(volatile uint8_t *)(channel+3u)=0u;
 *(volatile uint16_t *)channel=0u;
 (void)opencfw_em9305_command_count_down_30e48c();
 return opencfw_em9305_common_release_304588(1u);
}

int main(void){uint8_t channel[140],expected[140];unsigned cases=0;for(unsigned v=0;v<256;++v){memset(channel,v,140);memcpy(expected,channel,140);if(opencfw_em9305_config_channel_busy_31b2f8((uintptr_t)channel)!=v)return 1;calls=0;
 for(unsigned i=0;i<2;++i)expected[i]=0;
 expected[3]=expected[4]=expected[23]=expected[108]=expected[109]=expected[112]=0;
 if(opencfw_em9305_config_channel_clear_31ad64((uintptr_t)channel)!=0xdeadbeef||calls!=2||memcmp(expected,channel,140))return 2;
 memset(channel,v,140);memcpy(expected,channel,140);expected[0]=0;if(opencfw_em9305_config_link_clear_31ad88((uintptr_t)channel)!=(uint32_t)(uintptr_t)channel||memcmp(expected,channel,140))return 3;cases+=3;
 }printf("PASS %u\n",cases);return 0;}
