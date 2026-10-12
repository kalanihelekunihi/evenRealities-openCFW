from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text().split('/* Native command30e120')[1].split('/* Native pattern332b94')[0]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned alloc,allocs,patterns,requests,inserts,pending,bounds,clamps,enters,exits;
static uint32_t opencfw_em9305_ll_command_pending_310634(void){pending++;return 0;}
static uint32_t opencfw_em9305_ll_signed_bounds_31026c(uintptr_t l,uintptr_t u){bounds++;*(uint8_t *)l=156;*(uint8_t *)u=10;return 10;}
static uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t n){clamps++;return n+1;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
static uint32_t opencfw_em9305_wsf_critical_enter(void){enters++;return 0;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 0;}
static uint32_t opencfw_em9305_command_channel_332c30(uint32_t n){return n? n<12?n-1:n==12?38:n>=39?39:n-2:37;}
static uintptr_t opencfw_em9305_wsf_pool_allocate(uint32_t n){assert(n==257);allocs++;return alloc?0x840000:0;}
static uint32_t opencfw_em9305_command_count_30e4bc(void){return ++*(uint8_t *)0x805a79;}
static uint32_t opencfw_em9305_common_request_30455c(uint32_t n){assert(n==2||n==3);requests++;return 99;}
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t n){assert(n==0x8058f4);inserts++;return 99;}
uint32_t opencfw_em9305_command_duration_332be4(uint32_t a,uint32_t b,uint32_t c){assert(a==19);return a+10*b+1000*c;}
uint32_t opencfw_em9305_command_pattern_332b94(uint32_t a,uint32_t b,uintptr_t p){assert(a==19&&b<8&&p==0x840000);patterns++;return 98;}
uint32_t opencfw_em9305_command_callback_332e2c(uintptr_t a){(void)a;return 0;}
uint32_t opencfw_em9305_command_callback_332db4(uintptr_t a,uint32_t b){(void)a;(void)b;return 0;}
/* Native command30e120'''+s+r'''
static uint8_t in[24];
static void setup(unsigned state){memset((void *)0x8058dc,0xa5,512);memset((void *)0x805a70,0,16);*(uint8_t *)0x8058dc=state;memset(in,0,24);in[3]=19;*(uint16_t *)in=0x1234;allocs=patterns=requests=inserts=pending=bounds=clamps=enters=exits=0;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned powers[]={128,130,155,156,0,10,11,21,126,127};
for(unsigned state=0;state<2;state++)for(unsigned kind=0;kind<9;kind++)for(unsigned mode=0;mode<6;mode++)for(unsigned pi=0;pi<10;pi++)for(unsigned features=0;features<4;features++)for(alloc=0;alloc<2;alloc++){setup(state);in[2]=39;in[4]=kind;in[5]=mode;in[16]=powers[pi];*(uint8_t *)0x805995=kind;*(uint8_t *)0x805a95=(features&1?1:0)|(features&2?8:0);int power=(int8_t)in[16];unsigned range=power==126||power==127;unsigned expected=kind>=8||mode<1||mode>4?48:mode==2&&!(features&1)?17:mode>=3&&!(features&2)?17:!range&&(power<-126||power>20)?48:!range&&(power<-100||power>10)?17:kind==3||state?0:alloc?0:31;assert(opencfw_em9305_command_30e120((uintptr_t)in)==expected);unsigned reached=kind<8&&mode>=1&&mode<=4&&(mode==1||(mode==2?(features&1):(features&2)));assert(pending==reached&&bounds==reached);unsigned good=expected==0||expected==31;if(good){unsigned adjusted=power==126?156:power==127?10:(uint8_t)(power+1);assert(in[16]==adjusted);if(kind==3){assert(requests==1&&inserts==0&&allocs==0&&*(uint8_t *)0x8058dc==1&&*(uint8_t *)0x805995==3);}else{assert(enters==1&&exits==1&&*(uint8_t *)0x805994==19&&*(uint8_t *)0x805995==kind&&*(uint8_t *)0x805996==39&&*(uint8_t *)0x8059a8==adjusted);if(state){assert(!allocs&&!patterns&&!requests&&!inserts);}else{unsigned m=mode>=3?3:mode;unsigned encoding=mode==3?2:mode==4?1:0;unsigned duration=19+10*m+1000*encoding;assert(allocs==1&&patterns==alloc&&requests==alloc&&inserts==alloc&&*(uint16_t *)0x805992==duration&&*(uint16_t *)0x805990==257&&*(uint32_t *)0x80598c==(alloc?0x840000:0));}}}cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-2034-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/d && /tmp/d'],text=True);print(a.strip());p.with_name('command-2034-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual complete parent with controlled native child contracts. Guards, power boundary/sentinel paths, active update, kind3 path, record allocation/pattern/schedule. No DSP/runtime/hardware proof.'},indent=2)+'\n')
