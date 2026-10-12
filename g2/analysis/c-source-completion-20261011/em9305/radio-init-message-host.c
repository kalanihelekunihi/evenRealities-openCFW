#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t message[8];static unsigned callbacks,resets,initializers,events,state;static uint32_t old;
static uint32_t cb(uintptr_t p,uintptr_t target){if(p!=(uintptr_t)message||target!=(uintptr_t)&cb||*(uint32_t*)0x805c78!=(uint32_t)p)abort();callbacks++;return 77;}
static uint32_t init(uintptr_t p){if(p!=(uintptr_t)&init||state!=1)abort();initializers++;return 99;}
static uint32_t opencfw_em9305_radio_address_reset_303e38(void){if(resets++)abort();return 77;}
static uintptr_t opencfw_em9305_radio_reset_30390c(void){if(resets++!=1)abort();return 88;}
static uint32_t opencfw_em9305_address_count_clear_303700(void){if(resets++!=2)abort();return 99;}
static uint32_t opencfw_em9305_init_state_30e9a4(uint32_t v){if(resets!=3||v!=0x805f04||*(uint16_t*)0x805f1c||*(uint32_t*)0x805f18||*(uint32_t*)0x805f14||*(uint8_t*)0x805f04||*(uint8_t*)0x805f05!=old)abort();state=1;return 42;}
static uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){if(*(uint32_t*)p!=0x10000||*(uint8_t*)0x8051f8||state!=1||resets!=3)abort();events++;return 0xabcdef;}
#include "radio-init-message-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned vectors=0;for(unsigned type=0;type<256;type++)for(unsigned present=0;present<2;present++)for(unsigned pending=0;pending<2;pending++)for(unsigned busy=0;busy<2;busy++)for(unsigned tail=0;tail<2;tail++){
for(unsigned i=0;i<256;i++)*(uint32_t*)(uintptr_t)(0x802950u+i*4)=present?(uintptr_t)&cb:0;
for(unsigned i=1;i<=22;i++)*(uint32_t*)(uintptr_t)(0x805200u+i*4)=present?(uintptr_t)&init:0;
message[2]=type;message[3]=tail;*(uint8_t*)0x8051f8=pending;*(uint8_t*)0x805a79=busy;old=type;memset((void*)0x805f04,old,28);callbacks=resets=initializers=events=state=0;unsigned doreset=(pending||(type==255&&!tail))&&!busy;uint32_t expected=doreset?0xabcdef:(pending||(type==255&&!tail))?busy:0;uint32_t r=opencfw_em9305_init_message_3075cc((uintptr_t)message);if(r!=expected||callbacks!=(present?(type==255?22u:1u):0u)||resets!=(doreset?3u:0u)||initializers!=(doreset&&present?22u:0u)||events!=doreset||*(uint8_t*)0x8051f8!=(doreset?0u:(pending||(type==255&&!tail))))abort();vectors++;}
printf("PASS %u complete message/reset source projections; runtime registered callbacks and genuine reset children controlled\n",vectors);return 0;}
