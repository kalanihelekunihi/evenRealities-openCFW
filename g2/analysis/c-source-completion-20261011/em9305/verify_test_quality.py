from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native306f0c..'):s.index('/* Native330f08..')]
body=body.replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)state_data)')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t link_data[400],stream_data[128],state_data[8],output;static unsigned link_ok,stream_ok,link_calls,stream_calls,fallback_calls,write_fallback;static uint32_t fallback_status;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==0x1234);link_calls++;return link_ok?(uintptr_t)link_data:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==0x1234);stream_calls++;return stream_ok?(uintptr_t)stream_data:0;}
uint32_t opencfw_em9305_ll_connection_quality_30be68(uint32_t id,uintptr_t p){assert(id==0x1234&&p==(uintptr_t)&output);fallback_calls++;if(write_fallback)*(uint8_t*)p=0x5a;return fallback_status;}
"""+body+r"""
int main(void){unsigned cases=0;uint32_t statuses[]={0,2,12,0xdeadbeef};
for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned value=0;value<256;value++){for(unsigned marker=0;marker<256;marker++){for(unsigned st=0;st<4;st++){for(write_fallback=0;write_fallback<2;write_fallback++){
 output=0xa5;link_calls=stream_calls=fallback_calls=0;link_data[380]=value;stream_data[100]=value;state_data[3]=marker;fallback_status=statuses[st];
 unsigned missing=!link_ok&&!stream_ok;unsigned expected=missing?fallback_status:0;unsigned expected_output=link_ok?value:stream_ok?(marker?127:value):write_fallback?0x5a:0xa5;
 assert(opencfw_em9305_ll_test_30bd18(0x1234,(uintptr_t)&output)==expected&&output==expected_output&&link_calls==1&&stream_calls==!link_ok&&fallback_calls==missing);cases++;
}}}}}}printf("%u\n",cases);}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-quality-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual two C bodies with normalized stream state pointer and controlled selected find/slot-quality children. Exhaustive quality and marker bytes, link/stream precedence, fallback statuses and untouched output. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
