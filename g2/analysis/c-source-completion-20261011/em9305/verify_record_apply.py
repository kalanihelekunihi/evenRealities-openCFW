from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native309cfc..309e60'):s.index('/* Native316ad4..316b5c')]
for addr,name in [('805cac','config_pointer'),('805a86','mode_byte'),('805aa4','fourth_word'),('805aa0','third_word'),('805b18','handler_byte')]:
 for typ in ['uint8_t','uint32_t']:b=b.replace(f'*(volatile {typ} *)(uintptr_t)0x{addr}u',name)
b=b.replace('__asm__ volatile("mpyuw %0,%1,1000":"=r"(scaled):"r"(duration));','scaled=duration*1000u;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t input[40],config[80],record[512],assoc[2824],message[8],result[8];
static uintptr_t config_pointer;static uint8_t mode_byte,handler_byte;static uint32_t fourth_word,third_word;
static unsigned fail,releases,sends,streams,associated;
uint32_t opencfw_em9305_ll_stream_free_count_31b248(void){return fail==1?0:3;}
uintptr_t opencfw_em9305_ll_record_find_31aa98(uint32_t id){assert(id==7);return fail==2?1:0;}
uint32_t opencfw_em9305_radio_association_exists_317280(uint32_t id){assert(id==8);return fail==3;}
uintptr_t opencfw_em9305_ll_record_allocate_316a8c(uint32_t id){assert(id==7);return fail==4?0:(uintptr_t)record;}
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==8&&input[12]==2);return associated?(uintptr_t)assoc:0;}
void opencfw_em9305_radio_record_configure_32c3bc(uintptr_t r,uintptr_t i){assert(r==(uintptr_t)record&&i==(uintptr_t)input);*(uint32_t *)(record+44)=fail==5?1001:1000;}
void opencfw_em9305_radio_record_release_31ac84(uintptr_t r){assert(r==(uintptr_t)record);releases++;}
uint32_t opencfw_em9305_radio_record_finish_32c2b0(uintptr_t r){assert(r==(uintptr_t)record);return 0;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t i,uint32_t s){assert(i==0&&s==0);return fail==6?9:8;}
uintptr_t opencfw_em9305_radio_stream_allocate_316ad4(uintptr_t r){assert(r==(uintptr_t)record);streams++;return fail==7?0:1;}
uintptr_t opencfw_em9305_radio_stream_setup_327718(uintptr_t s,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){assert(s==1&&a==0&&b==0&&c==3&&d==4&&e==0);return (uintptr_t)result;}
void opencfw_em9305_radio_association_callback_3291e4(uint32_t id){(void)id;}void opencfw_em9305_radio_association_callback_3291d0(uint32_t id){(void)id;}void opencfw_em9305_radio_association_callback_3290c4(uint32_t id){(void)id;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4);return fail==8?0:(uintptr_t)message;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==9&&m==(uintptr_t)message&&*(uint16_t *)message==7&&*(uint16_t *)(message+2)==272);sends++;return 0;}
'''+b+r'''
int main(void){unsigned n=0;config_pointer=(uintptr_t)config;third_word=3;fourth_word=4;handler_byte=9;
for(fail=0;fail<10;fail++)for(associated=0;associated<2;associated++)for(unsigned mode=0;mode<2;mode++){
 memset(input,0,40);memset(record,0,512);memset(assoc,0,2824);memset(result,0,8);config[58]=fail==9?0:3;config[48]=2;input[0]=7;input[1]=8;input[2]=1;input[12]=5;*(uint16_t *)(input+10)=1;assoc[2518]=77;mode_byte=mode?64:0;streams=releases=sends=0;
 unsigned expected=(fail==1||fail==4||fail==7||fail==9)?13:fail==2?12:fail==3?66:fail==5?17:fail==6?18:0;
 assert(opencfw_em9305_radio_record_apply_309cfc((uintptr_t)input)==expected);assert(releases==(fail==5||fail==6||fail==7));assert(sends==(fail==0));if(expected==0&&associated){assert(*(uint32_t *)(record+180)==(uint32_t)(uintptr_t)assoc);assert(*(uint32_t *)(assoc+2804)==(uint32_t)(uintptr_t)&opencfw_em9305_radio_association_callback_3291e4);assert(record[410]==77&&result[0]==0);}n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-apply-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C ten failure/success cuts, association/mode branches, cleanup/timing child return/message and callback writes. Real children/RAM/MPYUW normalized; no nativeISA/hardware proof.'},indent=2)+'\n');print('PASS',n)
