#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned mode,slotok,allocfail,posts,status_calls,releases,parameters,transfer,insert,common,count;static uint32_t code,allocation=10000;static uint8_t captured[4];
static void fail_at(unsigned line){fprintf(stderr,"line=%u mode=%u slot=%u fail=%u\n",line,mode,slotok,allocfail);exit(1);}
#define abort() fail_at(__LINE__)
struct opencfw_em9305_native_product_pair{uint32_t low,high;};

static uintptr_t opencfw_em9305_init_connection_allocate_316c58(void){return mode?0x806390:0;}
static uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t p){if(p!=0x806390)abort();releases++;return 0;}
static uint32_t opencfw_em9305_init_connection_parameters_32074c(uintptr_t p,uint32_t k,uint32_t l,uint32_t h){if(p!=0x804004||k!=0x53||l!=0x12345678||h!=0xabcdef)abort();parameters++;return 0;}
static uint32_t opencfw_em9305_associated_slot_sdiv(uint32_t n,uint32_t d){return (uint32_t)((int32_t)n/(int32_t)d);}
static uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t id,uint32_t dir,uint32_t min,uint32_t max,uint32_t ext,uintptr_t out,uintptr_t cb){if(id!=1||dir||min!=2500||max!=3750||ext!=0x45||!cb)abort();*(uint32_t*)out=allocation;return slotok;}
static struct opencfw_em9305_native_product_pair opencfw_em9305_native_mpydu_329154(uint32_t a,uint32_t b){uint64_t p=(uint64_t)a*b;return (struct opencfw_em9305_native_product_pair){(uint32_t)p,(uint32_t)(p>>32)};}
static uint32_t opencfw_em9305_common_request_30455c(uint32_t n){if(n!=1)abort();common++;return 0;}
static uint32_t opencfw_em9305_command_count_30e4bc(void){count++;return 0;}
static uint32_t opencfw_em9305_radio_transfer_31dd88(uintptr_t p,uintptr_t in,uintptr_t s){if(p!=0x806390||in!=0x803bd8||s)abort();transfer++;return 0;}
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){return 77;}
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){if(p!=0x803c2c)abort();insert++;*(uint32_t*)0x803c34=0x111222;return 0;}
static uint32_t opencfw_em9305_init_state_status_send_3257a4(uint32_t c,uint32_t k,uint32_t l,uint32_t h){if(k!=0x53||l!=0x12345678||h!=0xabcdef)abort();code=c;status_calls++;return 0;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=4)abort();memset((void*)0x807000,0xa5,4);return allocfail?0:0x807000;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){if(h!=23||p!=0x807000)abort();memcpy(captured,(void*)p,4);posts++;return 123;}
#include "init-state-create-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
 for(mode=0;mode<2;mode++)for(slotok=0;slotok<2;slotok++)for(allocfail=0;allocfail<2;allocfail++)for(unsigned flag=0;flag<2;flag++){
 memset((void*)0x800000,0,0x10000);posts=status_calls=releases=parameters=transfer=insert=common=count=0;
 *(uint32_t*)0x805c78=0x804000;*(uint32_t*)0x805c70=0x806000;*(uint16_t*)0x804004=2;*(uint16_t*)0x804006=3;*(uint16_t*)(0x806390+592)=0x45;
 *(uint32_t*)0x804010=0x76543210;*(uint32_t*)0x804014=flag?0x10000:0;*(uint32_t*)0x804018=0x12345678;*(uint32_t*)0x80401c=0xabcdef;*(uint8_t*)0x804020=0x53;*(uint8_t*)0x805b18=23;*(uint16_t*)0x803bd2=7;
 uint32_t r=opencfw_em9305_init_state_action_31b4e0(0,0);
 if(mode&&slotok){if(r!=0x111222||status_calls||releases||posts||parameters!=1||transfer!=1||insert!=1||common!=1||count!=1||*(uint8_t*)0x805a74!=1||*(uint8_t*)0x805a75!=1||*(uint8_t*)0x805a76!=flag||*(uint16_t*)(0x806390+892)!=65535||*(uint8_t*)(0x806390+890)!=255||*(uint32_t*)(0x806390+516)!=0x12345678||*(uint32_t*)(0x806390+520)!=0xabcdef||*(uint8_t*)(0x806390+524)!=0x53||*(uint32_t*)0x803c38!=1305||*(uint32_t*)0x803c3c!=0x7654u*625u||*(uint32_t*)0x803bcc!=0x111222)abort();}
 else {if(r!=(allocfail?0u:123u)||status_calls!=1||code!=(mode?13u:9u)||releases!=mode||posts!=(allocfail?0u:1u)||parameters||transfer||insert||common||count)abort();if(!allocfail&&memcmp(captured,(uint8_t[]){0xa5,0xa5,3,3},4))abort();}
 cases++;
 }
 for(unsigned active=0;active<2;active++)for(unsigned state=0;state<8;state++)for(unsigned out=0;out<2;out++){
 *(uint32_t*)0x805c70=0x806000;*(uint8_t*)0x806390=active;*(uint8_t*)(0x806390+64)=state;*(uint32_t*)(0x806390+24)=0x123;*(uint32_t*)(0x806390+28)=0x456;*(uint32_t*)0x807008=0xa5;
 uint32_t r=opencfw_em9305_init_connection_query_31b21c(1,out?0x807008:0);unsigned valid=active&&state==4;if(r!=(valid?0x123u:0)||*(uint32_t*)0x807008!=(valid&&out?0x456u:0xa5u))abort();cases++;
 }
 for(unsigned i=0;i<256;i++){*(uint8_t*)0x805a76=i;if(opencfw_em9305_init_secondary_count_up_30e4cc()!=0x805a76||*(uint8_t*)0x805a76!=(uint8_t)(i+1))abort();cases++;}
 printf("PASS %u isolated state creation/helper cases\n",cases);return 0;}
