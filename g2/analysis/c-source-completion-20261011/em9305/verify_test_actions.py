from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('extern uint32_t opencfw_em9305_ll_test_action_31b7e4'):s.index('/* Native31b7e4..')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x805cb0u','context').replace('*(volatile uint32_t *)(record+4u)','((uintptr_t)state_data)')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t link[656],stream[256],expected_link[656],expected_stream[256],state_data[8];static unsigned link_ok,stream_ok,mutate,first_calls,second_calls;static uint32_t context,initial_context=0xdeadbeef;
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==7);return link_ok?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==7);return stream_ok?(uintptr_t)stream:0;}
uint32_t opencfw_em9305_ll_test_action_31b7e4(uintptr_t scratch){uint8_t*r=link_ok?link:stream;unsigned offset=link_ok?528:36,id_offset=link_ok?8:2;assert(*(uint16_t*)scratch==*(uint16_t*)(r+id_offset)&&*(uint32_t*)(scratch+16)==(uint32_t)(uintptr_t)(r+offset)&&context==(uint32_t)(uintptr_t)(r+offset));first_calls++;if(mutate){*(uint16_t*)(r+id_offset)=0x2222;r[link_ok?532:44]=255;context=0xabcd;}return 0xdeadbeef;}
uint32_t opencfw_em9305_ll_test_action_31b8a8(uintptr_t scratch){uint8_t*r=link_ok?link:stream;unsigned offset=link_ok?532:44,id_offset=link_ok?8:2;assert(*(uint16_t*)scratch==*(uint16_t*)(r+id_offset)&&*(uint32_t*)(scratch+16)==(uint32_t)(uintptr_t)(r+offset)&&context==(first_calls?0:initial_context));second_calls++;return 0xdeadbeef;}
'''+body+r'''
int main(void){unsigned cases=0;unsigned flags[]={0,1,254,255},roles[]={0,1,255};
for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned maskcase=0;maskcase<258;maskcase++){for(unsigned f=0;f<4;f++){for(unsigned g=0;g<4;g++){for(unsigned role=0;role<3;role++){for(mutate=0;mutate<2;mutate++){
 uint32_t mask=maskcase<256?maskcase:maskcase==256?0x80000000:0x80000003;memset(link,0xa5,656);memset(stream,0xa5,256);*(uint16_t*)(link+8)=0x6789;*(uint16_t*)(stream+2)=0x4321;link[528]=stream[36]=flags[f];link[532]=stream[44]=flags[g];state_data[3]=roles[role];memcpy(expected_link,link,656);memcpy(expected_stream,stream,256);first_calls=second_calls=0;context=initial_context;
 unsigned status,first=0,second=0;if(link_ok){status=mask==0||(mask&~3u)?18:((mask&1)&&flags[f]==255)||((mask&2)&&flags[g]==255)?12:0;if(!status){first=(mask&1)!=0;second=(mask&2)!=0;}}
 else if(!stream_ok)status=2;
 else {status=((mask&1)&&flags[f]==255)||((mask&2)&&flags[g]==255)||(roles[role]?flags[f]:flags[g])==255?12:0;if(!status){first=roles[role]!=0;second=!first;}}
 uint8_t*er=link_ok?expected_link:expected_stream;unsigned a=link_ok?528:36,b=link_ok?532:44,i=link_ok?8:2;if(first){if(mutate){*(uint16_t*)(er+i)=0x2222;er[b]=255;}er[a]=255;}if(second)er[b]=255;
 assert(opencfw_em9305_ll_test_30cb24(7,mask)==status&&first_calls==first&&second_calls==second&&context==(first?0:initial_context));assert(memcmp(link,expected_link,656)==0&&memcmp(stream,expected_stream,256)==0);cases++;
}}}}}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-actions-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C with controlled selected lookups and genuine action callbacks, normalized runtime context/state cells. All low-byte masks plus full-word invalid masks, sentinel/role gates, callback order and callback-induced id/marker/context mutation. Native scratch fields other than id/+16 are not invented. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
