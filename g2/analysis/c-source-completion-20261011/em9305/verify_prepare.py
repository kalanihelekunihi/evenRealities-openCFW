from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated stock334464'):s.index('/* Authenticated preparation state 32d694')];b=re.sub(r'__asm__ volatile\("div %0,%1,%2".*?;','index=delta/912u;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,calls;static char trace[16];static void mark(char c){trace[calls++]=c;}
uint32_t opencfw_em9305_radio_prepare_state_32d694(uintptr_t p,uintptr_t state,uintptr_t flag){assert(p==0x860000&&*(uint8_t *)(p+336)==255);*(uint32_t *)(state+4)=0x850000;*(uint8_t *)flag=scenario==5||scenario==6?0:1;mark('F');return scenario<=3?0:1;}
uintptr_t opencfw_em9305_ll_segment_header_323d70(uintptr_t out,uintptr_t p){assert(out==0x802808&&p==0x860000+336&&*(uint8_t *)p==1&&*(uint8_t *)(p+5)==0);mark('H');return 2;}
uint32_t opencfw_em9305_radio_request_current_303d58(uint32_t unused,uint32_t selector){(void)unused;assert(selector==1);*(uint8_t *)(0x850000+1)=9;mark('R');return 0;}
static uint32_t gate_callback(uint32_t id){assert(id==3);mark('I');return scenario==2?0:1;}
static uint32_t payload_callback(uint32_t low,uint32_t high){if(scenario==8)assert(low==55&&high==0);else assert(low==0x12345678&&high==0xabcdef01);*(uint8_t *)0x850000&=~32;mark('T');return 0;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<11;scenario++){memset((void *)0x800000,0,0x100000);calls=0;memset(trace,0,16);uintptr_t p=0x860000;unsigned force=scenario==1||scenario==7,gate=scenario!=0&&scenario!=10;*(uint32_t *)0x805c70=p-912*3;*(uint8_t *)(p+347)=scenario==10;*(uint8_t *)(p+379)=scenario==7;*(uint8_t *)(p+337)=1;*(uint8_t *)(p+2)=1;*(uint8_t *)(p+4)=scenario==5?2:0;*(uint8_t *)0x850000=scenario==5?0xa0:scenario==6?1:0xa1;*(uint8_t *)(0x850000+1)=7;
if(scenario==2||scenario==3||scenario==5){*(uint32_t *)0x805cd8=0x830000;*(uint32_t *)(uintptr_t)(0x830000+(scenario==5?8:12))=(uint32_t)(uintptr_t)gate_callback;}
if(scenario==8||scenario==9){*(uint32_t *)0x8052d0=(uint32_t)(uintptr_t)payload_callback;*(uint8_t *)(p+108)=1;*(uint8_t *)(p+111)=scenario==8?1:0;*(uint16_t *)(p+262)=55;*(uint32_t *)(p+456)=0x12345678;*(uint32_t *)(p+460)=0xabcdef01;}
unsigned result=opencfw_em9305_radio_prepare_32780c(p,force,gate);if(scenario==0){assert(result==0&&calls==0&&*(uint8_t *)(p+336)==0);}else if(scenario==2){assert(result==0&&strcmp(trace,"FI")==0);}else if(scenario==1||scenario==3||scenario==7){assert(result==2&&strcmp(trace,scenario==3?"FIHR":"FHR")==0);assert(*(uint8_t *)(p+339)==(scenario==7)&&*(uint8_t *)(p+379)==1&&*(uint8_t *)(p+380)==(scenario==7?0:1));}else{assert(result==(scenario==6?11:12));assert(strcmp(trace,scenario==5?"FIR":scenario==8||scenario==9?"FTR":"FR")==0);assert(*(uint8_t *)(p+341)==7&&*(uint8_t *)(p+339)==(scenario!=6));if(scenario==5)assert(*(uint8_t *)0x850000==0xa0);else if(scenario==6)assert(*(uint8_t *)0x850000==5);else assert(*(uint8_t *)0x850000==(scenario==8||scenario==9?0x95:0xb5));}cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('prepare-host.c');p.write_text(h);output=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);assert output.strip()=='PASS 11';print(output.strip())
raw=(root/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert raw[0x334464-0x302400:0x33446c-0x302400]==bytes([2,0,0,0,8,40,128,0])
p.with_name('prepare-host-receipt.json').write_text(json.dumps({'cases_passed':11,'template_bytes_verified':8,'scope':'Host fixed-RAM and controlled state/header/request children: early gates, empty branch, optional callback bypass, active flags, payload callback and fresh length. DIV normalized; no full child/native/layout/hardware proof.'},indent=2)+'\n')
