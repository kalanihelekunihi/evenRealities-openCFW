from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native306a9c..'):s.index('/* Native31ab50..')]
h=r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned link_ok,stream_ok,link_calls,stream_calls;static _Alignas(4) uint8_t link[656],stream[256],output[12],expected_link[656],expected_stream[256],expected_output[12];
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){assert(id==0x1234);link_calls++;return link_ok?(uintptr_t)link:0;}
uintptr_t opencfw_em9305_ll_stream_find_31ab14(uint32_t id){assert(id==0x1234);stream_calls++;return stream_ok?(uintptr_t)stream:0;}
'''+body+r'''
static uint32_t load(uint8_t*p){uint32_t x;memcpy(&x,p,4);return x;}static void store(uint8_t*p,uint32_t x){memcpy(p,&x,4);}
int main(void){unsigned count=0;unsigned flags[]={0,1,2,255},offsets[]={0,88,92,96,108};uint32_t values[]={0,1,255,256,0xdeadbeef};
for(link_ok=0;link_ok<2;link_ok++){for(stream_ok=0;stream_ok<2;stream_ok++){for(unsigned f=0;f<4;f++){for(unsigned g=0;g<4;g++){for(unsigned mode=0;mode<4;mode++){for(unsigned alias=0;alias<6;alias++){for(unsigned v=0;v<5;v++){
 for(unsigned i=0;i<656;i++)link[i]=expected_link[i]=(uint8_t)(i*17+v*33);for(unsigned i=0;i<256;i++)stream[i]=expected_stream[i]=(uint8_t)(i*13+v*41);memset(output,0xa5,12);memcpy(expected_output,output,12);
 link[549]=expected_link[549]=flags[f];link[548]=expected_link[548]=flags[g];stream[108]=expected_stream[108]=flags[f];stream[109]=expected_stream[109]=flags[g];
 uint8_t *dst=output,*ed=expected_output;if(alias){if(link_ok){unsigned o=alias==1?548:568+4*(alias-2);dst=link+o;ed=expected_link+o;}else if(stream_ok){dst=stream+offsets[alias-1];ed=expected_stream+offsets[alias-1];}}
 unsigned expected=link_ok?0:stream_ok?(flags[f]^1):2;
 if(mode==2){if(link_ok){store(expected_link+576,0);store(expected_link+572,0);store(expected_link+568,0);expected_link[580]=values[v];expected_link[549]=1;expected_link[581]=values[v]!=0;expected=0;}else if(stream_ok){expected=flags[f]||flags[g]?12:0;if(!expected){expected_stream[116]=values[v];expected_stream[110]=1;expected_stream[108]=1;expected_stream[109]=0;store(expected_stream+88,0);store(expected_stream+92,0);store(expected_stream+96,0);}}}
 else if(link_ok){if(flags[f]){uint32_t a=load(expected_link+568),b=load(expected_link+572),c=load(expected_link+576);store(ed,a);store(ed+4,b);store(ed+8,c);expected=0;if(mode==3){unsigned pending=expected_link[548];expected_link[549]=0;if(pending)expected_link[548]=0;}}else if(mode==3){expected=flags[g]?0:12;if(flags[g])expected_link[548]=0;}else{expected=flags[g]?0:12;if(flags[g]){store(ed+8,0);store(ed+4,0);store(ed,0);}}}
 else if(stream_ok){if(flags[f]){uint32_t second=load(expected_stream+92),first=load(expected_stream+88);store(ed+4,second);store(ed,first);store(ed+8,load(expected_stream+96));}if(mode==3)expected_stream[109]=1;}
 if(mode==1)expected=0;link_calls=stream_calls=0;uint32_t result=mode==0?opencfw_em9305_ll_test_counters_307498(0x1234,(uintptr_t)dst):mode==1?opencfw_em9305_ll_test_30c2bc(0x1234,(uintptr_t)dst):mode==2?opencfw_em9305_ll_test_30c2d4(0x1234,values[v]):opencfw_em9305_ll_test_30c2d8(0x1234,(uintptr_t)dst);
 assert(result==expected&&link_calls==1&&stream_calls==!link_ok);assert(memcmp(link,expected_link,656)==0&&memcmp(stream,expected_stream,256)==0&&memcmp(output,expected_output,12)==0);count++;
}}}}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('test-counters-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual seven connected C bodies with controlled selected lookup children; native-derived ordered buffer effects, link/stream precedence, nonboolean flag values, output aliases and complete record comparison. Not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
