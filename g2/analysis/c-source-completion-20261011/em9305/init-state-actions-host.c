#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned mode,callbacks,releases,removes,count_calls,term_calls,common_calls;static uint8_t captured[38];static unsigned captured_size;
static void *opencfw_em9305_memset(void *d,uint32_t v,uint32_t n){return memset(d,v,n);}
static uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event){uint8_t *p=(uint8_t *)event;captured_size=p[2]==8?6:38;memcpy(captured,p,captured_size);callbacks++;return p[2]==8?123:223;}
static uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t out,uint32_t low,uint32_t high){uint8_t *p=(uint8_t *)out;for(unsigned i=0;i<4;i++)p[i]=low>>(i*8);p[4]=high;p[5]=high>>8;return out;}
static uint32_t opencfw_em9305_wsf_event_release(uintptr_t event){releases++;if(mode==1&&releases==1){if(event!=0x700)abort();*(uint32_t *)(uintptr_t)(0x803b94+308)=0x702;}if(mode==1&&releases==2&&event!=0x702)abort();return 99;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){count_calls++;return 0;}
static uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){(void)handler;
 if(mode==2){uintptr_t expected[]={0x803bbc,0x803bbc,0x803bc4,0x803bf4,0x803c24};uintptr_t values[]={0x800,0,0x801,0x802,0};if(removes>=5||queue!=expected[removes])abort();return values[removes++];}
 removes++;return 0;
}
static uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t record,uint32_t reason){if(record!=0x806000+2*912||(reason!=76&&reason!=77))abort();term_calls++;return 0;}
static uint32_t opencfw_em9305_common_release_304588(uint32_t n){if(n!=1)abort();common_calls++;return 0;}
#include "init-state-actions-prepared.c"
static void reset(void){mode=callbacks=releases=removes=count_calls=term_calls=common_calls=0;memset((void *)0x803b94,0,500);}
int main(void){if(mmap((void *)0x800000,0x10000,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)0x800000)abort();unsigned cases=0;
 reset();if(opencfw_em9305_init_state_action_31b4a4(0,0)!=123||captured_size!=6||memcmp(captured,(uint8_t[]){0,0,8,12,12,0},6))abort();
  cases++;
 for(unsigned code=0;code<256;code++){
  reset();if(opencfw_em9305_init_state_status_send_3257a4(code,0x153,0x76543210,0xabcd)!=223)abort();
  uint8_t expected[38]={0};expected[2]=5;expected[3]=expected[4]=code;expected[9]=0x53;memcpy(expected+10,(uint8_t[]){0x10,0x32,0x54,0x76,0xcd,0xab},6);expected[35]=expected[36]=expected[37]=255;
  if(captured_size!=38||memcmp(captured,expected,38))abort();
  cases++;
 }
 reset();*(uint32_t *)(uintptr_t)0x805c78=0x804000;*(uint32_t *)(uintptr_t)0x80401c=0xabcd;*(uint32_t *)(uintptr_t)0x804018=0x76543210;*(uint8_t *)(uintptr_t)0x804020=0x53;
 if(opencfw_em9305_init_state_action_31b4c8(0,0)!=223||captured[3]!=12||captured[9]!=0x53)abort();
  cases++;
 reset();mode=1;*(uint32_t *)(uintptr_t)(0x803b94+300)=0x700;*(uint32_t *)(uintptr_t)(0x803b94+308)=0x701;
 if(opencfw_em9305_init_state_events_clear_322884(0x803b94)!=99||releases!=2||*(uint32_t *)(uintptr_t)(0x803b94+300)||*(uint32_t *)(uintptr_t)(0x803b94+308))abort();
  cases++;
 reset();mode=2;*(uint8_t *)(uintptr_t)(0x803b94+66)=1;*(uint8_t *)(uintptr_t)0x805a76=0;*(uint8_t *)(uintptr_t)0x805a74=5;
 if(opencfw_em9305_init_state_cleanup_325740(0x803b94)!=0||releases!=3||removes!=5||count_calls!=1||*(uint8_t *)(uintptr_t)0x805a76!=255||*(uint8_t *)(uintptr_t)0x805a74!=0)abort();
  cases++;
 for(unsigned which=0;which<2;which++){
  reset();*(uint16_t *)(uintptr_t)0x803c0c=2;*(uint32_t *)(uintptr_t)0x805c70=0x806000;*(uint32_t *)(uintptr_t)0x803cbc=0xabcd;*(uint32_t *)(uintptr_t)0x803cb8=0x76543210;*(uint8_t *)(uintptr_t)0x803cac=0x53;
  uint32_t result=which?opencfw_em9305_init_state_action_31b648(0,0):opencfw_em9305_init_state_action_31b614(0,0);
  if(result!=(which?223u:0u)||term_calls!=1||common_calls!=1||count_calls!=1||callbacks!=(which?2u:0u))abort();
  if(which&&(captured[3]!=2||captured[9]!=3))abort();
  cases++;
 }
 printf("PASS %u isolated state action/status/cleanup cases\n",cases);return 0;}
