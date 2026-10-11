from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30c998..'):s.index('/* Native3073ec..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_cell')
body=body.replace('__asm__ volatile("mpywhul %0,%1,%2":"=r"(span):"r"(periods),"r"(maximum));','span=periods*maximum;').replace('__asm__ volatile("mpywhl %0,%1,%2":"=r"(required):"r"(span),"r"(factor));','required=span*factor;').replace('__asm__ volatile("mpyuw %0,%1,10000":"=r"(available):"r"(timeout));','available=timeout*10000u;')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[40],handler_cell=7;static uint16_t controls[6];static _Alignas(2) uint8_t message[16];static unsigned sends,allocations;
uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t);
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==1);return 1;}
uint32_t opencfw_em9305_ll_slot_flag_307480(uint32_t id,uint32_t mask){assert(id==1&&mask==1);return 1;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==16);allocations++;return (uintptr_t)message;}
void *opencfw_em9305_memcpy(void *a,const void *b,uint32_t n){assert(a==message+4&&b==controls&&n==12&&*(uint16_t *)message==1);return memcpy(a,b,n);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==7&&p==(uintptr_t)message&&*(uint16_t *)(message+2)==0x1d01&&memcmp(message+4,controls,12)==0);sends++;return 7;}
"""+body+r"""
static unsigned model(void){uint32_t a=controls[0],b=controls[1],c=controls[2],d=controls[3];return a<6||b<a||b>3200||c>499||d<10||d>3200||4ull*d<=(uint64_t)(c+1)*b?18:0;}
static void check(void){unsigned want=model();assert(opencfw_em9305_ll_connection_parameters_validate_30a6b4((uintptr_t)controls)==want);sends=allocations=0;memset(message,0xa5,16);assert(opencfw_em9305_ll_connection_modify_30c998(1,(uintptr_t)controls)==want);assert(sends==!want&&allocations==!want);if(want)for(unsigned i=0;i<16;i++)assert(message[i]==0xa5);}
int main(void){unsigned cases=0;configuration[34]=3;
for(unsigned field=0;field<4;field++){for(unsigned value=0;value<65536;value++){controls[0]=6;controls[1]=100;controls[2]=0;controls[3]=100;controls[4]=0xa55a;controls[5]=0x5aa5;controls[field]=value;check();cases++;}}
for(unsigned maximum=6;maximum<=3200;maximum+=17){for(unsigned latency=0;latency<500;latency+=13){unsigned edge=(latency+1)*maximum/4;for(unsigned delta=0;delta<2;delta++){controls[0]=6;controls[1]=maximum;controls[2]=latency;controls[3]=(uint16_t)(edge+delta);check();cases++;}}}
printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['30a6b4..30a70a','30c998..30c9fe'],'scope':'Actual connected selected C validator/modify wrapper; normalized fixed RAM; controlled slot/allocator/send; exhaustive each16-bit field and product boundary pairs; host product stand-ins bounded by validated operands, named DSP operations retained in target C; no native ISA arithmetic/runtime equality inferred','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-parameters-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connected connection parameter cases')
