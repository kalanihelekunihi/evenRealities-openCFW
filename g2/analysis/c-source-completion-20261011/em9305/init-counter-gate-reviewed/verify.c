#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
extern uint32_t opencfw_em9305_init_transition_gate_3168e4(void);
extern uint32_t opencfw_em9305_init_transition_count_down_320068(void);
uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==1);*(uint8_t*)0x805a74=123;return 7;}
int main(void){assert(mmap((void*)0x805000,4096,3,0x32,-1,0)==(void*)0x805000);for(unsigned n=0;n<256;n++){for(unsigned enabled=0;enabled<2;enabled++){*(uint8_t*)0x805b9d=enabled;*(uint8_t*)0x805a79=n;*(uint8_t*)0x805a76=n;*(uint8_t*)0x805a71=99;assert(opencfw_em9305_init_transition_gate_3168e4()==(enabled?0x805a76:0));assert(*(uint8_t*)0x805a71==0&&*(uint8_t*)0x805a79==(uint8_t)(n-1)&&*(uint8_t*)0x805a76==(uint8_t)(n-enabled));}*(uint8_t*)0x805a74=n;*(uint8_t*)0x805a79=n;assert(opencfw_em9305_init_transition_count_down_320068()==0x805a79);assert(*(uint8_t*)0x805a74==122&&*(uint8_t*)0x805a79==(uint8_t)(n-1));}puts("PASS768 connected counter/gate paths");}
