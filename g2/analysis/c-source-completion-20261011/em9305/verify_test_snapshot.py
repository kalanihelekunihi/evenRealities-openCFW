from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30c724 tail'):s.index('/* Native30c728 tail')].replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)state_data)')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned link_ok,stream_ok,copies,link_calls,stream_calls;static uint8_t link[656],stream[256],state_data[8],output[32];
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==0x1234);link_calls++;return link_ok?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==0x1234);stream_calls++;return stream_ok?(uintptr_t)stream:0;}
void *opencfw_em9305_memcpy(void *dst,const void *src,uint32_t n){assert(dst==output&&n==28&&src==(link_ok?link+584:stream+60));copies++;return memcpy(dst,src,n);}
'''+body+r'''
int main(void){unsigned count=0;for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned marker=0;marker<256;marker++){for(unsigned pattern=0;pattern<256;pattern++){
 for(unsigned i=0;i<656;i++)link[i]=(uint8_t)(pattern+i*13);for(unsigned i=0;i<256;i++)stream[i]=(uint8_t)(pattern+i*17);memset(output,0xa5,32);state_data[3]=marker;copies=link_calls=stream_calls=0;
 unsigned success=link_ok||(stream_ok&&marker==0);assert(opencfw_em9305_ll_test_30c724(0x1234,(uintptr_t)output)==(success?0:2)&&copies==success&&link_calls==1&&stream_calls==!link_ok);if(success)assert(memcmp(output,link_ok?link+584:stream+60,28)==0);else for(unsigned i=0;i<28;i++)assert(output[i]==0xa5);for(unsigned i=28;i<32;i++)assert(output[i]==0xa5);count++;
}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-snapshot-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C with normalized runtime state pointer and controlled selected lookup/copy children. Exhaustive marker/pattern bytes, link precedence, exact source range/28-byte copy and untouched failure/tail bytes. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
