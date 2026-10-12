#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
/* Native3185e8..318670: two PHY contributions, feature reads remain separately live. */
uint32_t opencfw_em9305_config_link_time_3185e8(uint32_t first_phy,uint32_t second_phy,uint32_t first_length,uint32_t second_length)
{
 uint32_t sum=0u;
 if(first_phy==1u)sum=(first_length<<3u)+112u;
 else if(first_phy==2u)sum=60u+(first_length<<2u);
 else if(first_phy==3u){uint32_t n=first_length+4u;
  sum=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 sum+=150u;
 if(second_phy==1u)sum+=(second_length<<3u)+112u;
 else if(second_phy==2u)sum+=(second_length<<2u)+60u;
 else if(second_phy==3u){uint32_t n=second_length+4u;
  sum+=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return sum+*(volatile uint16_t *)(config+54u)+150u;
}
/* Native318670..31869e: early second-slot gate, equality and first empty attachment. R1 preserved by native routine. */
uint32_t opencfw_em9305_config_attach_link_318670(uintptr_t channel,uintptr_t link)
{
 if(*(volatile uint32_t *)(channel+92u))return 0u;
 for(uint32_t i=0u;i<2u;++i){uintptr_t cell=channel+88u+i*4u;uint32_t value=*(volatile uint32_t *)cell;
  if(value==(uint32_t)link)return 1u;
  if(value==0u){*(volatile uint32_t *)cell=(uint32_t)link;return 1u;}
 }
 return 0u;
}

static uint32_t reference(uint32_t r0,uint32_t r1,uint32_t r2,uint32_t r3){uint32_t r12;
 if(r0==3){r0=r2+4;r12=(*(uint8_t*)0x805a86&16)?(r0<<4)+462:(r0<<6)+720;}else{r12=60;if(r0==2)r12+=r2<<2;else{r12=0;if(r0==1){r0=r2<<3;r12=r0+(56<<1);}}}
 r12+=150;
 if(r1==3){r0=r3+4;r12+=(*(uint8_t*)0x805a86&16)?(r0<<4)+462:(r0<<6)+720;}else if(r1==2){r12+=r3<<2;r12+=60;}else if(r1==1){r12+=r3<<3;r12+=56<<1;}
 r0=*(uint16_t*)0x813036;r0+=r12;return r0+150;
}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x813000;unsigned cases=0;uint32_t lengths[]={0,1,255,4095,65535,0x80000000u,0xffffffffu};
 for(unsigned f=0;f<2;++f)for(unsigned a=0;a<256;++a)for(unsigned b=0;b<256;++b)for(unsigned k=0;k<7;++k){*(uint8_t*)0x805a86=f?16:0;*(uint16_t*)0x813036=k*10922;uint32_t x=lengths[k],y=lengths[6-k];if(opencfw_em9305_config_link_time_3185e8(a,b,x,y)!=reference(a,b,x,y))return 3;++cases;}
 uint32_t values[]={0,1,0x820000,0xffffffff};
 for(unsigned a=0;a<4;++a)for(unsigned b=0;b<4;++b)for(unsigned c=0;c<4;++c){uint32_t original[32],expected[32];memset(original,0xa5,sizeof(original));original[22]=values[a];original[23]=values[b];memcpy(expected,original,sizeof(original));unsigned answer=0;if(!values[b]){if(values[a]==values[c])answer=1;else if(!values[a]){answer=1;expected[22]=values[c];}else{answer=1;expected[23]=values[c];}}memcpy((void*)0x814000,original,sizeof(original));if(opencfw_em9305_config_attach_link_318670(0x814000,values[c])!=answer||memcmp((void*)0x814000,expected,sizeof(expected)))return 4;++cases;}
 printf("PASS %u\n",cases);}
