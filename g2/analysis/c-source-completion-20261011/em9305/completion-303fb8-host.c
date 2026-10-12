#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[100];static unsigned cursor,initial,next,last;static uint32_t canceled;
static void mark(char c){trace[cursor++]=c;trace[cursor]=0;}
static uint32_t a(uint32_t c,uint32_t arg){assert(c==0x810000&&arg==0x8013f0);mark('A');return initial;}
static uint32_t b(uint32_t c,uint32_t arg){assert(c==0x810000&&arg==0x8013f0);mark('B');return 55;}
static uint32_t d(uint32_t c,uint32_t arg){assert(c==0x810000&&(arg==0||arg==0x8013f0));mark('D');return next;}
static uint32_t e(uint32_t c,uint32_t arg){assert(c==0x810000&&(arg==0||arg==0x8013f0));mark('E');return last;}
static uint32_t g(uint32_t c,uint32_t arg){assert(c==0x810000&&(arg==0||arg==0x8013f0));mark('G');return 44;}
static uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t value){mark('C');canceled=value;return 11;}
static uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t value){(void)value;mark('F');return 12;}
static uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t row){assert(row==0x820000);mark('P');return 13;}
static uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t root){assert(root==0x8015cc&&*(uint32_t *)(root+8)==next+0x123);mark('I');return 14;}
static uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t p){assert(p);mark('R');return 15;}
static uint32_t opencfw_em9305_radio_request_30fcd8(uintptr_t p,uint32_t selector){assert(selector==1&&*(uint16_t *)p==9&&*(uint32_t *)(p+4)==0x830000);mark('S');return 16;}
static uint32_t opencfw_em9305_radio_request_30faec(uintptr_t p,uint32_t size){assert(p==0x8013f0&&size==257);mark('Q');return 17;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(n==20);return memcpy(d,s,n);}
static void *opencfw_em9305_memset(void *d,uint32_t value,uint32_t n){assert(value==0&&n==20);return memset(d,0,n);}
static const uint8_t opencfw_em9305_radio_template_3343f8[20]={1};
/* Authenticated completion303fb8..304140. State2 compares incoming R0;
 * callback address low byte and changed R17 argument are intentional. */
uint32_t opencfw_em9305_radio_completion_303fb8(uint32_t current,uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t fifth)
{
 uintptr_t root=0x8015ccu,row=0u,callback=0u;
 uint32_t state=*(volatile uint8_t *)(root-8u),argument=first,result=current,amount=0u;
 _Alignas(4) uint8_t scratch[20];
 _Alignas(4) uint8_t descriptor[8];
 typedef uint32_t (*completion_fn)(uint32_t,uint32_t);
 if(state==3u){
  row=*(volatile uint32_t *)(uintptr_t)(current+44u);
  callback=*(volatile uint32_t *)(row+116u);
  if(first-3u<2u){
   result=((completion_fn)callback)(current,0u);
   callback=*(volatile uint32_t *)(row+120u);
   if(callback!=0u)result=((completion_fn)callback)(current,0u);
   if(first==4u)goto cancel_finish;
   goto finish;
  }
  if(first!=0u){
   result=((completion_fn)callback)(current,0u);
   callback=*(volatile uint32_t *)(row+120u);
   if(callback!=0u)result=((completion_fn)callback)(current,0u);
   goto finish;
  }
  argument=0x8013f0u;
  amount=((completion_fn)callback)(current,argument);
  result=amount;
  if(amount!=0u)goto start;
  goto fallback;
 }
 if(state==2u){
  *(volatile uint8_t *)(root-8u)=3u;
  row=*(volatile uint32_t *)(uintptr_t)(current+44u);
  callback=*(volatile uint32_t *)(row+112u);
  if(current<2u){
   result=((completion_fn)callback)(current,0u);
   if(first==4u)goto cancel_finish;
   goto finish;
  }
  if(first!=0u)goto finish;
  *(volatile uint32_t *)(row+140u)=fourth;
  *(volatile uint32_t *)(row+136u)=third;
  *(volatile uint8_t *)(row+133u)=(uint8_t)callback;
  *(volatile uint8_t *)(row+134u)=(uint8_t)fifth;
  argument=0x8013f0u;
  result=((completion_fn)callback)(current,argument);
  callback=*(volatile uint32_t *)(row+116u);
  if(callback==0u)goto fallback;
  amount=((completion_fn)callback)(current,argument);
  result=amount;
  if(amount!=0u)goto start;
  goto fallback;
 }
 result=first-3u;
 if(state!=0u)return 0u;
 if(first==4u)goto cancel_finish;
 if(first!=0u)goto finish;
 row=*(volatile uint32_t *)(uintptr_t)(current+44u);
 *(volatile uint32_t *)(row+136u)=third;
 callback=*(volatile uint32_t *)(row+104u);
 *(volatile uint32_t *)(row+140u)=fourth;
 *(volatile uint8_t *)(row+133u)=(uint8_t)second;
 *(volatile uint8_t *)(row+134u)=(uint8_t)fifth;
 argument=0x8013f0u;
 amount=((completion_fn)callback)(current,argument);
 result=amount;
 if(amount!=0u){
  result=*(volatile uint32_t *)(row+100u);
  if(result!=0u){
   *(volatile uint8_t *)(root-8u)=1u;
   uint32_t bytes=*(volatile uint8_t *)(row+124u);
   *(volatile uint32_t *)(descriptor+4u)=result;
   *(volatile uint16_t *)descriptor=(uint16_t)bytes;
   (void)opencfw_em9305_memcpy(scratch,opencfw_em9305_radio_template_3343f8,20u);
   (void)opencfw_em9305_radio_record_30fc28((uintptr_t)scratch);
   result=opencfw_em9305_radio_request_30fcd8((uintptr_t)descriptor,1u);
   goto initialized;
  }
 }
 result=opencfw_em9305_radio_cancel_30fab8(result);
initialized:
 callback=*(volatile uint32_t *)(row+108u);
 if(callback!=0u)result=((completion_fn)callback)(current,argument);
 if(amount!=0u)return 0u;
 callback=*(volatile uint32_t *)(row+116u);
 if(callback==0u)goto fallback;
 amount=((completion_fn)callback)(current,argument);
 result=amount;
 if(amount==0u)goto fallback;
 *(volatile uint8_t *)(root-8u)=3u;
 result=opencfw_em9305_radio_cancel_30fab8(result);
start:
 (void)opencfw_em9305_common_radio_prepare_30fb4c(row);
 *(volatile uint32_t *)(root+8u)=amount+fourth;
 (void)opencfw_em9305_common_radio_bind_30fc10(root);
 (void)opencfw_em9305_memset(scratch,0u,20u);
 (void)opencfw_em9305_radio_record_30fc28((uintptr_t)scratch);
 (void)opencfw_em9305_radio_request_30faec(argument,257u);
 callback=*(volatile uint32_t *)(row+120u);
 result=((completion_fn)callback)(current,argument);
 if(result!=0u)return 0u;
 goto cancel_finish;
fallback:
 callback=*(volatile uint32_t *)(row+120u);
 result=(uint32_t)callback;
 if(callback!=0u)result=((completion_fn)callback)(current,argument);
cancel_finish:
 result=opencfw_em9305_radio_cancel_30fab8(result);
finish:
 (void)opencfw_em9305_common_radio_finish_3045c0(result);
 return 1u;
}

static void setup(unsigned state){memset((void *)0x800000,0,0x100000);*(uint8_t *)0x8015c4=state;*(uint32_t *)0x81002c=0x820000;*(uint32_t *)0x820064=0x830000;*(uint32_t *)0x820068=(uintptr_t)a;*(uint32_t *)0x82006c=(uintptr_t)b;*(uint32_t *)0x820070=(uintptr_t)g;*(uint32_t *)0x820074=(uintptr_t)d;*(uint32_t *)0x820078=(uintptr_t)e;*(uint8_t *)0x82007c=9;cursor=0;trace[0]=0;canceled=0;}
static void run(unsigned state,unsigned first,unsigned i,unsigned n,unsigned l,unsigned expected,const char *wanted){setup(state);initial=i;next=n;last=l;assert(opencfw_em9305_radio_completion_303fb8(0x810000,first,0x56,0x789,0x123,0x9a)==expected);assert(!strcmp(trace,wanted));if(first==0&&(state==0||state==2)){assert(*(uint32_t *)0x820088==0x789&&*(uint32_t *)0x82008c==0x123&&*(uint8_t *)0x820085==(state==0?0x56:(uint8_t)(uintptr_t)g)&&*(uint8_t *)0x820086==0x9a);}}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);
run(0,0,0,0,0,1,"ACBDECF");run(0,0,0,1,0,1,"ACBDCPIRQECF");run(0,0,0,1,1,0,"ACBDCPIRQE");run(0,0,1,0,0,0,"ARSB");run(0,0,1,1,1,0,"ARSB");
run(2,0,0,0,0,1,"GDECF");run(2,0,0,1,0,1,"GDPIRQECF");run(2,0,0,1,1,0,"GDPIRQE");run(3,0,0,0,0,1,"DECF");run(3,0,0,1,0,1,"DPIRQECF");run(3,0,0,1,1,0,"DPIRQE");
run(0,4,0,0,0,1,"CF");assert(canceled==1);run(0,2,0,0,0,1,"F");run(2,2,0,0,0,1,"F");run(3,3,0,0,0,1,"DEF");run(3,4,0,0,5,1,"DECF");assert(canceled==5);run(3,2,0,0,0,1,"DEF");run(1,0,0,0,0,0,"");run(4,0,0,0,0,0,"");
setup(0);initial=1;next=last=0;*(uint32_t *)0x820064=0;assert(opencfw_em9305_radio_completion_303fb8(0x810000,0,0,0,0,0)==0&&!strcmp(trace,"ACB"));
setup(3);initial=next=last=0;*(uint32_t *)0x820078=0;assert(opencfw_em9305_radio_completion_303fb8(0x810000,3,0,0,0,0)==1&&!strcmp(trace,"DF"));
setup(3);initial=next=last=0;*(uint32_t *)0x820078=0;assert(opencfw_em9305_radio_completion_303fb8(0x810000,0,0,0,0,0)==1&&!strcmp(trace,"DCF"));
setup(2);initial=next=last=0;*(uint32_t *)0x820074=0;assert(opencfw_em9305_radio_completion_303fb8(0x810000,0,0,0,0,0)==1&&!strcmp(trace,"GECF"));
setup(0);initial=next=last=0;*(uint32_t *)0x82006c=0;*(uint32_t *)0x820074=0;assert(opencfw_em9305_radio_completion_303fb8(0x810000,0,0,0,0,0)==1&&!strcmp(trace,"ACECF"));
setup(0);initial=1;next=last=0;*(uint32_t *)0x82006c=0;assert(opencfw_em9305_radio_completion_303fb8(0x810000,0,0,0,0,0)==0&&!strcmp(trace,"ARS"));
printf("PASS 25\n");}
