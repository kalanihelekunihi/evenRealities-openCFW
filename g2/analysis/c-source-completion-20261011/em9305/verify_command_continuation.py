from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native continuation332d2c'):s.index('/* Native policy callback332db4')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned trace,stop,mutate,allocation,message;
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){assert(trace==0&&p==0x820000);trace=1;return 17;}
static uint32_t opencfw_em9305_wsf_pool_release(uintptr_t p){assert(trace==0&&p==0x840000);trace=2;return 99;}
static uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(trace==2&&p==0x850000);trace=3;return 98;}
uint32_t opencfw_em9305_command_stop_30b654(uintptr_t p){assert(p==0&&trace==0);stop++;if(mutate) *(uint8_t *)0x8058dc=mutate;return 97;}
uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==2&&trace==(message?3:2));trace=4;if(mutate==4) *(uint8_t *)0x8058dc=4;return 96;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4&&trace==4);trace=5;return allocation?0x860000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p){assert(trace==5&&handler==71&&p==0x860000&&*(uint16_t *)0x860002==261);trace=6;return 23;}
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x82002c=0x830000;*(uint32_t *)0x83006c=0x840000;*(uint8_t *)0x805b18=71;unsigned cases=0;
for(unsigned state=0;state<5;state++)for(unsigned limit=0;limit<4;limit++)for(unsigned count=0;count<4;count++)for(message=0;message<2;message++)for(allocation=0;allocation<2;allocation++)for(mutate=0;mutate<5;mutate++){*(uint8_t *)0x8058dc=state;*(uint16_t *)0x8058de=limit;*(uint16_t *)0x8058e2=count;*(uint16_t *)0x8058e4=0;*(uint16_t *)0x8058e6=0;*(uint8_t *)0x805a78=1;*(uint8_t *)0x805a79=0;*(uint32_t *)0x805a6c=message?0x850000:0;trace=stop=0;unsigned expectedstop=limit&&count>=limit;unsigned fresh=expectedstop&&mutate?mutate:state;unsigned finalstate=mutate==4?4:fresh;unsigned expected=fresh==2?17:finalstate==4?allocation?23:0:0x805a79;assert(opencfw_em9305_command_callback_332d2c(0x820000)==expected&&stop==expectedstop);if(fresh==2){assert(trace==1&&*(uint32_t *)0x805a6c==(message?0x850000:0));}else{assert(*(uint32_t *)0x805a6c==0);if(finalstate==4){assert(trace==(allocation?6:5)&&*(uint8_t *)0x8058dc==4&&*(uint8_t *)0x805a79==0);}else{assert(trace==4&&*(uint8_t *)0x8058dc==0&&*(uint8_t *)0x805a78==0&&*(uint8_t *)0x805a79==255);}}cases++;}
printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('command-continuation-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/c && /tmp/c'],text=True);print(a.strip());p.with_name('command-continuation-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual callback/count-down with controlled children, state mutations, limit stops, pending insert, releases, state4 allocation/send/null and byte underflow. No hardware runtime proof.'},indent=2)+'\n')
