#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned fail,apply_result=1,applies,allocs,sends,length,command_seen,mutate;
static uint16_t request;
static uint32_t expect_id,expect_value;
static uint8_t output[64];
uint32_t opencfw_em9305_command_pair_apply_307fa0(uint32_t id,uint32_t value){assert(id==expect_id&&value==expect_value);applies++;return apply_result;}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t cmd){allocs++;length=n;command_seen=cmd;if(mutate)request=mutate;return fail?0:(uintptr_t)(output+5);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output);sends++;return 99;}
uint32_t opencfw_em9305_ll_stream_gate_30e510(void)
{
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a9eu;
 if(busy==0u) *(volatile uint8_t *)(uintptr_t)0x805a9fu=1u;
 return busy==0u;
}
uint32_t opencfw_em9305_address_busy_307cb8(void)
{return *(volatile uint8_t *)(uintptr_t)0x8051a4u==1u;}
uint32_t opencfw_em9305_command_ready_3213d0(uint32_t id)
{
 if(id>5u)return 0u;
 uint32_t offset;
 offset=id*784u; /* Host-only bounded stride normalization. */
 return *(volatile uint8_t *)(uintptr_t)(0x803d78u+offset)!=0u;
}
void *opencfw_em9305_memcpy(void *destination,const void *source,uint32_t bytes)
{
 uintptr_t out=(uintptr_t)destination,in=(uintptr_t)source;
 if (((out^in)&3u)==0u) {
  uint32_t align=(4u-(uint32_t)(out&3u))&3u;
  while (align!=0u) {
   if (bytes==0u) return destination;
   uint8_t value=*(volatile const uint8_t *)in;
   *(volatile uint8_t *)out=value;
   in+=1u;out+=1u;bytes-=1u;align-=1u;
  }
  while (bytes>=4u) {
   uint32_t value=*(volatile const uint32_t *)in;
   *(volatile uint32_t *)out=value;
   in+=4u;out+=4u;bytes-=4u;
  }
 }
 while (bytes!=0u) {
  uint8_t value=*(volatile const uint8_t *)in;
  *(volatile uint8_t *)out=value;
  in+=1u;out+=1u;bytes-=1u;
 }
 return destination;
}
/* Native optimized fill 0x33301c..0x333062, not presumed libc semantics.
 * Preserve byte alignment writes, 32-bit expansion of full R1, word stores,
 * trailing byte writes and unchanged incoming destination return.
 */
#include <stdint.h>
void *opencfw_em9305_memset(void *destination,uint32_t value,uint32_t bytes)
{
    uintptr_t current = (uintptr_t)destination;
    if ((current & 3u) != 0) {
        uint32_t alignment = 4u - (uint32_t)(current & 3u);
        while (alignment != 0) {
            if (bytes == 0) return destination;
            *(volatile uint8_t *)current = (uint8_t)value;
            current++;
            alignment--;
            bytes--;
        }
    }
    const uint32_t pair = (value << 8) | value;
    const uint32_t word = pair | (pair << 16);
    while (bytes >= 4) {
        bytes -= 4;
        *(volatile uint32_t *)current = word;
        current += 4;
    }
    while (bytes != 0) {
        *(volatile uint8_t *)current = (uint8_t)value;
        current++;
        bytes--;
    }
    return destination;
}

/* Native303270..303278: literal zero-fill52. */
uintptr_t opencfw_em9305_command_info_zero_303270(uintptr_t output)
{return (uintptr_t)opencfw_em9305_memset((void *)output,0u,52u);}
/* Native3032a8..3032b4: forward36-byte resident information copy. */
uintptr_t opencfw_em9305_command_info_copy_3032a8(uintptr_t output)
{return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8017fcu,36u);}
extern uint32_t opencfw_em9305_command_pair_apply_307fa0(uint32_t,uint32_t);
/* Native30c580..30c5c0: full-width id check, readiness, busy and apply result. */
uint32_t opencfw_em9305_command_pair_set_30c580(uint32_t id,uint32_t value)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(id>=3840u)return 18u;
 if(opencfw_em9305_command_ready_3213d0(id)==0u)return 66u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 return opencfw_em9305_command_pair_apply_307fa0(id,value)!=0u?0u:18u;
}
/* Native330bdc..330c60 full prehandler; fresh opcode after status store. */
uint32_t opencfw_em9305_command_prehandle_330bdc(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status;
 uintptr_t response;
 if(command==0xffdbu){status=0u;response=opencfw_em9305_ll_response_allocate_32e428(53u,0xffdbu);}
 else if(command==0xffb3u){
  uint32_t first_hi=*(volatile uint8_t *)(input+1u),second_hi=*(volatile uint8_t *)(input+3u);
  uint32_t first_lo=*(volatile uint8_t *)input,second_lo=*(volatile uint8_t *)(input+2u);
  status=opencfw_em9305_command_pair_set_30c580(first_lo+(first_hi<<8u),second_lo+(second_hi<<8u));
  response=opencfw_em9305_ll_response_allocate_32e428(1u,*(volatile uint16_t *)request);
 }else return 0u;
 if(response==0u)return 1u;
 *(volatile uint8_t *)response=(uint8_t)status;
 uint32_t fresh=*(volatile uint16_t *)request;
 _Alignas(4) uint8_t scratch[52];
 if(fresh==0xffdcu){
  (void)opencfw_em9305_command_info_copy_3032a8((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)(response+1u),scratch,36u);
 }else if(fresh==0xffdbu){
  (void)opencfw_em9305_command_info_zero_303270((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)(response+1u),scratch,52u);
 }
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uint16_t input[2]={0,0xbeef};for(unsigned j=0;j<36;j++)*(uint8_t *)(uintptr_t)(0x8017fc+j)=j*37+11;for(unsigned j=0;j<6;j++)*(uint8_t *)(uintptr_t)(0x803d78+j*784)=1;*(uint8_t *)0x805a9e=0;*(uint8_t *)0x8051a4=0;expect_id=0;expect_value=0xbeef;
for(unsigned opcode=0;opcode<65536;opcode++)for(fail=0;fail<2;fail++){request=opcode;allocs=sends=applies=0;memset(output,0xa5,64);unsigned handled=opcode==0xffb3||opcode==0xffdb;assert(opencfw_em9305_command_prehandle_330bdc((uintptr_t)&request,(uintptr_t)input)==handled);assert(allocs==handled&&sends==(handled&&!fail)&&applies==(opcode==0xffb3));if(handled){assert(command_seen==opcode&&length==(opcode==0xffdb?53u:1u));if(!fail){assert(output[5]==0);for(unsigned j=6;j<64;j++)assert(output[j]==(opcode==0xffdb&&j<58?0:0xa5));}}cases++;}
fail=0;for(unsigned original=0;original<2;original++)for(unsigned variant=0;variant<4;variant++){request=original?0xffdb:0xffb3;mutate=variant==0?0:variant==1?0xffdb:variant==2?0xffdc:0x1234;allocs=sends=applies=0;memset(output,0xa5,64);assert(opencfw_em9305_command_prehandle_330bdc((uintptr_t)&request,(uintptr_t)input)==1&&sends==1&&output[5]==0);for(unsigned j=6;j<64;j++){unsigned value=0xa5;if(request==0xffdb&&j<58)value=0;if(request==0xffdc&&j<42)value=*(uint8_t *)(uintptr_t)(0x8017fc+j-6);assert(output[j]==value);}cases++;}
mutate=0;for(unsigned id=0;id<65536;id++)for(unsigned mode=0;mode<8;mode++)for(apply_result=0;apply_result<2;apply_result++){unsigned gate=mode&1,ready_flag=(mode>>1)&1,busy=(mode>>2)&1;*(uint8_t *)0x805a9e=gate;*(uint8_t *)0x8051a4=busy;for(unsigned j=0;j<6;j++)*(uint8_t *)(uintptr_t)(0x803d78+j*784)=ready_flag;expect_id=id;expect_value=id^0xabcd;applies=0;unsigned eligible=!gate&&id<3840&&id<=5&&ready_flag&&!busy;unsigned result=gate?12:id>=3840?18:id>5||!ready_flag?66:busy?12:apply_result?0:18;assert(opencfw_em9305_command_pair_set_30c580(id,expect_value)==result&&applies==eligible);cases++;}
printf("PASS %u\n",cases);}
