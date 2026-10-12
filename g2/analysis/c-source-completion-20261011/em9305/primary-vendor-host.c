#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t bytes[128],input[16];static uint16_t req[2];static unsigned fail,sends,calls,mutate;static uint32_t length,op,child,a0,a1,a2;
static void *opencfw_em9305_memcpy(void*a,const void*b,uint32_t n){return memcpy(a,b,n);}
uint32_t opencfw_em9305_controller_set_address(uintptr_t p){if(p!=(uintptr_t)input)abort();calls++;child=0xfff0;return 23;}
uint32_t opencfw_em9305_vendor_command_30be48(uintptr_t p){if(p!=(uintptr_t)input)abort();calls++;child=0xfff1;return 0x123;}
uint32_t opencfw_em9305_vendor_command_30d87c(uintptr_t p){if(p!=(uintptr_t)input)abort();calls++;child=0xfff2;return 0x234;}
uint32_t opencfw_em9305_vendor_command_30d9b4(uint32_t a,uint32_t b,uint32_t c){calls++;child=0xfff3;a0=a;a1=b;a2=c;return 0x345;}
uint32_t opencfw_em9305_vendor_command_30cd5c(uint32_t a){calls++;child|=1;a0=a;return 77;}
uint32_t opencfw_em9305_vendor_command_30db24(uint32_t a){calls++;child|=8;a0=a;return 77;}
uint32_t opencfw_em9305_vendor_command_30e034(uint32_t a){calls++;child=0xffe6;a0=a;return 0x456;}
uint32_t opencfw_em9305_vendor_allocator_second_313fa8(uint32_t a){if(a!=0x123456)abort();calls++;return 0x89abcdef;}
static uint32_t opencfw_em9305_pal_status_secondary(void){return 0;}
static uint32_t opencfw_em9305_pal_pending_consume(uint32_t a){if(a)abort();return 0xabcd;}
static uint32_t opencfw_em9305_controller_allocator_query(uint32_t a){if(a!=0xab)abort();return 0x12345678;}
static uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t p){uint64_t a=0;for(unsigned i=0;i<8;i++)a|=(uint64_t)*(volatile uint8_t*)(p+i)<<(i*8);return a;}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){length=n;op=c;if(mutate)req[0]=0xfffe;return fail?0:(uintptr_t)(bytes+16);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=(uintptr_t)(bytes+11))abort();sends++;return 99;}
#include "primary-vendor-leaves-prepared.c"
#include "primary-vendor-prepared.c"
static int known(unsigned c){switch(c){case 0xffa0:case 0xffa1:case 0xffa2:case 0xffa3:case 0xffc0:case 0xffcd:case 0xfff0:case 0xfff1:case 0xfff2:case 0xfff3:case 0xfff4:case 0xfff9:case 0xfffa:case 0xfffe:case 0xffff:case 0xffe1:case 0xffe6:return 1;default:return 0;}}
static void half(uint8_t*p,unsigned n){p[0]=n;p[1]=n>>8;}
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();*(uint32_t*)0x805cac=0x806000;for(unsigned i=0;i<128;i++)*(uint8_t*)(uintptr_t)(0x806000+i)=i+17;for(unsigned i=0;i<38;i++)*(uint8_t*)(uintptr_t)(0x8015e4+i)=i+41;for(unsigned i=0;i<28;i++)*(uint8_t*)(uintptr_t)(0x801848+i)=i+101;for(unsigned i=0;i<16;i++)input[i]=i+1;for(unsigned i=0;i<8;i++)*(uint16_t*)(uintptr_t)(0x805b1a+i*2)=0x2300+i;*(uint16_t*)0x8058d8=0x2468;*(uint16_t*)0x805f1c=0x1357;*(uint16_t*)0x805838=0x9876;unsigned vectors=0;
for(unsigned c=0;c<65536;c++)for(fail=0;fail<2;fail++)for(unsigned shortform=0;shortform<2;shortform++){
 memset(bytes,0xa5,sizeof bytes);uint8_t expected[128];memset(expected,0xa5,sizeof expected);req[0]=c;req[1]=shortform?5:9;length=op=child=a0=a1=a2=calls=sends=0;*(uint8_t*)0x8058cc=0;*(uint8_t*)0x8057a8=0;*(uint8_t*)0x801318=0;
 unsigned r=opencfw_em9305_primary_vendor_32eb34((uintptr_t)req,(uintptr_t)input);unsigned k=known(c);if(r!=k)abort();
 if(!k){if(length||calls||sends)abort();vectors++;continue;}unsigned el=1,es=0;switch(c){case 0xffc0:el=57;break;case 0xffcd:es=1;break;case 0xffa2:es=18;break;case 0xfff1:el=7;es=0x23;break;case 0xfff2:es=0x34;break;case 0xfff3:es=0x45;break;case 0xfff4:el=39;break;case 0xfffa:el=35;break;case 0xfffe:el=29;break;case 0xffff:es=12;break;case 0xffe6:es=0x56;break;}
 if(length!=el||op!=c||sends!=!fail)abort();
 if(c==0xfff3&&(a0!=0x04030201||a1!=(shortform?0:0x08070605)||a2!=1))abort();
 if(c==0xffe6&&a0!=0x04030201)abort();
 if(c==0xffa0&&*(uint8_t*)0x8058cc!=1)abort();
 if(c==0xffa1&&*(uint8_t*)0x8057a8!=1)abort();
 if(c==0xfff9&&*(uint8_t*)0x801318!=1)abort();
 if(c==0xffe1&&(calls!=1||child!=1||a0!=1))abort();
 if(!fail){expected[16]=es;uint8_t*p=expected+17;switch(c){case 0xfff4:memcpy(p,(void*)0x8015e4,38);break;case 0xfffe:memcpy(p,(void*)0x801848,28);break;case 0xfffa:half(p,0);half(p+2,0xabcd);p[4]=0x78;p[5]=0x56;p[6]=0x34;p[7]=0x12;p[8]=0xef;p[9]=0xcd;p[10]=0xab;p[11]=0x89;half(p+12,51);half(p+14,0x2300);half(p+16,0);half(p+18,0x2468);half(p+20,0x1357);half(p+22,0x9876);break;case 0xffc0:half(p,29);half(p+2,0x2301);half(p+4,3);half(p+6,0x2302);half(p+8,3);half(p+10,0x2303);half(p+12,6);half(p+14,0x2304);half(p+16,69);half(p+18,0x2306);half(p+20,70);half(p+22,0x2305);half(p+24,74);half(p+26,0);half(p+28,75);half(p+30,0x2307);break;}
 }if(memcmp(bytes,expected,sizeof bytes)){fprintf(stderr,"mismatch %x fail%u short%u\n",c,fail,shortform);for(unsigned i=0;i<128;i++)if(bytes[i]!=expected[i])fprintf(stderr,"%u %x %x\n",i,bytes[i],expected[i]);abort();}vectors++;
}
/* Fresh opcode after allocator: initially status-only request receives descriptor. */
fail=0;mutate=1;req[0]=0xffcd;memset(bytes,0xa5,sizeof bytes);sends=0;if(opencfw_em9305_primary_vendor_32eb34((uintptr_t)req,(uintptr_t)input)!=1||op!=0xffcd||length!=1||bytes[16]!=1||memcmp(bytes+17,(void*)0x801848,28)||sends!=1)abort();vectors++;
printf("PASS %u vendor command/response projections; controlled seven remaining child contracts; no native execution equality claim\n",vectors);return 0;}
