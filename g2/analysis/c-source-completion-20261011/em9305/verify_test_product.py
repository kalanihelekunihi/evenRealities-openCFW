from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30bb14..'):s.index('/* Native306f0c..')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','((uintptr_t)current)').replace('*(volatile uint16_t *)(uintptr_t)0x805af4u','interval')
h=r"""
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
static uint8_t config[2][64];static uint8_t *current;static uint16_t interval;
"""+body+r"""
int main(void){unsigned count=0;
for(unsigned pattern=0;pattern<256;pattern++){for(unsigned i=0;i<2;i++){for(unsigned j=0;j<64;j++)config[i][j]=(uint8_t)(pattern+i*33+j*17);current=config[i];assert(opencfw_em9305_ll_test_30bb14()==(uint32_t)(current[38]+256u*current[39]));assert(opencfw_em9305_ll_test_30bb20()==current[35]);current=config[1-i];assert(opencfw_em9305_ll_test_30bdc4()==(uint32_t)(current[44]+256u*current[45]));assert(opencfw_em9305_ll_test_30bdd0()==current[42]);count++;}}
uint32_t upper[]={0,0x10000,0xffff0000};for(unsigned high=0;high<3;high++){for(unsigned low=0;low<65536;low++){uint32_t value=upper[high]|low;interval=0xa55a;unsigned valid=low>=1&&low<=46400;assert(opencfw_em9305_ll_test_30d35c(value)==(valid?0:18)&&interval==(valid?low:0xa55a));count++;}}
printf("%u\n",count);}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-product-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C getters/setter under normalized live pointer and interval cells; pointer changes between getter calls, full halfword interval domain with full-word upper inputs, invalid write preservation. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
