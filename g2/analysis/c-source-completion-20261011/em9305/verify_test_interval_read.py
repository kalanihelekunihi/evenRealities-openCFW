from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30bc3c tail'):s.index('/* Native306a9c..')];body=body.replace('(uintptr_t)0x805af4u','(uintptr_t)(memory+2)').replace('(uintptr_t)0x805af5u','(uintptr_t)(memory+3)')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t memory[8];
'''+body+r'''
int main(void){unsigned cases=0;for(unsigned v=0;v<65536;v++){for(unsigned off=0;off<6;off++){uint8_t expected[8];memset(memory,0xa5,8);memory[2]=v;memory[3]=v>>8;memcpy(expected,memory,8);expected[off]=expected[2];expected[off+1]=expected[3];assert(opencfw_em9305_ll_test_30bc3c((uintptr_t)(memory+off))==2&&memcmp(expected,memory,8)==0);cases++;}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-interval-read-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual selected C normalized interval cell; exhaustive halfword and destination aliases including first write changing subsequent source read. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
