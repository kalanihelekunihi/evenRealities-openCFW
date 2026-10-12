#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static void failure(unsigned line){fprintf(stderr,"failure line%u\n",line);exit(1);}
#define abort() failure(__LINE__)
static unsigned allocfail,encodes,signals;static unsigned counters;static uint32_t seen_low,seen_high;
static uint32_t opencfw_em9305_init_callback_320908(uintptr_t a,uint32_t b){return (uint32_t)a+b;}
static uint32_t opencfw_em9305_init_callback_3205c4(uintptr_t a,uint32_t b){return (uint32_t)a+b;}
static void*opencfw_em9305_memset(void*d,uint32_t v,uint32_t n){if((uintptr_t)d!=0x803c2c||v||n!=240)abort();return memset(d,v,n);}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=45)abort();return allocfail?0:0x807000;}
static uint32_t opencfw_em9305_auxiliary_signal_304394(void){if(*(uint8_t*)0x803c28!=1)abort();signals++;return 99;}
static uint32_t opencfw_em9305_radio_access_raw_318878(void){if(*(uint32_t*)0x803cc0!=(allocfail?0u:0x807000u))abort();counters++;return 0x12345678;}
static uint32_t opencfw_em9305_radio_crc_seed_318960(void){if(*(uint32_t*)0x803be8!=0x12345678)abort();counters++;return 0xabcdef01;}
static uint32_t opencfw_em9305_associated_random_31896c(void){counters++;return 0x345;}
static uint32_t opencfw_em9305_compose_accuracy_318988(void){if(*(uint8_t*)0x803c02!=0x45)abort();counters++;return 0x67;}
static uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t out,uintptr_t input){if(out!=0x803b94||input!=0x803d1c||encodes)abort();encodes++;seen_low=*(uint32_t*)0x803cac;seen_high=*(uint32_t*)0x803cb4;return 2;}
static uint32_t opencfw_em9305_radio_encode_323c94(uintptr_t out,uintptr_t input){if(out!=0x803b96||input!=0x803bd8||encodes!=1)abort();encodes++;return 34;}
#include "init-connection-parameters-host-view.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
 for(unsigned type=0;type<2;type++)for(unsigned address_kind=0;address_kind<2;address_kind++)for(unsigned privacy=0;privacy<2;privacy++)for(unsigned kind=0;kind<2;kind++)for(allocfail=0;allocfail<2;allocfail++)for(unsigned flags=0;flags<8;flags++){
 memset((void*)0x800000,0,0x10000);encodes=counters=0;*(uint8_t*)0x803bd6=type;*(uint8_t*)0x803bd5=address_kind;*(uint16_t*)0x803c0e=9;
 *(uint8_t*)0x805b00=flags;*(uint8_t*)0x805a9c=0x42;*(uint8_t*)0x805a9d=privacy;*(uint32_t*)0x805a94=1u<<14;*(uint32_t*)0x805aa0=0x77889900;*(uint32_t*)0x805aa4=0xaabbccdd;
 *(uint32_t*)0x805b40=0x11112222;*(uint32_t*)0x805b44=0x33334444;*(uint32_t*)0x805a8c=0x55556666;*(uint32_t*)0x805a90=0x77778888;
 *(uint16_t*)0x804004=11;*(uint16_t*)0x804006=12;
 if(opencfw_em9305_init_connection_parameters_32074c(0x804000,kind,0x76543210,0xfedcba98)!=36||encodes!=2||counters!=4)abort();
 unsigned channel=(flags&1)?((flags&2)?((flags&4)?37:39):38):37;
 uint32_t address_flags=(address_kind?2u:0u)|(privacy?81u:1u);
 if(seen_low!=(address_flags|(!type?((kind<<3)|4u):0u))||seen_high!=(address_kind?0x77778888u:0x33334444u)||*(uint8_t*)0x803c5d!=channel||*(uint8_t*)0x803c03!=0x67||*(uint8_t*)0x803d1d!=1||*(uint8_t*)0x803d1e!=address_kind||*(uint32_t*)0x803cc0!=(allocfail?0u:0x807000u)||*(uint32_t*)0x803c48!=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_320908||*(uint32_t*)0x803cd0!=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3205c4||*(uint32_t*)0x803cd8!=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31e5ec||*(uint32_t*)0x803cc4!=0x803b94||*(uint8_t*)0x803cf1!=36)abort();
 if(!type&&(*(uint32_t*)0x803cac!=(address_flags|(kind<<3)|4u)||*(uint32_t*)0x803cb8!=0x76543210||*(uint32_t*)0x803cbc!=0xfedcba98||*(uint32_t*)0x803be0!=0x76543210||*(uint32_t*)0x803be4!=0xfedcba98))abort();
 cases++;
 }
 signals=0;if(opencfw_em9305_init_callback_31e5ec(1,2)!=0||signals!=1)abort();cases++;
 printf("PASS %u isolated parameter/callback cases (XBFU host substitution)\n",cases);return 0;}
