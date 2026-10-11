from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native330f08..'):s.index('/* Native30bc3c tail')]
h=r'''
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
'''+body+r'''
int main(void){unsigned cases=0;_Alignas(4) uint8_t memory[64],expected[64];uint32_t statuses[]={0,2,255,256,0xdeadbeef},ids[]={0,1,255,256,65535,0xdeadbeef};
for(unsigned pattern=0;pattern<256;pattern++){for(unsigned in=0;in<8;in++){for(unsigned out=0;out<24;out++){for(unsigned st=0;st<5;st++){for(unsigned id=0;id<6;id++){
 for(unsigned i=0;i<64;i++)memory[i]=expected[i]=(uint8_t)(pattern+i*17);unsigned src=in*4;
 expected[out+1]=ids[id];expected[out]=statuses[st];expected[out+2]=ids[id]>>8;
 for(unsigned w=0;w<3;w++){unsigned s=src+4*w,d=out+3+4*w;expected[d]=expected[s];expected[d+1]=expected[s+1];expected[d+2]=expected[s+2];expected[d+3]=expected[s+3];}
 assert(opencfw_em9305_ll_test_response_330f08((uintptr_t)(memory+out),statuses[st],ids[id],(uintptr_t)(memory+src))==(uint32_t)(uintptr_t)(memory+out));assert(memcmp(memory,expected,64)==0);cases++;
}}}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-response-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual selected C body; controlled aligned source and overlapping destination buffers, full output byte comparison. Ordered native mixed-width reads retained; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
