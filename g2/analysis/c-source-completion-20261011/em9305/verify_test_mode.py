from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native31ab50..'):s.index('/* Native30c724 tail')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','((uintptr_t)config_data)').replace('*(volatile uint32_t *)(uintptr_t)0x805c64u','((uintptr_t)channels)').replace('*(volatile uint8_t *)(uintptr_t)0x805adcu','product')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t link[656],stream[256],channels[420],config_data[64],expected_link[656],expected_stream[256];static unsigned link_ok,stream_ok,link_calls,stream_calls;static uint8_t product;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==0x1234);link_calls++;return link_ok?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==0x1234);stream_calls++;return stream_ok?(uintptr_t)stream:0;}
'''+body+r'''
int main(void){unsigned count=0;unsigned flags[]={0,1,2,255};uint32_t values[]={0,1,2,3,256,0xdeadbeef};
for(unsigned key=0;key<256;key++){for(unsigned hit=0;hit<4;hit++){memset(channels,0,420);config_data[52]=3;for(unsigned row=0;row<3;row++){channels[row*140]=1;channels[row*140+6]=(uint8_t)(key+1);}if(hit<3)channels[hit*140+6]=key;assert(opencfw_em9305_ll_test_channel_find_31ab50(key)==(hit<3?(uintptr_t)(channels+hit*140):0));assert(opencfw_em9305_ll_test_channel_find_31ab50(key+256)==0);count+=2;}}
config_data[52]=0;assert(opencfw_em9305_ll_test_channel_find_31ab50(0)==0);count++;
for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned first=0;first<4;first++){for(unsigned second=0;second<4;second++){for(unsigned state=0;state<4;state++){for(unsigned arg=0;arg<6;arg++){for(unsigned gate=0;gate<4;gate++){
 memset(link,0xa5,656);memset(stream,0xa5,256);memset(channels,0,420);config_data[52]=3;channels[280]=1;channels[286]=73;*(uint32_t*)(channels+328)=0x12345678;link[11]=73;link[10]=flags[state];link[512]=flags[first];link[513]=flags[second];stream[108]=flags[first];stream[109]=flags[second];product=flags[gate];memcpy(expected_link,link,656);memcpy(expected_stream,stream,256);link_calls=stream_calls=0;
 unsigned expected;if(link_ok){expected=(!flags[first]&&!flags[state])||(!flags[second]&&flags[state]==1)?17:values[arg]>=3?18:0;if(expected==0){*(uint32_t*)(expected_link+564)=0;expected_link[556]=values[arg];expected_link[548]=1;*(uint32_t*)(expected_link+552)=0x12345678;}}
 else if(stream_ok){expected=flags[first]||flags[second]?12:!product?7:0;if(expected==0){expected_stream[116]=values[arg];*(uint32_t*)(expected_stream+112)=0;*(uint16_t*)(expected_stream+108)=1;}}
 else expected=2;
 assert(opencfw_em9305_ll_test_30c2dc(0x1234,values[arg])==expected&&link_calls==1&&stream_calls==!link_ok);assert(memcmp(link,expected_link,656)==0&&memcmp(stream,expected_stream,256)==0);count++;
}}}}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-mode-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual three C bodies with normalized runtime pointer/feature cells and controlled selected link/stream lookup. Channel stride and full-word id domain; link state/value gates, stream busy/product gates, complete output records. Native success requires matched channel; no invented null guard. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
