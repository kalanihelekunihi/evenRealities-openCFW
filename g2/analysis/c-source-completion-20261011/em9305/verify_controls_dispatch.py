from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
body=s[s.index('/* Native32f770..'):s.index('extern uint32_t opencfw_em9305_ll_controls_validate_32e378')]
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request,expected_command,expected_controls[5],new_command;
static uint8_t packet[16];static uint32_t child_status,expected_id;static unsigned calls,events,allocs,sends,allocation_ok,mutate;
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(n==1&&c==expected_command);allocs++;if(mutate)request=new_command;return allocation_ok?(uintptr_t)(packet+5):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)packet);assert(packet[5]==(request==0x207d?(uint8_t)child_status:0xa5));for(unsigned i=0;i<16;i++)if(i!=5)assert(packet[i]==0xa5);sends++;return 0xabcdef01;}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t status){assert(p==(uintptr_t)&request&&status==child_status);events++;return 0;}
uint32_t opencfw_em9305_ll_controls_apply_30d524(uintptr_t p){assert(memcmp((void*)p,expected_controls,10)==0);calls++;return child_status;}
uint32_t opencfw_em9305_ll_slot_controls_apply_30e0e0(uint32_t id,uintptr_t p){assert(id==expected_id&&memcmp((void*)p,expected_controls,10)==0);calls++;return child_status;}
"""+body+r"""
int main(void){unsigned count=0;uint8_t input[12];uint32_t statuses[]={0,2,12,18,255,256,0xdeadbeef};
for(unsigned c=0;c<65536;c++){
 if(c!=0x207d&&c!=0x207e){request=c;assert(opencfw_em9305_dispatch_32f64c((uintptr_t)&request,0)==0);count++;continue;}
 for(unsigned pattern=0;pattern<256;pattern++)for(unsigned st=0;st<7;st++)for(allocation_ok=0;allocation_ok<2;allocation_ok++)for(mutate=0;mutate<2;mutate++)for(unsigned change=0;change<2;change++){
 request=expected_command=c;new_command=change?0x207d:0x207e;child_status=statuses[st];calls=events=allocs=sends=0;memset(packet,0xa5,16);
 for(unsigned i=0;i<12;i++)input[i]=(uint8_t)(pattern+i*37);expected_id=input[0]+256u*input[1];unsigned off=c==0x207e?2:0;for(unsigned i=0;i<5;i++)expected_controls[i]=input[off+2*i]+256u*input[off+2*i+1];
 assert(opencfw_em9305_dispatch_32f64c((uintptr_t)&request,(uintptr_t)input)==1);assert(calls==1&&events==(c==0x207e)&&allocs==(c==0x207d)&&sends==(c==0x207d&&allocation_ok));count++;
 }}printf("%u\n",count);}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['32f64c..32f70a','32f770..32f792'],'scope':'Actual C with controlled genuine children; all commands, five halfword decoding, statuses, allocation failure, command reload mutation and untouched packet bytes. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
p=Path(__file__).with_name('controls-dispatch-receipt.json');p.write_text(json.dumps(r,indent=2)+'\n');print(f'PASS {cases} controls dispatch cases')
