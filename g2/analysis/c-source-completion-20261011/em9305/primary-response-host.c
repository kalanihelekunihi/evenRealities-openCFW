#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t bytes[160];static uint16_t request;static unsigned fail,mutate,sends,child;static uint32_t allocated_command,allocated_length;static uint8_t seen_status;
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){allocated_command=c;allocated_length=n;if(mutate)request=0x1002;return fail?0:(uintptr_t)(bytes+16);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=(uintptr_t)(bytes+11))abort();sends++;return 0xcafe;}
static uint32_t opencfw_em9305_ll_test_30bb14(void){child|=1;return 0x1234;}
static uint32_t opencfw_em9305_ll_test_30bb20(void){child|=2;return 0x56;}
static uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t p,uint32_t n){if(n!=8)abort();child=8;seen_status=bytes[16];memset((void*)p,0x88,8);return 77;}
static uint32_t opencfw_em9305_command_stop_30b654(uintptr_t p){child=9;for(unsigned i=0;i<20;i++)if(((uint8_t*)p)[i])abort();((uint8_t*)p)[2]=0x31;((uint8_t*)p)[3]=0x32;return 12;}
static void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){return memset(p,v,n);}
static void *opencfw_em9305_memcpy(void*p,void*q,uint32_t n){seen_status=bytes[16];return memcpy(p,q,n);}
uint32_t opencfw_em9305_primary_query_30bf04(uintptr_t a,uintptr_t b,uintptr_t c){child=4;*(uint16_t*)a=0x1234;*(uint8_t*)b=0x56;*(uint16_t*)c=0x789a;return 0;}
uint32_t opencfw_em9305_primary_query_30c92c(uintptr_t a,uintptr_t b){child=5;seen_status=bytes[16];*(uint8_t*)a=0x51;*(uint8_t*)b=0x52;return 0;}
uint32_t opencfw_em9305_primary_query_30bb74(uintptr_t a){child=6;seen_status=bytes[16];memset((void*)a,0x66,6);return 0;}
uint32_t opencfw_em9305_primary_query_30bdb4(uintptr_t a){child=7;seen_status=bytes[16];memset((void*)a,0x77,8);return 0;}
uint32_t opencfw_em9305_primary_query_30bf20(uint32_t c){if(c!=0x200f)abort();child=10;seen_status=bytes[16];return 0xa1;}
uint32_t opencfw_em9305_primary_query_30bea4(uintptr_t a){child=11;seen_status=bytes[16];memset((void*)a,0xb1,8);return 0;}
uint32_t opencfw_em9305_primary_query_30c928(uintptr_t a,uintptr_t b){child=12;*(uint8_t*)a=0xc1;*(uint8_t*)(a+1)=0xc2;*(uint16_t*)b=0xc4c3;return 0;}
uint32_t opencfw_em9305_primary_query_313960(uintptr_t a,uint32_t b,uint32_t c){if(b||c!=96)abort();child=13;seen_status=bytes[16];memset((void*)a,0xd1,8);return 0;}
/* Native32e918..32eb30: complete response router. Allocation captures the
 * command before call, then routing reloads the request after allocation.
 * Unwritten packet bytes and provider-owned scratch stay native sparse. */
extern uint32_t opencfw_em9305_primary_query_30bf04(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30c92c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30bb74(uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30bdb4(uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30bf20(uint32_t);
extern uint32_t opencfw_em9305_primary_query_30bea4(uintptr_t);
extern uint32_t opencfw_em9305_primary_query_30c928(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_query_313960(uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_primary_response_32e918(uintptr_t request,uint32_t status,uint32_t length)
{
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u)return 0u;
 uint32_t command=*(volatile uint16_t *)request;
 _Alignas(4) uint8_t scratch[24];
 switch(command){
 case 0x2002u:{
  uint32_t first=opencfw_em9305_ll_test_30bb14();
  uint32_t second=opencfw_em9305_ll_test_30bb20();
  *(volatile uint8_t *)(packet+3u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)(first>>8u);break;
 }
 case 0x1001u:{
  (void)opencfw_em9305_primary_query_30bf04((uintptr_t)scratch,(uintptr_t)(scratch+23u),(uintptr_t)(scratch+20u));
  *(volatile uint8_t *)packet=(uint8_t)status;
  uint32_t single=*(volatile uint8_t *)(scratch+23u);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)single;
  uint32_t word=*(volatile uint16_t *)(scratch+20u);
  *(volatile uint8_t *)(packet+4u)=(uint8_t)single;
  uint32_t first=*(volatile uint16_t *)scratch;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)word;
  *(volatile uint8_t *)(packet+7u)=(uint8_t)word;
  *(volatile uint8_t *)(packet+5u)=(uint8_t)first;
  *(volatile uint8_t *)(packet+3u)=(uint8_t)(word>>8u);
  *(volatile uint8_t *)(packet+8u)=(uint8_t)(word>>8u);
  *(volatile uint8_t *)(packet+6u)=(uint8_t)(first>>8u);break;
 }
 case 0x204bu:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30c92c(packet+1u,packet+2u);break;
 case 0x1009u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30bb74(packet+1u);break;
 case 0x2003u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30bdb4(packet+1u);break;
 case 0x200fu:{
  *(volatile uint8_t *)packet=(uint8_t)status;
  uint32_t result=opencfw_em9305_primary_query_30bf20(command);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)result;break;
 }
 case 0x2018u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_radio_random_bytes_310038(packet+1u,8u);break;
 case 0x201cu:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_30bea4(packet+1u);break;
 case 0x201fu:{
  (void)opencfw_em9305_memset(scratch,0u,20u);
  uint32_t result=opencfw_em9305_command_stop_30b654((uintptr_t)scratch);
  *(volatile uint8_t *)packet=(uint8_t)result;
  uint32_t first=*(volatile uint8_t *)(scratch+2u);
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  uint32_t second=*(volatile uint8_t *)(scratch+3u);
  *(volatile uint8_t *)(packet+2u)=(uint8_t)second;break;
 }
 case 0x204cu:{
  (void)opencfw_em9305_primary_query_30c928((uintptr_t)scratch,(uintptr_t)(scratch+20u));
  *(volatile uint8_t *)packet=(uint8_t)status;
  uint32_t first=*(volatile uint8_t *)scratch;
  *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
  uint32_t value=*(volatile uint16_t *)(scratch+20u);
  uint32_t second=*(volatile uint8_t *)(scratch+1u);
  *(volatile uint8_t *)(packet+3u)=(uint8_t)value;
  *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
  *(volatile uint8_t *)(packet+4u)=(uint8_t)(value>>8u);break;
 }
 case 0x0c48u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(uintptr_t)0x80571au;break;
 case 0x1002u:
  (void)opencfw_em9305_memset((void *)(packet+1u),0u,64u);
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_memcpy((void *)(packet+1u),(void *)(uintptr_t)0x805885u,64u);break;
 case 0x1003u:
  *(volatile uint8_t *)packet=(uint8_t)status;
  (void)opencfw_em9305_primary_query_313960(packet+1u,0u,96u);break;
 case 0u:case 0x0c01u:case 0x0c49u:case 0x0c63u:case 0x0c82u:case 0x0c84u:
 case 0x2001u:case 0x2005u:case 0x2010u:case 0x2011u:case 0x2012u:case 0x201du:case 0x201eu:
 case 0x204du:case 0x204fu:case 0x2050u:case 0x205fu:case 0x2074u:case 0x207bu:
  *(volatile uint8_t *)packet=(uint8_t)status;break;
 default:break;
 }
 return opencfw_em9305_ll_event_send(packet-5u);
}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint8_t*)0x80571a=0xe1;for(unsigned i=0;i<64;i++)((uint8_t*)0x805885)[i]=i+1;unsigned n=0;unsigned statuses[]={0,0x1234,255};for(unsigned op=0;op<65536;op++)for(fail=0;fail<2;fail++)for(unsigned si=0;si<3;si++){unsigned status=statuses[si];memset(bytes,0xa5,160);request=op;sends=child=0;seen_status=0;uint8_t expected[160];memset(expected,0xa5,160);uint8_t *e=expected+16;unsigned child_expected=0;switch(op){case 0x2002:e[0]=status;e[1]=0x34;e[2]=0x12;e[3]=0x56;child_expected=3;break;case 0x1001:{uint8_t a[]={status,0x56,0x9a,0x78,0x56,0x34,0x12,0x9a,0x78};memcpy(e,a,9);child_expected=4;break;}case 0x204b:e[0]=status;e[1]=0x51;e[2]=0x52;child_expected=5;break;case 0x1009:e[0]=status;memset(e+1,0x66,6);child_expected=6;break;case 0x2003:e[0]=status;memset(e+1,0x77,8);child_expected=7;break;case 0x2018:e[0]=status;memset(e+1,0x88,8);child_expected=8;break;case 0x201f:e[0]=12;e[1]=0x31;e[2]=0x32;child_expected=9;break;case 0x200f:e[0]=status;e[1]=0xa1;child_expected=10;break;case 0x201c:e[0]=status;memset(e+1,0xb1,8);child_expected=11;break;case 0x204c:e[0]=status;e[1]=0xc1;e[2]=0xc2;e[3]=0xc3;e[4]=0xc4;child_expected=12;break;case 0x1003:e[0]=status;memset(e+1,0xd1,8);child_expected=13;break;case 0xc48:e[0]=status;e[1]=0xe1;break;case 0x1002:e[0]=status;for(unsigned i=0;i<64;i++)e[1+i]=i+1;break;
case 0:case 0xc01:case 0xc49:case 0xc63:case 0xc82:case 0xc84:case 0x2001:case 0x2005:case 0x2010:case 0x2011:case 0x2012:case 0x201d:case 0x201e:case 0x204d:case 0x204f:case 0x2050:case 0x205f:case 0x2074:case 0x207b:e[0]=status;break;}
unsigned got=opencfw_em9305_primary_response_32e918((uintptr_t)&request,status,65);if(allocated_command!=op||allocated_length!=65)abort();if(fail){if(got||sends||child)abort();for(unsigned i=0;i<160;i++)if(bytes[i]!=0xa5)abort();}else{if(got!=0xcafe||sends!=1||child!=child_expected||memcmp(bytes,expected,160))abort();if((child_expected>=5&&child_expected<=8)||(child_expected>=10&&child_expected!=12)||op==0x1002)if(seen_status!=(uint8_t)status)abort();}n++;}
fail=0;mutate=1;request=0x2002;memset(bytes,0xa5,160);sends=child=0;opencfw_em9305_primary_response_32e918((uintptr_t)&request,7,65);if(allocated_command!=0x2002||child||bytes[16]!=7||sends!=1)abort();for(unsigned i=0;i<64;i++)if(bytes[17+i]!=i+1)abort();n++;printf("PASS %u response fixtures\n",n);}
