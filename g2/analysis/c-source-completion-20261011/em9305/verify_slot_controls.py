from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native32e378..'):s.index('extern uint32_t opencfw_em9305_ll_test_30b1ac')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','((uintptr_t)config_data)').replace('*(volatile uint32_t *)(uintptr_t)0x805c70u','((uintptr_t)slots)')
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x805a98u','feature').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','runtime_handler')
for i in range(5):body=body.replace(f'(uintptr_t)0x{0x805ad0+2*i:x}u',f'(uintptr_t)(shared+{2*i})')
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('__asm__ volatile("mpywhul %0,%1,%2":"=r"(span):"r"(periods),"r"(maximum));','span=periods*maximum;').replace('__asm__ volatile("mpyuw %0,%1,10":"=r"(available):"r"(timeout));','available=timeout*10u;').replace('__asm__ volatile("mpy %0,%1,%2":"=r"(required):"r"(rounded),"r"(span));','required=rounded*span;')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t config_data[64],slots[1824],shared[10],message[4],feature,runtime_handler;
static unsigned active,alloc_ok,allocs,sends,copies;static uint16_t controls[5];static uint32_t selected;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==selected);return active;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4);allocs++;return alloc_ok?(uintptr_t)message:0;}
void *opencfw_em9305_memcpy(void *dst,const void *src,uint32_t n){assert(n==10&&dst==slots+selected*912+856&&src==controls);copies++;return memcpy(dst,src,n);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==runtime_handler&&m==(uintptr_t)message&&*(uint16_t*)message==selected&&*(uint16_t*)(message+2)==0x2901);sends++;return 99;}
"""+body+r"""
int main(void){unsigned count=0;unsigned iv[]={0,1,3,4,6,100,65535},timeouts[]={9,10,100,3200,3201};
for(selected=0;selected<3;selected++){for(active=0;active<2;active++){for(unsigned f=0;f<2;f++){for(unsigned sf=0;sf<2;sf++){for(unsigned busy=0;busy<2;busy++){for(unsigned state=0;state<2;state++){for(alloc_ok=0;alloc_ok<2;alloc_ok++){for(unsigned i=0;i<7;i++){for(unsigned t=0;t<5;t++){for(unsigned lat=0;lat<3;lat++){
 memset(config_data,0,64);config_data[34]=2;memset(slots,0,1824);memset(shared,0xa5,10);memset(message,0xa5,4);feature=f?64:0;runtime_handler=7;allocs=sends=copies=0;
 uint8_t *slot=slots+(selected%2)*912;*(uint16_t*)(slot+266)=iv[i];slot[548]=sf?64:0;slot[888]=busy;slot[2]=state;controls[0]=1;controls[1]=2;controls[2]=lat;controls[3]=1;controls[4]=timeouts[t];
 uint32_t required=(iv[i]+(iv[i]+3)/4)*(lat+1)*2*2;unsigned expected=selected>=2||!active?2:timeouts[t]<10||timeouts[t]>3200?18:timeouts[t]*10<required?18:!f||!sf?26:busy?12:0;
 unsigned proceed=selected<2&&active&&timeouts[t]>=10&&timeouts[t]<=3200&&timeouts[t]*10>=required&&f&&sf&&!busy;
 assert(opencfw_em9305_ll_slot_controls_apply_30e0e0(selected,(uintptr_t)controls)==expected);assert(allocs==proceed&&sends==(proceed&&alloc_ok)&&copies==sends);
 if(proceed&&!state)assert(memcmp(shared,controls,10)==0);else for(unsigned b=0;b<10;b++)assert(shared[b]==0xa5);
 if(sends)assert(memcmp(slot+856,controls,10)==0);count++;
}}}}}}}}}}printf("%u\n",count);}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('slot-controls-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual connected C validator and slot apply with normalized runtime addresses/ISA products and controlled children. Native named multiplication retained in target source; no ISA/native runtime equality claim.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
