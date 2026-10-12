#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned totals[3],positions[3],release_count,recycles,timers,critical,exits,callbacks,countdown;static uintptr_t expected_release[1024];static unsigned expected_count;static unsigned enabled;
static uint32_t opencfw_em9305_associated_slot_sdiv(uint32_t n,uint32_t d){return (uint32_t)((int32_t)n/(int32_t)d);}
static uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){unsigned q=queue==0x806390+368?0:queue==0x806390+360?1:queue==0x806390+352?2:3;if(q==3)abort();unsigned i=positions[q]++;if(i>=totals[q])return 0;*(uint8_t*)handler=(i%2)?255:1;uintptr_t event=0x808000+q*0x1000+i*8;*(uint32_t*)event=0x80c000+i*8;return event;}
static uint32_t opencfw_em9305_wsf_event_release(uintptr_t e){if(release_count>=expected_count||e!=expected_release[release_count])abort();release_count++;return 3;}
static uint32_t opencfw_em9305_wsf_queue_append(uintptr_t q,uintptr_t n){if(q!=0x8056dc||n<0x808ff8||n>=0x809800)abort();recycles++;return 4;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){critical++;return 2;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 5;}
static uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer){uintptr_t offsets[]={384,728,476,496};if(timers>=4||timer!=0x806390+offsets[timers])abort();timers++;return 6;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){countdown++;*(uint8_t*)0x805a70=3;return 0;}
static uint32_t opencfw_em9305_common_release_304588(uint32_t index){if(index!=1)abort();return 7;}
static uint32_t second(uint32_t id,uintptr_t callee){if(id!=1||callee!=(uintptr_t)second||*(uint8_t*)0x806390!=1)abort();callbacks++;*(uint32_t*)(0x806390+760)=0x80f000;return 9;}
static uint32_t first(uint32_t id,uintptr_t callee){if(id!=1||callee!=(uintptr_t)first||*(uint8_t*)0x806390!=1)abort();callbacks++;*(uint32_t*)0x8027f4=(uint32_t)(uintptr_t)second;return 8;}
#include "init-connection-release-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;unsigned sizes[]={0,1,2,3,255,256};
 for(unsigned a=0;a<6;a++)for(unsigned b=0;b<6;b++)for(unsigned c=0;c<6;c++)for(enabled=0;enabled<2;enabled++){
 memset((void*)0x800000,0,0x10000);release_count=recycles=timers=critical=exits=callbacks=countdown=expected_count=0;memset(positions,0,sizeof positions);
 totals[0]=sizes[a];totals[1]=sizes[b];totals[2]=sizes[c];
 for(unsigned q=0;q<3;q++)for(unsigned i=0;i<totals[q];i++){uintptr_t e=0x808000+q*0x1000+i*8;expected_release[expected_count++]=(q==1&&i%2==0)?0x80c000+i*8-4:e;}
 *(uint32_t*)0x805c70=0x806000;*(uint8_t*)0x806390=1;*(uint8_t*)0x805ab4=254;*(uint8_t*)0x805ab5=253;
 if(enabled){*(uint32_t*)0x805cd8=0x804000;*(uint32_t*)0x804004=(uint32_t)(uintptr_t)first;expected_release[expected_count++]=0x80f000;}
 if(opencfw_em9305_init_connection_release_31ad90(0x806390)!=7||release_count!=expected_count||recycles!=(totals[1]+1)/2||timers!=4||critical!=1+(totals[1]+1)/2+(totals[2]+1)/2||exits!=critical||callbacks!=enabled*2||countdown!=1||*(uint8_t*)0x806390||*(uint8_t*)0x805a70!=2||*(uint8_t*)0x805ab4!=(uint8_t)(254+(totals[1]+1)/2+(totals[2]+1)/2)||*(uint8_t*)0x805ab5!=(uint8_t)(253+totals[0]))abort();
 cases++;
 }
 printf("PASS %u isolated release/queue/callback cases\n",cases);return 0;}
