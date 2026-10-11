from pathlib import Path
import re
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native3093a0'):s.index('/* Native31ac08')];b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?:"r"\((\w+)\),"r"\(1250u\)\);',lambda m:m.group(0).split('"=r"(')[1].split(')')[0]+'='+m[1]+'*1250u;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
static uint32_t found,ready,duration;static unsigned resets,calls;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==7);return found?0x880000:0;}
uint32_t opencfw_em9305_radio_record_ready_31ac08(uint32_t id){assert(id==7);return ready;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){resets++;return memset(p,v,n);}
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){assert(a==3&&b==0&&c==0&&d==90&&e==4&&f==0&&g==2&&h==5);calls++;return duration;}
uint32_t opencfw_em9305_radio_access_raw_318878(void){return 0x12345678;}
uint32_t opencfw_em9305_radio_callback_32d7f4(uintptr_t p){(void)p;return 0;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);_Alignas(4) uint8_t input[12]={6,0,12,0,9,0,2,8,3,4,5,0};unsigned cases=0;
for(unsigned scenario=0;scenario<8;scenario++){
memset((void *)0x800000,0,0x100000);uintptr_t r=0x880000,config=0x870000,buffer=0x860000,control=0x850000;found=scenario!=0;ready=scenario!=1&&scenario!=2;duration=scenario==4?15001:15000;resets=calls=0;
*(uint32_t *)0x805cac=config;*(uint8_t *)(config+13)=scenario==1?0:2;*(uint16_t *)(config+20)=80;
*(uint32_t *)(r+72)=90;*(uint8_t *)(r+63)=3;*(uint16_t *)(r+1144)=4;*(uint32_t *)(r+1160)=buffer;*(uint32_t *)(r+2812)=control;
*(uint32_t *)(0x80517c+4)=control;*(uint32_t *)0x80517c=buffer;*(uint32_t *)0x805ce4=0x890000;
*(uint8_t *)(r+369)=scenario==3;*(uint8_t *)(r+32)=scenario==5?1:0;
unsigned expected=scenario==0?66:scenario==1?7:scenario==3?12:scenario==4?69:scenario==5?18:0;
assert(opencfw_em9305_command_apply_3093a0(7,(uintptr_t)input)==expected);
if(scenario<2){assert(resets==0&&calls==0);}else{assert(resets==(scenario==2?2:1));assert(*(uint32_t *)(buffer+3844)==32767&&*(uint32_t *)(buffer+3848)==0);for(unsigned n=0;n<64;n++)assert(*(uint8_t *)(buffer+3852+n)==255);assert(calls==(scenario==3?0:1));}
if(scenario==2){assert(*(uint8_t *)(0x80517c+8)==1&&*(uint8_t *)(0x80517c+9)==7);assert(*(uint32_t *)control==0x890000);}
if(expected==0){assert(*(uint32_t *)(r+712)==15000&&*(uint32_t *)(r+708)==7500);assert(*(uint16_t *)(r+716)==9&&*(uint8_t *)(r+718)==1);assert(*(uint32_t *)(r+784)==0x12345678&&*(uint32_t *)(r+792)==10000);assert(*(uint8_t *)(r+788)==2&&*(uint8_t *)(r+789)==8&&*(uint16_t *)(r+796)==1027&&*(uint8_t *)(r+798)==5&&*(uint16_t *)(control+76)==15);}
cases++;}
printf("PASS %u\n",cases);}
'''
p=root/'g2/analysis/c-source-completion-20261011/em9305/command-config-host.c';p.write_text(h)

import subprocess,json
image='opencfw/qemu-csky-builddeps:20261009t201800'
relative=p.relative_to(root)
output=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work',image,'sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(relative)+' -o /tmp/test && /tmp/test'],text=True)
assert output.strip()=='PASS 8'
p.with_name('command-config-host-receipt.json').write_text(json.dumps({'cases_passed':8,'scope':'Host normalized MPYUW, controlled child providers and fixed RAM: absent record, no pool, pool claim, busy, duration, flags, successful stores. No native runtime/hardware proof.'},indent=2)+'\n')
print(output.strip())
