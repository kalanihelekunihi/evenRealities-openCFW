from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31bad0..'):s.index('/* Native31c490..')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cb0u','active_pointer').replace('(uintptr_t)0x8028d0u','((uintptr_t)ring_data)').replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','handler_value')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t ring_data[144],active_data[8];static uintptr_t active_pointer;static uint8_t handler_value;static unsigned releases,posts,index_value,mutate;
uint32_t opencfw_em9305_wsf_event_release(uintptr_t packet){assert(packet==0x12345678);releases++;return 0xcafe;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t events){assert(handler==handler_value&&events==128&&*(uint32_t*)ring_data==(index_value+1)%6);posts++;if(mutate)*(uint32_t*)ring_data=99;return 0xbeef;}
'''+body+r'''
int main(void){unsigned cases=0;const uint32_t ids[]={0,1,0xffff,0x10000,0x1234,0xffffffff};for(index_value=0;index_value<6;index_value++){for(unsigned i=0;i<6;i++){for(unsigned length=0;length<256;length++){for(unsigned active=0;active<2;active++){for(mutate=0;mutate<2;mutate++){
 uint32_t id=ids[i];uint8_t expected[144];memset(ring_data,0xa5,144);*(uint32_t*)ring_data=index_value;memcpy(expected,ring_data,144);*(uint16_t*)(active_data+2)=(uint16_t)id;active_pointer=active?(uintptr_t)active_data:0;handler_value=length;releases=posts=0;unsigned released=active&&id<=0xffff;
 if(!released){unsigned row=index_value*20;*(uint32_t*)(expected+row+12)=0xaabbccdd;*(uint16_t*)(expected+row+24)=length;*(uint32_t*)(expected+row+20)=0x12345678;*(uint32_t*)(expected+row+16)=0x55667788;*(uint16_t*)(expected+row+8)=id;*(uint32_t*)expected=mutate?99:(index_value+1)%6;}
 assert(opencfw_em9305_ll_test_complete_31bad0(id,0xaabbccdd,0x55667788,0x12345678,length)==(released?0xcafe:0xbeef)&&releases==released&&posts==!released);assert(memcmp(expected,ring_data,144)==0);cases++;
}}}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-completion-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C completion callback with normalized product pointers. Six configured ring indices, ids including fullword nonmatches, all handler/length byte values, release versus ring/post branch, exact overlapping20Bstride/+24field stores, child mutates ringindex after pre-call write, and native return forwarding. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
