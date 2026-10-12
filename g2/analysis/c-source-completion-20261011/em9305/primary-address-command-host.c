#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
static unsigned entered,exited,seenA,seenB,stopA,stopB;
static uint32_t cbA(uint32_t n){if(n!=seenA++)abort();return n==stopA;}
static uint32_t cbB(uint32_t n){if(n!=seenB++)abort();return n==stopB;}
static uint32_t replacement(uint32_t n){if(n!=1u&&n!=2u)abort();seenA++;return 0;}
static uint32_t mutate(uint32_t n){if(n)abort();seenA++;*(uint32_t*)0x801308=(uintptr_t)replacement;return 0;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){entered++;return 77;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){if(*(uint32_t*)0x805a8c!=0x04030201||*(uint8_t*)0x805a7f!=1||*(uint16_t*)0x805a80!=257)abort();exited++;return 99;}
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
 volatile uint8_t *bytes=(volatile uint8_t *)address;
 uint32_t second=bytes[1],third=bytes[2],first=bytes[0];
 uint32_t sixth=bytes[5],fourth=bytes[3],fifth=bytes[4];
 uint32_t low=first|(second<<8)|(third<<16)|(fourth<<24);
 uint32_t high=fifth|(sixth<<8);
 return ((uint64_t)high<<32)|low;
}

#include "primary-address-command-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned vectors=0;uint8_t input[6]={1,2,3,4,0,0};
for(unsigned mask=0;mask<256;mask++)for(stopA=0;stopA<4;stopA++)for(stopB=0;stopB<4;stopB++){
*(uint8_t*)0x805a71=(mask&1)!=0;*(uint8_t*)0x805b91=(mask&2)!=0;*(uint8_t*)0x805a73=(mask&4)!=0;*(uint8_t*)0x804ffc=(mask&8)!=0;*(uint8_t*)0x805a74=(mask&16)!=0;*(uint8_t*)0x803bb8=(mask&32)!=0;*(uint32_t*)0x801308=(mask&64)?(uintptr_t)cbA:0;*(uint32_t*)0x801304=(mask&128)?(uintptr_t)cbB:0;entered=exited=seenA=seenB=0;unsigned expected=0;if((mask&3)==3)expected=12;else if(mask&4){if(mask&8)expected=12;else if((mask&64)&&stopA<3)expected=12;}if(!expected&&(mask&16)){if(mask&32)expected=12;else if((mask&128)&&stopB<3)expected=12;}uint32_t r=opencfw_em9305_command_primary_30de38((uintptr_t)input);if(r!=expected||entered!=!expected||exited!=entered)abort();
 vectors++;}
*(uint8_t*)0x805a71=*(uint8_t*)0x805a73=*(uint8_t*)0x805a74=0;
for(unsigned h=0;h<65536;h++){input[4]=h;input[5]=h>>8;entered=exited=0;uint32_t r=opencfw_em9305_command_primary_30de38((uintptr_t)input);unsigned expected=(h&0xc000)==0x8000?18:0;if(r!=expected||entered!=!expected||exited!=entered||(!expected&&*(uint32_t*)0x805a90!=h))abort();
 vectors++;}
input[4]=input[5]=0;seenA=entered=exited=0;*(uint8_t*)0x805a73=1;*(uint8_t*)0x804ffc=0;*(uint32_t*)0x801308=(uintptr_t)mutate;if(opencfw_em9305_command_primary_30de38((uintptr_t)input)||seenA!=3||entered!=1||exited!=1)abort();
 vectors++;
if(opencfw_em9305_primary_reset_mode_310718(0xf1234567)!=0xf1234567)abort();
 vectors++;
printf("PASS %u native-contract projections: gates/callbacks, all16-bit high addresses, fresh callback reload\n",vectors);return 0;}
