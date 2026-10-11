from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native310230..'):s.index('/* Native31026c..')]
body=body.replace('*(volatile int8_t *)(uintptr_t)0x8012b8u','upper_byte').replace('*(volatile int8_t *)(uintptr_t)0x8012b9u','lower_byte')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static int8_t upper_byte,lower_byte;static int32_t query;static unsigned calls;
uint32_t opencfw_em9305_radio_status_311a00(uint32_t x){assert(x==1);calls++;return (uint32_t)query;}
"""+body+r"""
int main(void){unsigned cases=0;int32_t inputs[]={-2147483647-1,-129,-128,-1,0,1,127,128,2147483647};int32_t queries[]={-128,-1,0,127,2147483647};
for(int a=-128;a<128;a++){for(int b=-128;b<128;b++){for(unsigned q=0;q<5;q++){for(unsigned i=0;i<9;i++){
 upper_byte=a;lower_byte=b;query=queries[q];calls=0;
 int32_t top=a<query?a:query,v=inputs[i],want=top<v?top:b>v?b:v;
 assert(opencfw_em9305_ll_signed_clamp_310230((uint32_t)v)==(uint32_t)want&&calls==1);cases++;
}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'310230..31025e','scope':'Actual selected C with signed product RAM bytes normalized and controlled fresh radio query; native-reading contract, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('signed-clamp-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled signed clamp cases')
