from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native327718..32780c'):s.index('/* Native30c3a4..30c40c')];b=b.replace('*(volatile uint32_t *)(stream+4u)','g_parent').replace('*(volatile uint8_t *)(uintptr_t)0x805a9cu','g_mode').replace('*(volatile uint32_t *)(uintptr_t)0x8028c0u','g_callback')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t stream[256],parent[512];static uintptr_t g_parent,g_callback;static uint8_t g_mode;static unsigned phase,called;
uint32_t opencfw_em9305_radio_access_mix_3188b8(uint32_t a,uint32_t i){assert(phase++==0&&a==0xdeadbeef&&i==7&&stream[176]==12+(parent[3]==1));return a^i;}
uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t p){assert(phase++==1&&p==(uintptr_t)(stream+120)&&*(uint32_t *)p==17&&*(uint32_t *)(p+4)==19&&stream[166]==1);stream[1]=9;return 0;}
void *opencfw_em9305_memcpy(void *o,const void *i,uint32_t n){if(n==8){assert(phase++==2&&o==stream+212&&i==parent+485&&*(uint32_t *)(stream+220)==0x02010101);}else{assert(phase++==3&&n==16&&o==stream+196&&i==parent+92);}return memcpy(o,i,n);}
static uintptr_t cb(uintptr_t p,uint32_t id,uint32_t flag){assert(phase==4&&p==(uintptr_t)(stream+196)&&id==81&&flag==1&&*(uint16_t *)(stream+236)==513);called++;return 71;}
'''+b+r'''
int main(void){unsigned cases=0;g_parent=(uintptr_t)parent;for(unsigned secure=0;secure<256;secure++)for(unsigned mode=0;mode<3;mode++)for(unsigned call=0;call<2;call++){memset(stream,0xcc,256);memset(parent,0xa5,512);parent[3]=mode;parent[484]=secure;stream[1]=7;stream[2]=81;g_mode=33;g_callback=call?(uintptr_t)cb:0;for(unsigned i=0;i<16;i++)parent[92+i]=i+9;for(unsigned i=0;i<8;i++)parent[485+i]=i+3;phase=called=0;uintptr_t r=opencfw_em9305_radio_stream_setup_327718((uintptr_t)stream,0xdeadbeef,0x1234,17,19,0x102);uint32_t mixed=0xdeadbeef^7;assert(*(uint16_t *)(stream+168)==(uint16_t)(mixed^(mixed>>16))&&*(uint32_t *)(stream+180)==mixed&&*(uint32_t *)(stream+184)==0x123409);assert(stream[188]==2&&stream[189]==2&&stream[178]==33&&*(uint16_t *)(stream+190)==0);if(secure){assert(phase==4&&called==call&&!memcmp(stream+196,parent+92,16));assert(r==(call?71:513));for(unsigned i=0;i<4;i++)assert(stream[212+i]==(uint8_t)((i+3)^(mixed>>(8*i))));}else assert(phase==2&&!called&&r==0x123409);cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('stream-setup-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C secure byte all256, parent modes0/1/2, callback presence, fresh streamid after child, fields/copy order. Parent/global/callback pointers and children normalized for host. No native ISA/crypto/layout/hardware proof.'},indent=2)+'\n');print('PASS',n)
