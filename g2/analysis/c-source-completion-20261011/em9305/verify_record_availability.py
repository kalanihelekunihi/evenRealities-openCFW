from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native307410..307434'):s.index('/* Native317280..3172c8')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t row[400];static unsigned found,calls;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==0x12345678);calls++;return found?(uintptr_t)row:0;}
'''+b+r'''
int main(void){unsigned n=0;for(found=0;found<2;found++)for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){row[369]=a;row[368]=c;calls=0;assert(opencfw_em9305_radio_record_available_307410(0x12345678)==(found&&a!=0&&c==1));assert(calls==1);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-availability-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all availability/state byte pairs and lookup outcomes. Genuine lookup normalized; native ISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
