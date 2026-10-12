#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_callback_child_322e44(uintptr_t);
static unsigned state,seq;static uint8_t data[32];
void *opencfw_em9305_memset(void *p,int v,unsigned long n){assert(seq==0&&v==0&&n==38);seq=1;*(volatile uint8_t *)0x805b82=state;return memset(p,v,n);}
void *opencfw_em9305_memcpy(void *p,const void *s,uint32_t n){assert(seq==1&&n==32&&s==data);assert(((uint8_t *)p)[-3]==20);assert(((uint8_t *)p)[-1]==(state==0?18:0));seq=2;return memcpy(p,s,n);}
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){assert(seq==2);seq=3;uint8_t *r=(void *)p;for(unsigned i=0;i<38;i++){unsigned expected=i>=5&&i<37?data[i-5]:i==2?20:i==4?(state==0?18:0):0;assert(r[i]==expected);}return 0x76543210;}
int main(void){assert(mmap((void *)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);for(state=0;state<256;state++){for(unsigned j=0;j<32;j++)data[j]=(state+j*7)&255;seq=0;*(volatile uint8_t *)0x805b82=255-state;assert(opencfw_em9305_callback_child_322e44((uintptr_t)data)==0x76543210&&seq==3);}puts("PASS256 fresh state and exact38 byte event cases");}
