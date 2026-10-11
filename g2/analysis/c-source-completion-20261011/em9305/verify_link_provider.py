from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native306a20..306a7c'):s.index('/* Native3319bc..331a40')].replace('*(volatile uint32_t *)(uintptr_t)0x805c70u','records_pointer').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_byte').replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t link[16],records[912*2],event[16];static uintptr_t records_pointer;static uint8_t handler_byte;static unsigned found,ok,allocs,sends,set,mode;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t handle){assert(handle==123);return found?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes){assert(bytes==(set?6:4));allocs++;link[6]=1;handler_byte=77;return ok?(uintptr_t)event:0;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p){assert(handler==77&&p==(uintptr_t)event&&event[0]==1&&event[1]==0&&event[2]==1&&event[3]==(set?38:37));if(set)assert(event[4]==(uint8_t)mode);sends++;return 99;}
'''+body+r'''
int main(void){unsigned n=0;for(found=0;found<2;found++)for(unsigned busy=0;busy<256;busy++)for(unsigned state=0;state<4;state++)for(unsigned present=0;present<2;present++)for(unsigned active=0;active<2;active++)for(ok=0;ok<2;ok++)for(set=0;set<2;set++){memset(link,0,16);memset(records,0,sizeof(records));link[2]=busy;link[3]=state;records[2]=active;records_pointer=present?(uintptr_t)records:0;allocs=sends=0;mode=0x1234;unsigned result=!found?2:busy||state==2?12:!present?2:!active?12:0;uint32_t got=set?opencfw_em9305_link_mode_30c940(123,mode):opencfw_em9305_link_query_30aec4(123);assert(got==result&&allocs==(result==0)&&sends==(result==0&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('link-provider-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C with normalized RAM/children and arithmetic MPYUW substitute. Full busy bytes/status gates, allocation outcomes, fresh handler/id and low-byte mode. ARC ISA/native timing/hardware not proved.'},indent=2)+'\n');print('PASS',n)
