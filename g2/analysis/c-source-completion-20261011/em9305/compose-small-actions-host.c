#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include "compose-small-actions-prepared.c"
int main(void){_Alignas(4) uint8_t r[288],o[16];unsigned cases=0;
for(unsigned seed=0;seed<65536;seed++){
 for(unsigned i=0;i<288;i++)r[i]=(uint8_t)((seed*17u+i*31u)^(seed>>8));
 for(unsigned i=0;i<16;i++)o[i]=0xa5;
 if(opencfw_em9305_compose_action_3237e8((uintptr_t)r,(uintptr_t)o)!=9||o[0]!=8||o[1]!=40)abort();
 unsigned offsets[7]={84,85,86,87,88,92,93};for(unsigned i=0;i<7;i++)if(o[i+2]!=r[offsets[i]])abort();
 for(unsigned i=9;i<16;i++)if(o[i]!=0xa5)abort();
 if(opencfw_em9305_compose_action_323820((uintptr_t)r,(uintptr_t)o)!=10||o[0]!=9||o[1]!=50)abort();
 for(unsigned i=0;i<8;i++)if(o[i+2]!=r[i+276])abort();
 for(unsigned i=10;i<16;i++)if(o[i]!=0xa5)abort();
 cases+=2;
}printf("PASS %u controlled encoding cases\n",cases);return 0;}
