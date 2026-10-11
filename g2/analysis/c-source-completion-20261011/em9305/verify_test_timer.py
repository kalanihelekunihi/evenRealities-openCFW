from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31c490..'):s.index('/* Native331a8c..')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','config_pointer').replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)state_data)').replace('*(volatile uint32_t *)(uintptr_t)0x802800u','((uintptr_t)&host_callback)')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t config[64],fresh[64],link_data[656],stream_data[256],state_data[320],channel[140];static uintptr_t config_pointer;static unsigned link_ok,stream_ok,alloc_ok,match,mutate,allocations,callbacks,size_value;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==0x1122);if(mutate)config_pointer=(uintptr_t)fresh;return link_ok?(uintptr_t)link_data:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==0x1122);return stream_ok?(uintptr_t)stream_data:0;}
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){assert(id==9);return (uintptr_t)channel;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes){assert(bytes==(uint16_t)((mutate?size_value:1234)+8));allocations++;return alloc_ok?0x1000:0;}
static uint32_t host_callback(uint32_t id,uintptr_t payload,uint32_t length,uint32_t timer){assert(id==0x1122&&payload==0x100c&&length==(link_ok?1234:4321)&&timer==(link_ok?0xaabbccdd:match?0x12345677:0x55667788));callbacks++;return 0xcafe;}
'''+body+r'''
int main(void){unsigned count=0;unsigned sizes[]={0,1234,65527,65535};for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned marker=0;marker<256;marker++){for(alloc_ok=0;alloc_ok<2;alloc_ok++){for(match=0;match<2;match++){for(mutate=0;mutate<2;mutate++){for(unsigned si=0;si<4;si++){
 memset(link_data,0,656);memset(stream_data,0,256);memset(config,0,64);memset(fresh,0,64);size_value=sizes[si];*(uint16_t*)(config+44)=1234;*(uint16_t*)(fresh+44)=size_value;config_pointer=(uintptr_t)config;link_data[11]=9;link_data[528]=marker;stream_data[36]=marker;*(uint32_t*)(channel+36)=0xaabbccdd;*(uint16_t*)(state_data+6)=4321;*(uint32_t*)(state_data+304)=match?0xffffffff:0x55667788;*(uint32_t*)(state_data+16)=0x12345678;allocations=callbacks=0;unsigned found=link_ok||stream_ok,takes=found&&marker==1;
 unsigned expected=!found?0:marker!=1?marker:alloc_ok?0xcafe:0;assert(opencfw_em9305_ll_test_timer_31c490(0x1122,0xffffffff)==expected&&allocations==takes&&callbacks==(takes&&alloc_ok));count++;
}}}}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-timer-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C timer helper normalized RAM/state/callback pointers. Allslotmarkerbytes, lookup alternatives, allocator miss/success, context equal/unequal, freshconfig mutation bylookup,16-bit allocation size wrap and exact callback fields/return. Controlled children, not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
