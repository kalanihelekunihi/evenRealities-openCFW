from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30c918..30c928'):s.index('/* Native325268..325284')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint32_t value,calls;
uint32_t opencfw_em9305_radio_identity_status_30396c(void){calls++;return value;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned v=0;v<256;v++)for(unsigned high=0;high<2;high++){value=v|(high?0xffffff00:0);calls=0;uint8_t out[3]={17,88,99};assert(opencfw_em9305_command_30c918((uintptr_t)(out+1))==0&&calls==1&&out[0]==17&&out[1]==v&&out[2]==99);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('status-output-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C original output pointer, lowbyte projection/status0, single genuine getter. Normalized child; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
