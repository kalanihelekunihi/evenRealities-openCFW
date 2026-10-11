from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native32e378..'):s.index('/* Native30e0e0 tail')]
h=r"""
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
"""+body+r"""
static unsigned expected(uint16_t *v){return v[0]>=1&&v[0]<=500&&v[1]>=1&&v[1]<=500&&v[0]<=v[1]&&v[2]<=499&&v[3]<v[1]&&v[4]>=10&&v[4]<=3200?0:18;}
int main(void){unsigned cases=0;uint16_t defaults[][5]={{1,1,0,0,10},{500,500,499,499,3200},{250,500,100,249,1000}};
for(unsigned d=0;d<3;d++)for(unsigned field=0;field<5;field++)for(unsigned value=0;value<65536;value++){uint16_t v[5];for(unsigned i=0;i<5;i++)v[i]=defaults[d][i];v[field]=value;assert(opencfw_em9305_ll_controls_validate_32e378((uintptr_t)v)==expected(v));cases++;}
for(unsigned first=0;first<502;first++)for(unsigned second=0;second<502;second++){uint16_t v[5]={first,second,499,second?second-1:0,3200};assert(opencfw_em9305_ll_controls_validate_32e378((uintptr_t)v)==expected(v));cases++;}
printf("%u\n",cases);}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('controls-validator-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual selected C; exhaustive halfword sweeps and paired first/second order domain against native-derived mathematical intervals; not native runtime equality.','native_range':'32e378..32e3b8','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
