#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned writes,encodes,schedules,sets,found;static uint64_t packed;
static uint32_t opencfw_em9305_radio_address_write_3045e8(uintptr_t out,uint32_t low,uint32_t high){if(out!=0x809008&&out!=0x809002)abort();if(out==0x809008&&(low!=11||high!=12))abort();writes++;return 0;}
static uint64_t opencfw_em9305_controller_pack_address(uintptr_t in){if(in!=0x807008)abort();*(uint8_t*)0x807000=0;return packed;}
static uint32_t opencfw_em9305_radio_peer_set_303cc0(uint32_t kind,uint32_t low,uint32_t high,uintptr_t pair){if(kind!=4||low!=21||high!=22||*(uint32_t*)pair!=(uint32_t)packed)abort();sets++;return 0;}
static uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,uint32_t low,uint32_t high,uintptr_t out){if(kind!=4||low!=21||high!=22)abort();if(found){*(uint32_t*)out=31;*(uint32_t*)(out+4)=32;}return found;}
static uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t out,uintptr_t descriptor){if(out!=0x809000||descriptor!=0x803d1c||*(uint8_t*)(descriptor+3)!=3)abort();encodes++;*(uint8_t*)(descriptor+1)=1;return 0;}
static uint32_t opencfw_em9305_associated_slot_sdiv(uint32_t n,uint32_t d){return (uint32_t)((int32_t)n/(int32_t)d);}
static uint32_t opencfw_em9305_radio_schedule_313424(uint32_t period,uint32_t id,uint32_t stamp,uint32_t a,uint32_t b){if(period!=5000||id!=1||stamp!=1948||a||b)abort();schedules++;return 2500;}
struct opencfw_em9305_native_product_pair {uint32_t low,high;};
static struct opencfw_em9305_native_product_pair opencfw_em9305_native_mpydu_329154(uint32_t a,uint32_t b){uint64_t v=(uint64_t)a*b;return (struct opencfw_em9305_native_product_pair){v,v>>32};}
static uint32_t opencfw_em9305_schedule_remu(uint32_t a,uint32_t b){if(!b)abort();return a%b;}
#include "init-connection-callback-prepared.c"
#define W(a) (*(uint32_t*)(uintptr_t)(a))
#define B(a) (*(uint8_t*)(uintptr_t)(a))
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
for(unsigned active=0;active<2;active++)for(unsigned output=0;output<2;output++)for(unsigned flags=0;flags<2;flags++)for(unsigned mode=0;mode<2;mode++)for(found=0;found<2;found++)for(unsigned valid=0;valid<2;valid++){
memset((void*)0x800000,0,0x10000);writes=encodes=schedules=sets=0;packed=((uint64_t)(valid?0x4000:0xc000)<<32)|0xabcdef01;
W(0x80802c)=0x804000;B(0x804000+188)=active;W(0x804000+104)=output?0x809000:0;*(uint16_t*)0x803c0c=1;W(0x805c70)=0x806000;
W(0x804000+172)=12;W(0x804000+168)=11;W(0x804000+160)=100;B(0x804000+185)=2;B(0x804000+186)=3;B(0x804000+187)=4;
B(0x803bd5)=flags?2:0;B(0x804000+184)=mode;W(0x804000+180)=22;W(0x804000+176)=21;W(0x804000+84)=41;W(0x804000+88)=42;W(0x804000+80)=2;B(0x807000)=0xa0;*(uint16_t*)(0x806390+266)=4;
uint32_t result=opencfw_em9305_init_callback_3205c4(0x808000,0x807000);
if(!active||!output){if(result||writes||encodes||schedules)abort();}
else {if(result!=1||writes!=(flags?2u:1u)||encodes!=1||schedules!=1||sets!=(flags&&mode&&valid))abort();if(W(0x806390+24)!=4448||B(0x803c11)!=(flags&&mode?0:1))abort();uint32_t quotient=(uint32_t)(((uint64_t)2500*0x1a36e3>>31)&0xffff)%4;if(*(uint16_t*)0x803c00!=quotient||B(0x809016)!=(uint8_t)quotient||B(0x809017)!=(uint8_t)(quotient>>8))abort();if(flags&&B(0x803d1e)!=1)abort();}
cases++;
}
printf("PASS %u isolated full callback cases\n",cases);return 0;}
