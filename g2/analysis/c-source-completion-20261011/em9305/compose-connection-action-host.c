#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
#include "compose-connection-action-prepared.c"
static uint32_t rd(const uint8_t*r,unsigned n,unsigned width){uint32_t v=0;for(unsigned i=0;i<width;i++)v|=(uint32_t)r[n+i]<<(8*i);return v;}
int main(void){_Alignas(4) uint8_t r[288],o[64],g[64];unsigned cases=0;
for(unsigned seed=0;seed<65536;seed++){
 for(unsigned i=0;i<288;i++)r[i]=(uint8_t)((seed*17u+i*31u)^(seed>>8));
 memset(o,0xa5,64);memset(g,0xa5,64);
 g[0]=(uint8_t)(r[178]+1);g[1]=44;g[2]=r[186];
 g[3]=(uint8_t)(((rd(r,186,2)&0x3f00)+((r[188]&1u)<<14)+(rd(r,190,2)<<15))>>8);
 g[4]=(uint8_t)(rd(r,190,2)>>1);g[5]=(uint8_t)(((rd(r,190,2)<<15)|((uint32_t)r[192]<<27))>>24);
 g[6]=(uint8_t)((r[194]<<5)|r[193]);g[7]=(uint8_t)(((rd(r,196,4)<<8)|(r[194]<<5))>>8);g[8]=r[197];
 g[9]=(uint8_t)(((rd(r,196,4)<<8)|((uint32_t)r[200]<<28))>>24);
 g[10]=r[204];g[11]=r[205];g[12]=(uint8_t)(((r[208]<<20)|rd(r,204,4))>>16);
 g[13]=(uint8_t)(((r[208]<<20)|rd(r,204,4)|(rd(r,210,2)<<24))>>24);g[14]=0;
 g[15]=r[212];g[16]=r[213];g[17]=r[214];g[18]=r[215];g[19]=r[216];g[20]=r[217];
 g[21]=(uint8_t)(((rd(r,220,2)<<20)|rd(r,216,4))>>16);g[22]=(uint8_t)(((rd(r,220,2)<<20)|rd(r,216,4))>>24);
 for(unsigned i=23;i<=28;i++)g[i]=r[i+199];
 g[29]=(uint8_t)(((r[232]<<5)-32u)|rd(r,228,4));for(unsigned i=30;i<=33;i++)g[i]=r[i+206];
 g[34]=(uint8_t)((rd(r,240,4)&127u)+(r[244]<<7));
 if(r[245]){memcpy(g+35,r+246,8);memcpy(g+43,r+254,16);}
 if(opencfw_em9305_compose_action_32366c((uintptr_t)r,(uintptr_t)o)!=(uint8_t)(r[178]+2)||memcmp(o,g,64))abort();
 cases++;
}printf("PASS %u controlled connection encodings\n",cases);return 0;}
