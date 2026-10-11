from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native3087a0..');body=s[a:s.index('extern uint32_t opencfw_em9305_dispatch_32f494',a)]
for old,new in [('(uintptr_t)0x8027ccu','(uintptr_t)&test_count'),('(uintptr_t)0x805aa4u','(uintptr_t)&stored_high'),('(uintptr_t)0x805aa0u','(uintptr_t)&stored_low'),('uintptr_t cursor=0x8027d0u;','uintptr_t cursor=(uintptr_t)callbacks;'),('*(volatile uint32_t *)cursor','*(volatile uintptr_t *)cursor'),('cursor+=4u;','cursor+=sizeof(uintptr_t);')]:body=body.replace(old,new)
h=r'''
#include <stdint.h>
#include <assert.h>
static uint8_t test_count;static uint32_t stored_low,stored_high,expected_low,expected_high,count_result,calls,results[3],change_count;
static uintptr_t callbacks[3];
uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t l,uint32_t h){assert(l==expected_low&&h==expected_high);return count_result;}
static uint32_t callback(uint32_t l,uint32_t h){assert(l==expected_low&&h==expected_high&&stored_low==l&&stored_high==h);assert(calls<3);uint32_t r=results[calls++];if(calls==1&&change_count)test_count=change_count;return r;}
'''+body+r'''
int main(void){uint8_t input[5];for(unsigned i=0;i<3;i++)callbacks[i]=(uintptr_t)&callback;
for(unsigned high=0;high<256;high++)for(unsigned pattern=0;pattern<8;pattern++){for(unsigned i=0;i<4;i++)input[i]=(uint8_t)(pattern*37+i*71);input[4]=high;expected_low=(uint32_t)input[0]+((uint32_t)input[1]<<8)+((uint32_t)input[2]<<16)+((uint32_t)input[3]<<24);expected_high=high;count_result=2;test_count=0;assert(opencfw_em9305_ll_connection_update_30cf40((uintptr_t)input)==(high<32?0:18));}
input[0]=input[1]=input[2]=input[3]=input[4]=255;expected_low=UINT32_MAX;expected_high=255;count_result=2;assert(opencfw_em9305_ll_connection_update_30cf40((uintptr_t)input)==18);
for(unsigned n=0;n<2;n++){count_result=n;assert(opencfw_em9305_ll_connection_update_30cf40((uintptr_t)input)==18);}
expected_low=0x12345678;expected_high=0x19;
for(unsigned scenario=0;scenario<5;scenario++){calls=change_count=0;test_count=3;results[0]=0;results[1]=256;results[2]=0x1a5;uint32_t expected=0xa5,total=3;if(scenario==1){results[0]=0x291;expected=0x91;}if(scenario==2){test_count=1;change_count=3;}if(scenario==3){change_count=1;expected=0;total=1;}if(scenario==4){test_count=0;expected=total=0;}assert(opencfw_em9305_ll_connection_mask_apply_3087a0(expected_low,expected_high)==expected);assert(calls==total&&stored_low==expected_low&&stored_high==expected_high);}return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':2056,'native_ranges':['3087a0..3087ec','30cf40..30cf88'],'scope':'Actual selected C under controlled count child, normalized RAM/callback pointer width; bounded native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
Path(__file__).with_name('connection-mask-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS2056 controlled connection-mask cases')
