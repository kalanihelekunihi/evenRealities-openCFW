#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint16_t request;static uint8_t input[40],response[64],expected[64];static uint32_t fresh,fail,allocated,sent,calls;
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){return id==7?0x810000:0;}
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t b){return (uint16_t)a*(uint16_t)b;}
static void *opencfw_em9305_memcpy(void*a,const void*b,size_t n){return memcpy(a,b,n);}
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t op){if(op!=request)abort();allocated=n;request=fresh;return fail?0:(uintptr_t)(response+8);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){if(p!=(uintptr_t)(response+3))abort();sent++;return 0;}
uint32_t opencfw_em9305_command_vendor_mask_30cf28(uint32_t a,uint32_t b){calls++;return a^b;}
uint32_t opencfw_em9305_command_vendor_mode_30d5a8(uint32_t a,uint32_t b){calls++;return a+b;}
uint32_t opencfw_em9305_command_vendor_option_30d75c(uint32_t a,uint32_t b,uint32_t c){calls++;return a+b+c;}
extern uint32_t opencfw_em9305_command_vendor_mode_30d5a8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_vendor_option_30d75c(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_vendor_mask_30cf28(uint32_t,uint32_t);
/* Native30be3c branches306f70/306f8c: genuine two-register64-bit result. */
uint64_t opencfw_em9305_command_vendor_statistics_30be3c(uint32_t id,uint32_t associated)
{
 uint32_t high=0u,low=0u;
 if(associated!=0u){uintptr_t record=opencfw_em9305_radio_record_find_31aa64((uint8_t)id);if(record!=0u){high=*(volatile uint32_t *)(record+724u);low=*(volatile uint32_t *)(record+720u);}}
 else if(id<6u){uint32_t offset=opencfw_em9305_config_limit_mpyuw(id,784u);uintptr_t row=0x803ffcu+offset;low=*(volatile uint32_t *)row;high=*(volatile uint32_t *)(row+4u);}
 return ((uint64_t)high<<32)|low;
}
/* Native303264..303270: live product36-byte snapshot, actual forward copy. */
void opencfw_em9305_command_vendor_snapshot_303264(uintptr_t output)
{(void)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8014f4u,36u);}
/* Native3328c8..3329b0: five vendor commands and fresh response opcode. */
uint32_t opencfw_em9305_dispatch_3328c8(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status=0u,size=1u,id=0u,associated=0u;
 switch(command){
 case 0xffd0u:{uint32_t c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),d=*(volatile uint8_t *)(input+3u),e=*(volatile uint8_t *)(input+4u),a=*(volatile uint8_t *)input;uint32_t mask=b+(c<<8)+(d<<16)+(e<<24);status=opencfw_em9305_command_vendor_mask_30cf28(a,mask);break;}
 case 0xffd1u:{uint32_t b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;status=opencfw_em9305_command_vendor_mode_30d5a8(a,b);break;}
 case 0xffd2u:{uint32_t c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;status=opencfw_em9305_command_vendor_option_30d75c(a,b,c);break;}
 case 0xffdau:size=37u;break;
 case 0xffdeu:{uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input,selector=*(volatile uint8_t *)(input+2u);id=low+(high<<8);associated=selector!=0u;size=6u;break;}
 default:return 0u;
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,*(volatile uint16_t *)request);if(response==0u)return 1u;
 *(volatile uint8_t *)response=(uint8_t)status;uintptr_t cursor=response+1u;
 command=*(volatile uint16_t *)request;
 if(command==0xffdau){uint8_t snapshot[36] __attribute__((aligned(4)));opencfw_em9305_command_vendor_snapshot_303264((uintptr_t)snapshot);(void)opencfw_em9305_memcpy((void *)cursor,snapshot,36u);}
 else if(command==0xffdeu){uint64_t counters=opencfw_em9305_command_vendor_statistics_30be3c((uint16_t)id,associated);*(volatile uint8_t *)(cursor+4u)=(uint8_t)(counters>>32u);*(volatile uint8_t *)cursor=(uint8_t)counters;*(volatile uint8_t *)(cursor+3u)=(uint8_t)(counters>>24u);*(volatile uint8_t *)(cursor+2u)=(uint8_t)(counters>>16u);*(volatile uint8_t *)(cursor+1u)=(uint8_t)(counters>>8u);}
 (void)opencfw_em9305_ll_event_send(cursor-6u);return 1u;
}

int main(void){void*m=mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);if(m==MAP_FAILED)return 2;for(unsigned i=0;i<0x20000;i++)((uint8_t*)m)[i]=(uint8_t)(i*73+19);
uint64_t count=0;unsigned options[]={0xffd0,0xffd1,0xffd2,0xffda,0xffde,0};
for(unsigned cmd=0;cmd<65536;cmd++)for(unsigned f=0;f<6;f++)for(unsigned bad=0;bad<2;bad++){
for(unsigned i=0;i<40;i++)input[i]=(uint8_t)(cmd+i*17);request=cmd;fresh=options[f];fail=bad;allocated=sent=calls=0;memset(response,0xa5,64);memcpy(expected,response,64);
unsigned recognized=cmd==0xffd0||cmd==0xffd1||cmd==0xffd2||cmd==0xffda||cmd==0xffde;unsigned size=cmd==0xffda?37:cmd==0xffde?6:1;unsigned status=0;
if(cmd==0xffd0)status=input[0]^(input[1]|input[2]<<8|input[3]<<16|(uint32_t)input[4]<<24);if(cmd==0xffd1)status=input[0]+input[1];if(cmd==0xffd2)status=input[0]+input[1]+input[2];
if(recognized&&!bad){expected[8]=status;if(fresh==0xffda)memcpy(expected+9,(void*)0x8014f4,36);if(fresh==0xffde){uint32_t id=cmd==0xffde?(input[0]|input[1]<<8):0;unsigned assoc=cmd==0xffde&&input[2]!=0;uintptr_t row=assoc?(uint8_t)id==7?0x810000+720:0:id<6?0x803ffc+id*784:0;uint32_t lo=row?*(uint32_t*)row:0,hi=row?*(uint32_t*)(row+4):0;expected[9]=lo;expected[10]=lo>>8;expected[11]=lo>>16;expected[12]=lo>>24;expected[13]=hi;}}
unsigned ret=opencfw_em9305_dispatch_3328c8((uintptr_t)&request,(uintptr_t)input);if(ret!=recognized||allocated!=(recognized?size:0)||sent!=(recognized&&!bad)||calls!=(cmd==0xffd0||cmd==0xffd1||cmd==0xffd2)||memcmp(response,expected,64)){fprintf(stderr,"FAIL %x %x %u\n",cmd,fresh,bad);return 1;}count++;}
for(unsigned id=0;id<65536;id++)for(unsigned assoc=0;assoc<2;assoc++){uintptr_t row=assoc?(uint8_t)id==7?0x810000+720:0:id<6?0x803ffc+id*784:0;uint64_t value=row?((uint64_t)*(uint32_t*)(row+4)<<32)|*(uint32_t*)row:0;if(opencfw_em9305_command_vendor_statistics_30be3c(id,assoc)!=value)return 3;count++;}printf("PASS %llu\n",(unsigned long long)count);return 0;}
