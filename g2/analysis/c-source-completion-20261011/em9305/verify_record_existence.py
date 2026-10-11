from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31aa64..31aa98'):s.index('/* Native30b2d8..30b3f8')].replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','config_pointer').replace('*(volatile uint32_t *)(uintptr_t)0x805c38u','rows_pointer')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t config[64],rows[2824*256];static uintptr_t config_pointer,rows_pointer;
'''+b+r'''
int main(void){unsigned n=0;config_pointer=(uintptr_t)config;rows_pointer=(uintptr_t)rows;
for(unsigned count=0;count<256;count++)for(unsigned id=0;id<258;id++)for(unsigned active=0;active<2;active++){
 memset(rows,0,sizeof rows);config[12]=count;uintptr_t expected=0;
 for(unsigned i=0;i<count;i++){rows[i*2824+1]=(uint8_t)i;rows[i*2824]=active;if(active&&id==i&&expected==0)expected=(uintptr_t)(rows+i*2824);}
 assert(opencfw_em9305_radio_record_find_31aa64(id)==expected);assert(opencfw_em9305_radio_record_exists_3072d0(id)==(expected!=0));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-existence-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all count bytes, ids0..257 and active/inactive rows, fullwidth id comparison/2824B stride/Boolean wrapper. RAM pointers normalized; no native ISA or hardware execution.'},indent=2)+'\n');print('PASS',n)
