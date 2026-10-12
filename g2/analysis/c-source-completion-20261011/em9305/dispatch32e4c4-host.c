#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/mman.h>
static uintptr_t req,inp,resp;
static unsigned fail,count,id,status,allocfail,mutate,guards,sends,structured,fallback;
static void opencfw_em9305_native_stack_check_302820(void){guards++;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=resp-5)fail++;sends++;return 97;}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t cmd){if(n!=2||cmd!=*(uint16_t*)req)fail++;if(mutate==2)*(uint16_t*)req=7;return allocfail?0:resp;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t s){if(r!=req||s!=status)fail++;structured++;return 9;}
static uint32_t opencfw_em9305_dispatch_331204(uintptr_t r,uintptr_t i){if(r!=req||i!=inp)fail++;fallback++;return status;}
extern uint32_t opencfw_em9305_command_records_apply_30dc48(uint32_t,uint32_t,uintptr_t);
extern void opencfw_em9305_command_struct_decode_332abc(uintptr_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_struct_apply_30b974(uintptr_t,uintptr_t,uintptr_t);
/* Native32e4c4..32e5a8: packed record command, structured command and existing fallback. */
uint32_t opencfw_em9305_dispatch_32e4c4(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command==0x2082u){uint32_t count=*(volatile uint8_t *)(input+1u),id=*(volatile uint8_t *)input;
  uintptr_t records=(uintptr_t)__builtin_alloca((3u+count*8u)&2040u);
  opencfw_em9305_native_stack_check_302820();
  uintptr_t row=input+2u;
  for(uint32_t i=0u;i<count;++i){
   uint32_t size=*(volatile uint8_t *)(row+3u),a=*(volatile uint8_t *)row,b=*(volatile uint8_t *)(row+1u),c=*(volatile uint8_t *)(row+2u);
   uintptr_t data=row+4u;row+=size+4u;
   uintptr_t out=records+i*8u;*(volatile uint32_t *)(out+4u)=(uint32_t)data;
   *(volatile uint8_t *)out=(uint8_t)a;*(volatile uint8_t *)(out+1u)=(uint8_t)b;
   *(volatile uint8_t *)(out+2u)=(uint8_t)c;*(volatile uint8_t *)(out+3u)=(uint8_t)size;
  }
  uint32_t status=opencfw_em9305_command_records_apply_30dc48(id,count,records);
  uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(2u,*(volatile uint16_t *)request);
  if(response){*(volatile uint8_t *)response=(uint8_t)status;
   if(*(volatile uint16_t *)request==0x2082u)*(volatile uint8_t *)(response+1u)=(uint8_t)id;
   (void)opencfw_em9305_ll_event_send(response-5u);
  }
  return 1u;
 }
 if(command==0x2085u){uint8_t scratch[60] __attribute__((aligned(4)));
  uintptr_t base=(uintptr_t)scratch;
  (void)opencfw_em9305_memset(scratch,0u,36u);
  opencfw_em9305_command_struct_decode_332abc(base+48u,base+36u,base,input);
  uint32_t status=opencfw_em9305_command_struct_apply_30b974(base+48u,base+36u,base);
  (void)opencfw_em9305_ll_status_event_331bf8(request,status);return 1u;
 }
 return opencfw_em9305_dispatch_331204(request,input);
}

uint32_t opencfw_em9305_command_records_apply_30dc48(uint32_t a,uint32_t n,uintptr_t records){
 if(a!=id||n!=count)fail++;
 uintptr_t row=inp+2;
 for(unsigned i=0;i<n;i++){
  unsigned char *r=(unsigned char*)records+i*8,*in=(unsigned char*)row;
  if(memcmp(r,in,4)||*(uint32_t*)(r+4)!=(uint32_t)(row+4))fail++;
  row+=4+in[3];
 }
 if(mutate==1)*(uint16_t*)req=7;
 return status;
}
void opencfw_em9305_command_struct_decode_332abc(uintptr_t a,uintptr_t b,uintptr_t c,uintptr_t i){
 if(a!=c+48||b!=c+36||i!=inp)fail++;
 for(unsigned j=0;j<36;j++)if(*(unsigned char*)(c+j))fail++;
 for(unsigned j=0;j<60;j++)*(unsigned char*)(c+j)=(unsigned char)(j+1);
}
uint32_t opencfw_em9305_command_struct_apply_30b974(uintptr_t a,uintptr_t b,uintptr_t c){
 if(a!=c+48||b!=c+36)fail++;
 for(unsigned j=0;j<60;j++)if(*(unsigned char*)(c+j)!=j+1)fail++;
 return status;
}
int main(void){
 uintptr_t arena=(uintptr_t)mmap((void*)0x20000000,131072,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 if(arena!=0x20000000)return 2;
 req=arena;inp=arena+64;resp=arena+100000;unsigned cases=0;
 for(count=0;count<256;count++)for(id=0;id<256;id+=85)for(allocfail=0;allocfail<2;allocfail++)for(mutate=0;mutate<3;mutate++){
  *(uint16_t*)req=0x2082;*(uint8_t*)inp=id;*(uint8_t*)(inp+1)=count;
  uintptr_t row=inp+2;for(unsigned j=0;j<count;j++){unsigned char *r=(unsigned char*)row;r[0]=j;r[1]=255-j;r[2]=j^id;r[3]=(j*31+id)&255;row+=r[3]+4;}
  status=0x12340000+count+id;guards=sends=structured=fallback=0;memset((void*)resp,0xa5,2);
  if(opencfw_em9305_dispatch_32e4c4(req,inp)!=1||guards!=1||sends!=!allocfail||structured||fallback)fail++;
  if(!allocfail&&(*(uint8_t*)resp!=(uint8_t)status||*(uint8_t*)(resp+1)!=(mutate?0xa5:id)))fail++;
  cases++;
 }
 for(unsigned j=0;j<256;j++){
  status=j*0x01010101u;*(uint16_t*)req=0x2085;structured=fallback=0;
  if(opencfw_em9305_dispatch_32e4c4(req,inp)!=1||structured!=1||fallback)fail++;cases++;
  *(uint16_t*)req=(uint16_t)j;structured=fallback=0;
  if(opencfw_em9305_dispatch_32e4c4(req,inp)!=status||structured||fallback!=1)fail++;cases++;
 }
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
