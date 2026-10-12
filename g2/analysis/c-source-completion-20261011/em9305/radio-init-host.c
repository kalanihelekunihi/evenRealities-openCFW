#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
static uint32_t expected,trace[64],n;
static uint32_t lower(uint32_t incoming,uint32_t id){if(incoming!=expected)abort();trace[n++]=id;expected=expected*3u+id;return expected;}
uint32_t opencfw_em9305_init_lower_306ab4(uint32_t value){return lower(value,0x306ab4u);}
uint32_t opencfw_em9305_init_lower_306c44(uint32_t value){return lower(value,0x306c44u);}
uint32_t opencfw_em9305_init_lower_3077f4(uint32_t value){return lower(value,0x3077f4u);}
uint32_t opencfw_em9305_init_lower_307834(uint32_t value){return lower(value,0x307834u);}
uint32_t opencfw_em9305_init_lower_3079c4(uint32_t value){return lower(value,0x3079c4u);}
uint32_t opencfw_em9305_init_lower_307af8(uint32_t value){return lower(value,0x307af8u);}
uint32_t opencfw_em9305_init_lower_307bdc(uint32_t value){return lower(value,0x307bdcu);}
uint32_t opencfw_em9305_init_lower_307c18(uint32_t value){return lower(value,0x307c18u);}
uint32_t opencfw_em9305_init_lower_307cc8(uint32_t value){return lower(value,0x307cc8u);}
uint32_t opencfw_em9305_init_lower_307d2c(uint32_t value){return lower(value,0x307d2cu);}
uint32_t opencfw_em9305_init_lower_307d64(uint32_t value){return lower(value,0x307d64u);}
uint32_t opencfw_em9305_init_lower_307d74(uint32_t value){return lower(value,0x307d74u);}
uint32_t opencfw_em9305_init_lower_307de8(uint32_t value){uint32_t r=lower(value,0x307de8u);expected=*(uint8_t*)(uintptr_t)0x80604a;return r;}
uint32_t opencfw_em9305_init_lower_307e30(uint32_t value){return lower(value,0x307e30u);}
uint32_t opencfw_em9305_init_lower_307ec8(uint32_t value){return lower(value,0x307ec8u);}
uint32_t opencfw_em9305_init_lower_3080f8(uint32_t value){return lower(value,0x3080f8u);}
uint32_t opencfw_em9305_init_lower_30814c(uint32_t value){return lower(value,0x30814cu);}
uint32_t opencfw_em9305_init_lower_308630(uint32_t value){return lower(value,0x308630u);}
uint32_t opencfw_em9305_init_lower_309cb8(uint32_t value){return lower(value,0x309cb8u);}
uint32_t opencfw_em9305_init_lower_30a0a4(uint32_t value){return lower(value,0x30a0a4u);}
uint32_t opencfw_em9305_init_lower_30a134(uint32_t value){return lower(value,0x30a134u);}
uint32_t opencfw_em9305_init_lower_30a29c(uint32_t value){return lower(value,0x30a29cu);}
uint32_t opencfw_em9305_init_lower_30a328(uint32_t value){return lower(value,0x30a328u);}
uint32_t opencfw_em9305_init_lower_30a37c(uint32_t value){return lower(value,0x30a37cu);}
uint32_t opencfw_em9305_init_lower_30e42c(uint32_t value){return lower(value,0x30e42cu);}
uint32_t opencfw_em9305_init_lower_30e538(uint32_t value){return lower(value,0x30e538u);}
uint32_t opencfw_em9305_init_lower_30e564(uint32_t value){return lower(value,0x30e564u);}
uint32_t opencfw_em9305_init_lower_30e580(uint32_t value){return lower(value,0x30e580u);}
uint32_t opencfw_em9305_init_lower_30e594(uint32_t value){return lower(value,0x30e594u);}
uint32_t opencfw_em9305_init_lower_30e9e0(uint32_t value){return lower(value,0x30e9e0u);}
uint32_t opencfw_em9305_init_callback_30bf24(uint32_t a,uintptr_t b){(void)a;(void)b;abort();}
static uint32_t opencfw_em9305_controller_wsf_register(uintptr_t cb){if(cb!=(uintptr_t)&opencfw_em9305_init_callback_30bf24)abort();trace[n++]=0x3140b4;expected=17;return expected;}
uint32_t opencfw_em9305_init_final_30bf6c(uint32_t value){return lower(value,0x30bf6c);}
#include "radio-init-prepared.c"
int main(void){if(mmap((void*)0x800000,0x20000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();for(unsigned flag=0;flag<256;flag++){*(uint8_t*)0x80604a=flag;expected=0x806000;n=0;uint32_t result=opencfw_em9305_ll_radio_initialize(0x806000);if(result!=expected)abort();uint32_t want[]={0x30e564,0x307d74,0x307bdc,0x30e42c,0x307834,0x30e9e0,0x309cb8,0x30e42c,0x30a134,0x30e580,0x30814c,0x30e594,0x308630,0x30e564,0x307af8,0x307c18,0x307d2c,0x307cc8,0x3079c4,0x307d64,0x30e538,0x3077f4,0x30e9e0,0x30a29c,0x30a328,0x30a37c,0x30e538,0x30a0a4,0x306ab4,0x307de8,0};unsigned pos=0;for(unsigned i=0;want[i];i++)if(trace[pos++]!=want[i])abort();if(flag&&trace[pos++]!=0x3080f8)abort();uint32_t tail[]={0x306c44,0x307e30,0x307ec8,0x3140b4,0x30bf6c,0};for(unsigned i=0;tail[i];i++)if(trace[pos++]!=tail[i])abort();if(pos!=n)abort();}puts("PASS 256 init call-chain projections; genuine lower contracts controlled; no native/runtime claim");return 0;}
