from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30c944..'):s.index('/* Native30a6b4..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[40],handler_cell,controls[12];static _Alignas(2) uint8_t message[16];static unsigned id,active,flag,allocation_ok,status,mode,kind,active_calls,flag_calls,validations,allocations,copies,sends;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&id<3);active_calls++;return active;}
uint32_t opencfw_em9305_ll_slot_flag_307480(uint32_t x,uint32_t m){assert(x==id&&m==1);flag_calls++;return flag;}
uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t p){assert(p==(uintptr_t)controls&&kind==1);validations++;return status;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==(kind?16:6));allocations++;return allocation_ok?(uintptr_t)message:0;}
void *opencfw_em9305_memcpy(void *a,const void *b,uint32_t n){assert(a==message+4&&b==controls&&n==12&&*(uint16_t *)message==id&&*(uint16_t *)(message+2)==0x1d01);copies++;handler_cell=9;return memcpy(a,b,n);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(p==(uintptr_t)message&&h==(kind?9:7)&&*(uint16_t *)message==id);if(kind)assert(*(uint16_t *)(message+2)==0x1d01&&memcmp(message+4,controls,12)==0);else assert(*(uint16_t *)(message+2)==0x1e01&&message[4]==mode&&message[5]==0xa5);sends++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;unsigned statuses[]={0,18,0x12345678};
for(id=0;id<5;id++){for(active=0;active<2;active++){for(flag=0;flag<2;flag++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){for(unsigned si=0;si<3;si++){for(mode=0;mode<256;mode++){for(kind=0;kind<2;kind++){
 status=statuses[si];for(unsigned i=0;i<12;i++)controls[i]=(uint8_t)(mode+17*i);handler_cell=7;memset(message,0xa5,16);active_calls=flag_calls=validations=allocations=copies=sends=0;
 unsigned valid=id<3&&active,ready=valid&&flag;unsigned want=!valid?2:!flag?12:kind?status:0;
 unsigned result=kind?opencfw_em9305_ll_connection_modify_30c998(id,(uintptr_t)controls):opencfw_em9305_ll_connection_mode_30c944(id,mode);
 assert(result==want&&active_calls==(id<3)&&flag_calls==valid&&validations==(kind&&ready));unsigned allocated=ready&&(!kind||status==0);assert(allocations==allocated&&sends==(allocated&&allocation_ok)&&copies==(kind&&allocated&&allocation_ok));
 if(!sends)for(unsigned i=0;i<16;i++)assert(message[i]==0xa5);cases++;
}}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['30c944..30c996','30c998..30c9fe'],'scope':'Actual selected C with normalized RAM and controlled active/slotflag/validator/allocator/send; full mode-byte range, 12-byte controls, exact statuses, header-before-copy and handler-after-copy ordering; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-mode-modify-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connection mode/modify cases')
