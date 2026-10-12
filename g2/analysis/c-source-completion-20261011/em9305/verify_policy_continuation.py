from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native continuation332e2c'):s.index('/* Native stop30b654')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned stop,mutate,allocation,insert,release,duration,pattern,request,send;
uint32_t opencfw_em9305_command_stop_30b654(uintptr_t p){assert(p==0);stop++;if(mutate) *(uint8_t *)0x8058dc=mutate;return 99;}
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){assert(p==0x820000);insert++;return 17;}
static uint32_t opencfw_em9305_wsf_pool_release(uintptr_t p){assert(p==0x840000);release++;return 18;}
static uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==2&&release);request++;if(mutate==4) *(uint8_t *)0x8058dc=4;return 19;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4&&request);return allocation?0x850000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t n,uintptr_t p){assert(n==71&&p==0x850000&&*(uint16_t *)(p+2)==261);send++;return 23;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){*(uint8_t *)0x805a79-=1;return 0x805a79;}
static uint32_t opencfw_em9305_command_duration_332be4(uint32_t a,uint32_t b,uint32_t c){assert(a==13&&b==2&&c==1);duration++;return 65000;}
static uint32_t opencfw_em9305_command_pattern_332b94(uint32_t a,uint32_t b,uintptr_t p){assert(a==13&&b==5&&p==0x840000);pattern++;return 0;}
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x82002c=0x830000;*(uint32_t *)0x830068=0x840000;*(uint8_t *)0x805b18=71;unsigned cases=0;uint16_t counts[]={0,1,65535};
for(unsigned state=0;state<5;state++)for(unsigned limit=0;limit<4;limit++)for(unsigned ci=0;ci<3;ci++)for(unsigned mismatch=0;mismatch<6;mismatch++)for(allocation=0;allocation<2;allocation++)for(mutate=0;mutate<5;mutate++){*(uint8_t *)0x8058dc=state;*(uint16_t *)0x8058de=limit;*(uint16_t *)0x8058e0=counts[ci];*(uint8_t *)0x805a78=1;*(uint8_t *)0x805a79=0;*(uint8_t *)0x805996=19;*(uint8_t *)0x830001=mismatch==1?18:19;*(uint8_t *)0x805995=5;*(uint8_t *)0x840000=mismatch==2?4:37;*(uint8_t *)0x805994=13;*(uint8_t *)0x840001=mismatch==3?12:13;*(uint8_t *)0x805997=2;*(uint8_t *)0x83000c=mismatch==4?1:2;*(uint16_t *)0x805998=1;*(uint8_t *)0x83000e=mismatch==5?0:1;*(uint8_t *)0x83000f=77;*(uint16_t *)0x83006c=88;*(uint16_t *)0x83006e=99;stop=insert=release=duration=pattern=request=send=0;unsigned next=(uint16_t)(counts[ci]+1);unsigned expectedstop=limit&&next>=limit;unsigned fresh=expectedstop&&mutate?mutate:state;unsigned finalstate=mutate==4?4:fresh;unsigned result=fresh==1?17:finalstate==4?allocation?23:0:0x805a79;assert(opencfw_em9305_command_callback_332e2c(0x820000)==result&&stop==expectedstop&&*(uint16_t *)0x8058e0==next);if(fresh==1){assert(insert==1&&!release&&!request&&!send&&duration==(mismatch!=0)&&pattern==(mismatch!=0));if(mismatch)assert(*(uint8_t *)0x830001==19&&*(uint8_t *)0x83000c==2&&*(uint8_t *)0x83000d==2&&*(uint8_t *)0x83000e==1&&*(uint8_t *)0x83000f==0&&*(uint16_t *)0x83006c==15&&*(uint16_t *)0x83006e==65000);}else{assert(!insert&&!duration&&!pattern&&release==1&&request==1&&send==(finalstate==4&&allocation));if(finalstate!=4)assert(*(uint8_t *)0x8058dc==0&&*(uint8_t *)0x805a78==0&&*(uint8_t *)0x805a79==255);}cases++;}
printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('policy-continuation-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/q && /tmp/q'],text=True);print(a.strip());p.with_name('policy-continuation-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual full callback with controlled native children. Wrapped-count limits/stop mutation, five mismatch update paths, policy/packet bytes, duration and scheduling, release/state4 send/null/cleanup. No target runtime or DSP numeric proof.'},indent=2)+'\n')
