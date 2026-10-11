from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native30c3a4..30c40c'):s.index('static uint32_t opencfw_em9305_native_div_309f5e')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
'''+b+r'''
static uint32_t reference(uint32_t n,uint32_t d){if(n<d)return 0;uint64_t shifted=d;uint32_t mask=1;do{shifted<<=1;mask<<=1;}while(shifted<=n);if(!mask)return 0;uint64_t rem=n;uint32_t q=0;do{shifted>>=1;uint32_t next=mask>>1;if(rem>=shifted){rem-=shifted;q+=next;}uint32_t old=mask;mask=next;if(old<=3)break;}while(1);return q;}
int main(void){unsigned cases=0;for(unsigned n=0;n<4096;n++)for(unsigned d=1;d<256;d++){assert(opencfw_em9305_radio_unsigned_divide_30c3a4(n,d)==n/d);assert(opencfw_em9305_radio_record_timing_30c40c(n,d)==(n+d-1)/d);cases++;}uint32_t bounds[]={0,1,2,3,255,256,0x7fffffff,0x80000000,0xfffffffe,0xffffffff};for(unsigned i=0;i<10;i++)for(unsigned j=1;j<10;j++){uint32_t n=bounds[i],d=bounds[j];assert(opencfw_em9305_radio_unsigned_divide_30c3a4(n,d)==reference(n,d));assert(opencfw_em9305_radio_record_timing_30c40c(n,d)==reference(n+d-1,d));cases++;}assert(opencfw_em9305_radio_unsigned_divide_30c3a4(0xffffffff,1)==0);printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('native-timing-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C division/timing ordinary domain and wrapping boundaries against arithmetic and instruction-derived two-word model. Zero divisor nontermination inspected statically, not executed; no native instruction/layout/hardware proof.'},indent=2)+'\n');print('PASS',n)
