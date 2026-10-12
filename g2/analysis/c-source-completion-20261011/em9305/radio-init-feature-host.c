#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
#include "radio-init-feature-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();*(uint32_t*)0x805cac=0x806000;unsigned vectors=0;
for(unsigned presence=0;presence<16;presence++)for(unsigned count=0;count<256;count++){
for(unsigned i=0;i<4;i++)*(uint32_t*)(uintptr_t)(0x802954u+i*4)=(presence&(1u<<i))?0x12345678:0;
*(uint8_t*)0x806022=count;unsigned f=presence&1,s=presence&2,t=presence&4,u=presence&8;uint32_t low=u?3:0,hi=0;if(s&&u)low|=0xc0003300;if(u&&f){low|=0x2000008c;if(count>=2)hi|=448;}uint32_t ret;if(s){if(!f){low|=0x30;ret=low;}else{low|=count>=2?0x1f000070:0xf000070;if(t)low|=0xc00000;ret=!f;}}else ret=!f;if(f&&s&&u){low|=0x3fcc00;if(count>=2)hi|=575;ret=low;}uint32_t r=opencfw_em9305_init_features_3099cc(0xabcdef);if(r!=ret||*(uint32_t*)0x805b48!=low||*(uint32_t*)0x805b4c!=hi){fprintf(stderr,"bad presence%u count%u ret%x/%x low%x/%x high%x/%x\n",presence,count,r,ret,*(uint32_t*)0x805b48,low,*(uint32_t*)0x805b4c,hi);abort();}vectors++;}
for(unsigned flag=0;flag<65536;flag++)for(unsigned high=0;high<16;high++){uint32_t old=flag*0x10203u,expected=old;*(uint32_t*)0x805b34=flag;*(uint32_t*)0x805b30=high<<28;*(uint32_t*)0x805b54=old;unsigned changed=0;if(flag&(1u<<8)){expected|=1u<<9;changed=1;}if(flag&(1u<<14)){expected|=1u<<15;changed=1;}if(flag&(1u<<5)){expected|=1u<<6;changed=1;}if(high){expected|=1u;changed=1;}if(opencfw_em9305_init_features_308ff8(0xabcdef)!=(changed?expected:0xabcdef)||*(uint32_t*)0x805b54!=expected)abort();vectors++;}
printf("PASS %u feature source projections; all provider presence/count, lower16flags and high nibble; no native/hardware claim\n",vectors);return 0;}
