#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_callback_30e840(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_callback_327dc8(void);
extern uint32_t opencfw_em9305_init_callback_3280c8(void);
extern uint32_t opencfw_em9305_init_callback_325450(void);
static unsigned kind,sequence;
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){volatile uint8_t *b=(void *)p;assert(b[0]==0&&b[1]==0&&b[3]==0);assert(b[2]==kind);return 0x12345678;}
uint32_t opencfw_em9305_common_init_302e90(void){assert(sequence==0);sequence=1;return 0xdead;}
void *opencfw_em9305_memset(void *p,int v,unsigned long n){if(p==(void *)0x8052d4){assert(sequence==1);assert(v==0&&n==304);sequence=2;}else assert(v==255&&n==32);return memset(p,v,n);}
uint32_t opencfw_em9305_init_lower_30e9e0(uint32_t v){assert(sequence==2&&v==0x8052d4);sequence=3;return 0xabcdef;}
uint32_t opencfw_em9305_callback_child_322e44(uintptr_t p){for(unsigned i=0;i<32;i++)assert(((uint8_t *)p)[i]==255);return 0x76543210;}
int main(void){assert(mmap((void *)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);
for(unsigned i=0;i<256;i++){uint8_t record[8];memset(record,0xa5,8);kind=i?54:52;assert(opencfw_em9305_init_callback_30e840((uintptr_t)record,i)==0x12345678);for(unsigned j=4;j<8;j++)assert(record[j]==0xa5);*(volatile uint8_t *)0x805b82=i;assert(opencfw_em9305_init_callback_325450()==(i?i:0x76543210));sequence=0;memset((void *)0x8052d3,0xa5,306);assert(opencfw_em9305_init_callback_3280c8()==0xabcdef&&sequence==3);for(unsigned j=0;j<304;j++)assert(*(volatile uint8_t *)(uintptr_t)(0x8052d4+j)==0);assert(*(volatile uint8_t *)0x8052d3==0xa5&&*(volatile uint8_t *)0x805404==0xa5);kind=63;assert(opencfw_em9305_init_callback_327dc8()==0x12345678);}
puts("PASS 256 callback header, branch, record and child-order cases");}
