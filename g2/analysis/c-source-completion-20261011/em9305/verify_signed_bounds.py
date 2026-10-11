from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31026c..'):s.index('/* Native309910..')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x8012b9u','lower_byte').replace('*(volatile uint8_t *)(uintptr_t)0x8012b8u','upper_byte')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t upper_byte,lower_byte;
"""+body+r"""
int main(void){unsigned cases=0;int32_t inputs[]={-2147483647-1,-129,-128,-1,0,1,127,128,2147483647};
for(int a=-128;a<128;a++){for(int b=-128;b<128;b++){
 upper_byte=(uint8_t)a;lower_byte=(uint8_t)b;uint8_t x=0,y=0;
 assert(opencfw_em9305_ll_signed_bounds_31026c((uintptr_t)&x,(uintptr_t)&y)==(uint32_t)(uintptr_t)&x);assert(x==(uint8_t)b&&y==(uint8_t)a);cases++;
 (void)opencfw_em9305_ll_signed_bounds_31026c((uintptr_t)&x,(uintptr_t)&x);assert(x==(uint8_t)a);cases++;
 for(unsigned i=0;i<9;i++){int32_t v=inputs[i];unsigned want=b>=v?1:a<=v?2:0;assert(opencfw_em9305_ll_signed_classify_31b374((uint32_t)v)==want);cases++;}
}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['31026c..310280','31b374..31b39a'],'scope':'Actual connected selected C with product bound RAM bytes normalized; signed edge and output alias cases; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('signed-bounds-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled signed bound cases')
