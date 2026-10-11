from pathlib import Path
import subprocess,tempfile,json,re
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('static uint32_t opencfw_em9305_native_div_309f5e'):s.index('/* Native327a4c..327a54')]
b=re.sub(r'__asm__ volatile\("div %0,%1,%2".*?;','r=(uint32_t)((int32_t)a/(int32_t)b);',b)
b=re.sub(r'__asm__ volatile\("divu %0,%1,%2".*?;','r=a/b;',b)
b=re.sub(r'__asm__ volatile\("mpyw %0,%1,%2".*?;','r=a*b;',b)
b=b.replace('__asm__ volatile("mpyuw %0,%1,1250":"=r"(scaled):"r"(interval));','scaled=interval*1250;').replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(factor),"r"(groups));','product=factor*groups;')
for addr,name in [('805aa0','lower_global'),('805aa4','upper_global'),('805b18','handler_global')]:
 for typ in ['uint8_t','uint32_t']:b=b.replace(f'*(volatile {typ} *)(uintptr_t)0x{addr}u',name)
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t input[40],record[512],assoc[2824],message[8];static unsigned fail,associated,streams,releases,sends,randoms,seeds,finished;static uint32_t lower_global=17,upper_global=19,handler_global=9;
static const uint8_t opencfw_em9305_radio_phy_values_334488[7]={2,1,3,1,1,1,4};
uint32_t opencfw_em9305_ll_stream_free_count_31b248(void){return fail==1?0:3;}
uintptr_t opencfw_em9305_ll_record_find_31aa98(uint32_t id){assert(id==7);return fail==2?1:0;}
uint32_t opencfw_em9305_radio_association_exists_317280(uint32_t id){assert(id==8);return fail==3;}
uintptr_t opencfw_em9305_ll_record_allocate_316a8c(uint32_t id){assert(id==7);return fail==4?0:(uintptr_t)record;}
uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t x){assert(x==1);return 1;}
uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t r,uint32_t n){assert(r==(uintptr_t)(record+(n==8?485:493)));randoms++;return 0;}
void opencfw_em9305_radio_encrypt_seed_317334(uintptr_t k,uintptr_t i,uintptr_t o){assert(k==(uintptr_t)(record+493)&&i==(uintptr_t)(input+8)&&o==(uintptr_t)(record+92));seeds++;}
uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return a*b;}
uint32_t opencfw_em9305_radio_phy_duration_31737c(uint32_t p,uint32_t n,uint32_t e){assert(p==1&&n==20&&e==(input[38]!=0));return 100;}
uint32_t opencfw_em9305_radio_record_finish_32c2b0(uintptr_t r){assert(r==(uintptr_t)record);finished++;return 0;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t l,uint32_t n){assert(l==60&&n==20);return fail==5?9:3;}
uintptr_t opencfw_em9305_radio_stream_allocate_316ad4(uintptr_t r){assert(r==(uintptr_t)record);streams++;return fail==6?0:1;}
uintptr_t opencfw_em9305_radio_stream_setup_327718(uintptr_t r,uint32_t a,uint32_t b,uint32_t lo,uint32_t hi,uint32_t p){assert(r==1&&a==0&&b==0&&lo==17&&hi==19&&p==1);return 0;}
void opencfw_em9305_radio_record_release_31ac84(uintptr_t r){assert(r==(uintptr_t)record);releases++;}
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==8);return associated?(uintptr_t)assoc:0;}
void opencfw_em9305_radio_association_callback_3291e4(uint32_t id){(void)id;}void opencfw_em9305_radio_association_callback_3291d0(uint32_t id){(void)id;}void opencfw_em9305_radio_association_callback_3290c4(uint32_t id){(void)id;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4);return fail==7?0:(uintptr_t)message;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==9&&m==(uintptr_t)message&&*(uint16_t *)message==7&&*(uint16_t *)(message+2)==272);sends++;return 0;}
'''+b+r'''
int main(void){unsigned cases=0;for(fail=0;fail<8;fail++)for(associated=0;associated<2;associated++)for(unsigned secure=0;secure<2;secure++)for(unsigned option=0;option<3;option++)for(unsigned single=0;single<2;single++)for(unsigned aligned=0;aligned<2;aligned++){memset(input,0,40);memset(record,0,512);memset(assoc,0,2824);input[0]=7;input[1]=8;input[2]=2;*(uint32_t *)(input+4)=2000;*(uint16_t *)(input+24)=4;input[26]=8;*(uint16_t *)(input+28)=60;*(uint16_t *)(input+30)=20;input[32]=1;input[33]=single;input[34]=aligned;input[35]=2;input[36]=2;input[37]=option;input[38]=secure;streams=releases=sends=randoms=seeds=finished=0;
uint32_t expected=fail==1||fail==4||fail==6?13:fail==2?12:fail==3?18:fail==5?2:0;assert(opencfw_em9305_radio_record_extended_apply_309e60((uintptr_t)input)==expected);assert(releases==(fail==6));if(fail==0||fail>=5){assert(finished==1&&randoms==2*secure&&seeds==secure);uint32_t count=option?8:4;assert(record[25]==count&&record[194]==(uint8_t)(option?2*option:0)&&record[28]==(uint8_t)(option?4*option:255));uint32_t a=single?250:250*count,bv=single?500:250;uint32_t span=a+100+bv*(count-1);assert(*(uint32_t *)(record+40)==span);uint32_t steps=2*option;uint32_t total=aligned?steps*5000+span+7000:(steps+1)*5000+span-2000;assert(*(uint32_t *)(record+44)==total);if(expected==0&&associated)assert(*(uint32_t *)(record+180)==(uint32_t)(uintptr_t)assoc);}assert(sends==(fail==0));cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('extended-apply-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C eight failure cuts, association/secure/options/single/aligned branches, native timing-failure originalcount return and no release. Arithmetic ISA operations normalized only for tested small positive operands; globals/children normalized. No native ISA/crypto/layout/hardware qualification.'},indent=2)+'\n');print('PASS',n)
