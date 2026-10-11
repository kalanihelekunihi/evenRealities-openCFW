from pathlib import Path
import tempfile,subprocess,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('extern uint32_t opencfw_em9305_ll_controls_validate_32e378'):s.index('/* Native32e378..')];b=b.replace('(0x805ad0u+2u*i)','((uintptr_t)output+2u*i)')
h='''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t output[8];static uint32_t status;static unsigned calls;
uint32_t opencfw_em9305_ll_controls_validate_32e378(uintptr_t p){assert(p);calls++;return status;}
'''+b+'''int main(void){unsigned cases=0;uint32_t st[]={0,2,12,18,256,0xdeadbeef};for(unsigned alias=0;alias<4;alias++)for(unsigned pattern=0;pattern<256;pattern++)for(unsigned t=0;t<6;t++){uint16_t separate[5],expected[8];for(unsigned i=0;i<8;i++)output[i]=pattern*257+i*101;for(unsigned i=0;i<5;i++)separate[i]=pattern*257+i*37;uintptr_t input=alias?(uintptr_t)(output+alias-1):(uintptr_t)separate;memcpy(expected,output,16);if(st[t]==0)memcpy(expected,(void*)input,10);status=st[t];calls=0;assert(opencfw_em9305_ll_controls_apply_30d524(input)==status&&calls==1&&memcmp(expected,output,16)==0);cases++;}printf("%u\\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'t.c'),'-o',str(p/'t')],check=True);n=int(subprocess.check_output([str(p/'t')],text=True))
Path(__file__).with_name('controls-apply-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C normalized shared RAM address; controlled validator statuses and overlapping input/output; all halfwords captured before writes. Not native runtime equality.','body_sha256':hashlib.sha256(b.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
