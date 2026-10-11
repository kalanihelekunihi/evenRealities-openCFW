from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native30e0e4 tail'):s.index('/* Native30b230..30b2d8')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t row[512];static unsigned found,calls;
uintptr_t opencfw_em9305_ll_record_find_31aa98(uint32_t id){assert(id==0x12345678);calls++;return found?(uintptr_t)row:0;}
'''+b+r'''
int main(void){unsigned n=0;for(found=0;found<2;found++)for(unsigned a=0;a<3;a++)for(unsigned c=0;c<3;c++)for(unsigned f=0;f<256;f++)for(unsigned o=0;o<256;o++){
 row[1]=a;row[3]=c;row[273]=f;row[290]=0xa5;calls=0;unsigned valid=found&&a==1&&c==1;assert(opencfw_em9305_command_30e0e4(0x12345678,0x12340000|o)==(!found?66:valid?0:12));assert(calls==1&&row[273]==(valid?(f|2):f)&&row[290]==(valid?o:0xa5));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-option-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C record lookup outcomes/state guards/all flag and option bytes/fullword truncation; genuine lookup normalized. No native ISA/hardware execution.'},indent=2)+'\n');print('PASS',n)
