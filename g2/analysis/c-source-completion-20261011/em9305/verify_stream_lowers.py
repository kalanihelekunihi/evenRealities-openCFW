from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native30e4dc..');body=s[a:s.index('extern uint32_t opencfw_em9305_ll_connection_begin_',a)]
for old,new in [('(uintptr_t)0x805a81u','(uintptr_t)&cap'),('(uintptr_t)0x805a94u','(uintptr_t)&test_flags'),('(uintptr_t)0x802a5eu','(uintptr_t)&latch')]:body=body.replace(old,new)
body=body.replace('static const uint32_t opencfw_em9305_stream_record_addresses','static const uintptr_t opencfw_em9305_stream_record_addresses').replace('{0x802d20u,0x802fe0u,0x8032a0u}','{(uintptr_t)records[0],(uintptr_t)records[1],(uintptr_t)records[2]}')
body=body.replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(scaled):"r"(10000u),"r"(timeout));','scaled=10000u*timeout;phase=2;')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static uint8_t cap,test_flags,latch;static _Alignas(4) uint8_t records[3][704];
static uint32_t phase,limit,latency,interval;
uint32_t opencfw_em9305_native_config_product(uint32_t a,uint32_t b){assert(a==latency+1&&b==interval);phase=1;return 0x11223344;}
uint32_t opencfw_em9305_native_clock_product(uint32_t a,uint32_t b){assert(phase==2&&a==0x11223344&&b==2500);phase=3;return limit;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(n==12);return memcpy(d,s,n);}
'''+body+r'''
int main(void){unsigned cases=0;uint8_t h[12]={0};
for(unsigned f=0;f<2;f++)for(unsigned c=0;c<2;c++)for(unsigned a=0;a<6;a++)for(unsigned b=0;b<6;b++)for(unsigned k=0;k<6;k++){test_flags=f?64:0;cap=c;h[0]=k;h[1]=a;h[2]=b;unsigned max=f?3:1;unsigned ok=a<=max&&b<=max&&k<5&&(a==0||a==2||((a==1||a==3)&&c));assert(opencfw_em9305_ll_stream_header_valid_332f04((uintptr_t)h)==ok);cases++;}
uint16_t x[6]={6,6,0,10,0,0};uint16_t variants[][4]={{5,6,0,10},{6,5,0,10},{6,3201,0,10},{3201,3201,0,10},{6,6,500,10},{6,6,0,9},{6,6,0,3201},{6,6,499,3200},{3200,3200,0,10}};
for(unsigned i=0;i<9;i++){memcpy(x,variants[i],8);latency=x[2];interval=x[1];limit=0;phase=0;unsigned expected=i<7?18:0;assert(opencfw_em9305_ll_stream_control_valid_332f00((uintptr_t)x)==expected);cases++;}
x[0]=x[1]=6;x[2]=0;x[3]=10;latency=0;interval=6;
for(unsigned i=0;i<3;i++){limit=99999+i;phase=0;assert(opencfw_em9305_ll_stream_control_valid_332f00((uintptr_t)x)==(i?18:0));assert(phase==3);cases++;}
for(unsigned bit=0;bit<8;bit++){latch=255;assert(opencfw_em9305_ll_stream_disable_307970(bit)==(255u&~(1u<<bit)));assert(latch==(255u&~(1u<<bit)));latch=0;assert(opencfw_em9305_ll_stream_enable_307a48(bit)==(1u<<bit));assert(latch==(1u<<bit));cases+=2;}
uint16_t pair[2]={0x1234,0x9876};uint8_t control[12];for(unsigned j=0;j<12;j++)control[j]=j*17;
for(unsigned i=0;i<3;i++)for(unsigned use=0;use<2;use++){memset(records,0xa5,sizeof records);assert(opencfw_em9305_ll_stream_configure_307a28(i,use?(uintptr_t)pair:0,(uintptr_t)control)==(uint32_t)(uintptr_t)(records[i]+24));assert(memcmp(records[i]+24,control,12)==0);if(use){assert(*(uint16_t*)(records[i]+20)==pair[0]&&*(uint16_t*)(records[i]+22)==pair[1]);}else{for(unsigned j=20;j<24;j++)assert(records[i][j]==0xa5);}for(unsigned j=0;j<20;j++)assert(records[i][j]==0xa5);for(unsigned j=36;j<704;j++)assert(records[i][j]==0xa5);cases++;}
printf("%u\n",cases);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'scope':'Actual selected lower C bodies with fixed RAM normalized; product children controlled and named MPYUW normalized. Contract checks from native reading, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_ranges':['30e4dc..30e510','332f04..332f3c','30a6b4..30a70c','307970..307980','307a28..307a58']}
Path(__file__).with_name('stream-lowers-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled stream lower cases')
