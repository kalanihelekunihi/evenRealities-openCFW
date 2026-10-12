#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t seed;static unsigned calls,mutation;
uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t v){return v&2?2:v&1?1:v&4;}
uint32_t opencfw_em9305_radio_access_raw_318878(void){++calls;if(mutation){*(uint16_t*)0x810006=2;*(uint32_t*)0x805c70=0x840000;*(uint16_t*)0x812006=0xbeef;}return seed;}
static const uint8_t opencfw_em9305_config_phy_values_33449d[7]={2u,1u,3u,1u,1u,1u,4u};
static inline uint32_t opencfw_em9305_config_extended_slot_stride(uint32_t i)
{return (i&65535u)*912u;}
/* Native3272d8..32739c: full extended link projection, PHY mapping, seed and slot metadata. */
void opencfw_em9305_config_extended_link_update_3272d8(uintptr_t link,uintptr_t input,uintptr_t row)
{
 uint32_t policy=*(volatile uint16_t *)(input+16u);
 *(volatile uint16_t *)(link+482u)=(uint16_t)policy;
 uint32_t modeword=*(volatile uint32_t *)(input+12u);
 *(volatile uint32_t *)(link+500u)=(modeword>>16u)|(modeword<<16u);
 uint32_t mode=*(volatile uint8_t *)(input+18u),multiplier=*(volatile uint8_t *)(row+1u);
 *(volatile uint8_t *)(link+484u)=(uint8_t)mode;
 *(volatile uint8_t *)(link+504u)=(uint8_t)multiplier;
 uint32_t first_length=*(volatile uint16_t *)(row+2u),second_length=*(volatile uint16_t *)(row+4u);
 uint32_t id=*(volatile uint8_t *)row;
 *(volatile uint16_t *)(link+486u)=(uint16_t)first_length;
 *(volatile uint16_t *)(link+488u)=(uint16_t)second_length;
 uint32_t first_time=*(volatile uint32_t *)(input+4u),second_time=*(volatile uint32_t *)(input+8u);
 uint32_t first_phy=*(volatile uint8_t *)(row+10u);
 *(volatile uint8_t *)(link+12u)=(uint8_t)id;
 *(volatile uint32_t *)(link+492u)=first_time;
 *(volatile uint32_t *)(link+496u)=second_time;
 uint32_t mapped=opencfw_em9305_radio_phy_project_3183d4(first_phy)-2u;
 uint32_t value=1u;if((uint8_t)mapped<=6u)value=opencfw_em9305_config_phy_values_33449d[(int8_t)mapped];
 uint32_t second_phy=*(volatile uint8_t *)(row+11u);
 *(volatile uint8_t *)(link+480u)=(uint8_t)value;
 mapped=opencfw_em9305_radio_phy_project_3183d4(second_phy)-2u;
 value=1u;if((uint8_t)mapped<7u)value=opencfw_em9305_config_phy_values_33449d[(int8_t)mapped];
 *(volatile uint8_t *)(link+481u)=(uint8_t)value;
 uint32_t retries=*(volatile uint16_t *)(row+12u);
 *(volatile uint16_t *)(link+512u)=(uint16_t)retries;
 uint32_t seed=opencfw_em9305_radio_access_raw_318878();
 uint32_t slot=*(volatile uint16_t *)(link+6u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t offset=opencfw_em9305_config_extended_slot_stride(slot);
 *(volatile uint32_t *)(link+372u)=seed;
 uint32_t a=*(volatile uint16_t *)(row+6u),b=*(volatile uint16_t *)(row+8u);
 uint32_t metadata=*(volatile uint32_t *)(base+offset+324u);
 uint32_t kind=*(volatile uint16_t *)(base+offset+382u);
 *(volatile uint16_t *)(link+448u)=(uint16_t)a;
 *(volatile uint16_t *)(link+444u)=(uint16_t)b;
 *(volatile uint32_t *)(link+376u)=metadata;
 *(volatile uint16_t *)(link+468u)=(uint16_t)kind;
}

static unsigned char expected[656];
static void w16(unsigned off,uint16_t v){memcpy(expected+off,&v,2);}static void w32(unsigned off,uint32_t v){memcpy(expected+off,&v,4);}
static unsigned mapped(unsigned v){return v&2?2:v&1?1:v&4?3:1;}
int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned a=0;a<256;++a)for(unsigned b=0;b<256;++b)for(unsigned m=0;m<2;++m){memset((void*)0x810000,0xa5,656);memset((void*)0x811000,0,32);memset((void*)0x812000,0,14);*(uint16_t*)0x810006=1;*(uint32_t*)0x805c70=0x830000;*(uint16_t*)0x811010=0xfedc;*(uint32_t*)0x81100c=0x12345678;*(uint8_t*)0x811012=7;*(uint32_t*)0x811004=0xffffffff;*(uint32_t*)0x811008=0x80000000;*(uint8_t*)0x812000=239;*(uint8_t*)0x812001=17;*(uint16_t*)0x812002=0xabcd;*(uint16_t*)0x812004=0xdcba;*(uint16_t*)0x812006=1234;*(uint16_t*)0x812008=4321;*(uint8_t*)0x81200a=a;*(uint8_t*)0x81200b=b;*(uint16_t*)0x81200c=0x0f0e;
*(uint32_t*)(uintptr_t)(0x830000+912+324)=0x11223344;*(uint16_t*)(uintptr_t)(0x830000+912+382)=0x5566;*(uint32_t*)(uintptr_t)(0x840000+1824+324)=0x778899aa;*(uint16_t*)(uintptr_t)(0x840000+1824+382)=0xbbcc;seed=0xcafebabe;calls=0;mutation=m;memcpy(expected,(void*)0x810000,656);
w16(482,0xfedc);w32(500,0x56781234);expected[484]=7;expected[504]=17;w16(486,0xabcd);w16(488,0xdcba);expected[12]=239;w32(492,0xffffffff);w32(496,0x80000000);expected[480]=mapped(a);expected[481]=mapped(b);w16(512,0x0f0e);if(m)w16(6,2);w32(372,seed);w16(448,m?0xbeef:1234);w16(444,4321);w32(376,m?0x778899aa:0x11223344);w16(468,m?0xbbcc:0x5566);
opencfw_em9305_config_extended_link_update_3272d8(0x810000,0x811000,0x812000);if(calls!=1||memcmp(expected,(void*)0x810000,656))return 3;++cases;}
printf("PASS %u\n",cases);}
